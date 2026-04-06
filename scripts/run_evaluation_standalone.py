import json
import time
import uuid
from pathlib import Path

from app.agent.orchestrator import chat_with_agent
from app.agent.memory import InMemorySessionStore
from app.core.utils import normalize_text
from app.db.seed import seed

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_PATH = BASE_DIR / "evaluation" / "test_cases.json"
RESULTS_DIR = BASE_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTATION_ALIASES = {
    "shipped": ["shipped", "đã giao", "được giao", "giao thành công", "đang vận chuyển", "đã giao vận chuyển"],
    "processing": ["processing", "đang xử lý", "được xử lý", "đang được xử lý", "xử lý"],
    "cancelled": ["cancelled", "đã hủy", "bị hủy", "hủy thành công", "đã được hủy"],
    "delivered": ["delivered", "đã giao thành công", "đã nhận hàng", "đã giao tới", "giao thành công"],
    "pending": ["pending", "chờ xác nhận", "đang chờ", "chưa xác nhận", "chờ duyệt", "chờ thanh toán"],
    "36 tháng": ["36 tháng", "36 thang", "3 năm", "ba năm"],
    "24 tháng": ["24 tháng", "24 thang", "2 năm", "hai năm"],
    "12 tháng": ["12 tháng", "12 thang", "1 năm", "mot nam", "một năm"],
    "60 tháng": ["60 tháng", "60 thang", "5 năm", "nam nam", "năm năm"],
    "3 đến 7 ngày": ["3 đến 7 ngày", "3-7 ngày", "3 tới 7 ngày", "3 den 7 ngay", "3 đến 7 ngày làm việc"],
    "tốc độ": ["tốc độ", "nhanh", "nhanh hơn", "truy xuất nhanh", "nhanh hon", "tốc độ đọc"],
    "đổi trả": ["đổi trả", "doi tra", "đổi hàng", "trả hàng", "hoàn hàng"],
    "không khớp": ["không khớp", "khong khop", "không đúng", "không trùng", "xác thực thất bại", "email không hợp lệ", "không match"],
    "hoàn tiền": ["hoàn tiền", "hoan tien", "trả tiền", "refund", "hoàn lại tiền", "tiền hoàn"],
    "giao hàng": ["giao hàng", "giao hang", "vận chuyển", "ship hàng", "delivery"],
    "xử lý": ["xử lý", "xu ly", "processing", "đang xử lý", "đang được xử lý"],
    "đang xử lý": ["đang xử lý", "đang được xử lý", "processing", "xử lý"],
    "lắp ráp": ["lắp ráp", "lap rap", "ráp máy", "build pc", "build máy"],
    "vệ sinh": ["vệ sinh", "ve sinh", "làm sạch", "lau chùi"],
    "socket": ["socket", "đế cắm", "chân cắm"],
    "mainboard": ["mainboard", "bo mạch chủ", "bo mạch", "main"],
    "nguồn": ["nguồn", "nguon", "psu", "power supply"],
    "xác nhận": ["xác nhận", "xac nhan", "confirm"],
}


# Pre-build normalized alias lookup (key: normalized expected -> list of normalized aliases)
_NORM_ALIASES: dict[str, list[str]] = {}
for _key, _vals in EXPECTATION_ALIASES.items():
    _nk = normalize_text(_key)
    _nv = [normalize_text(v) for v in _vals]
    if _nk in _NORM_ALIASES:
        _NORM_ALIASES[_nk] = list(dict.fromkeys(_NORM_ALIASES[_nk] + _nv))
    else:
        _NORM_ALIASES[_nk] = list(dict.fromkeys(_nv))


def semantic_match(answer: str, expected: str) -> bool:
    answer_norm = normalize_text(answer)
    expected_norm = normalize_text(expected)

    if expected_norm in answer_norm:
        return True

    aliases = _NORM_ALIASES.get(expected_norm, [])
    for alias in aliases:
        if alias in answer_norm:
            return True

    return False


def check_keywords(answer: str, must_include: list[str], must_not_include: list[str]):
    answer_norm = normalize_text(answer)

    missing = []
    unexpected = []

    for item in must_include:
        if not semantic_match(answer, item):
            missing.append(item)

    for item in must_not_include:
        if normalize_text(item) in answer_norm:
            unexpected.append(item)

    passed = len(missing) == 0 and len(unexpected) == 0
    return passed, missing, unexpected


def load_test_cases():
    try:
        return json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"File JSON invalid: {TEST_CASES_PATH}\nError: {e}")


def main():
    print("=" * 70)
    print("EVALUATION WITH 100 TEST CASES (40 RAG + 35 TOOL + 25 MULTI-TURN)")
    print("=" * 70)

    # Seed database
    print("\n[1/3] Reseeding database...")
    seed()

    # Load test cases
    print("[2/3] Loading 100 test cases...")
    cases = load_test_cases()
    print(f"  Loaded {len(cases)} test cases")

    # Run evaluation
    print("[3/3] Running evaluation (this may take 5-10 minutes)...\n")

    run_id = uuid.uuid4().hex[:8]
    all_results = []
    stats = {
        "total_cases": len(cases),
        "total_turns": 0,
        "passed_turns": 0,
        "failed_turns": 0,
        "latencies": [],
        "by_type": {}
    }

    memory_store = InMemorySessionStore()

    for case_idx, case in enumerate(cases, start=1):
        case_id = case["id"]
        case_type = case["type"]
        thread_id = f"{case['thread_id']}-{run_id}"
        turns = case["turns"]

        if case_type not in stats["by_type"]:
            stats["by_type"][case_type] = {
                "turns": 0,
                "passed": 0,
                "failed": 0,
                "latencies": []
            }

        case_result = {
            "id": case_id,
            "type": case_type,
            "thread_id": thread_id,
            "turns": []
        }

        # Initialize session memory
        history = memory_store.histories.get(thread_id, [])
        context_state = memory_store.contexts.get(thread_id, {})

        for turn_idx, turn in enumerate(turns, start=1):
            start_time = time.perf_counter()

            try:
                result = chat_with_agent(
                    turn["input"],
                    history=history,
                    context_state=context_state,
                    thread_id=thread_id
                )
                answer = result.get("answer", "")
                history = result.get("history", [])
                context_state = result.get("context_state", {})
                latency = time.perf_counter() - start_time
                http_ok = True
                error = ""
            except Exception as e:
                answer = ""
                latency = time.perf_counter() - start_time
                http_ok = False
                error = str(e)

            # Update memory store
            memory_store.histories[thread_id] = history
            memory_store.contexts[thread_id] = context_state

            # Check keywords
            passed = False
            missing = []
            unexpected = []

            if http_ok:
                passed, missing, unexpected = check_keywords(
                    answer,
                    turn.get("must_include", []),
                    turn.get("must_not_include", [])
                )

            turn_result = {
                "turn_index": turn_idx,
                "input": turn["input"],
                "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                "latency_sec": round(latency, 3),
                "http_ok": http_ok,
                "passed": passed,
                "missing_keywords": missing,
                "unexpected_keywords": unexpected,
                "error": error
            }

            case_result["turns"].append(turn_result)

            stats["total_turns"] += 1
            stats["latencies"].append(latency)
            stats["by_type"][case_type]["turns"] += 1
            stats["by_type"][case_type]["latencies"].append(latency)

            if passed:
                stats["passed_turns"] += 1
                stats["by_type"][case_type]["passed"] += 1
            else:
                stats["failed_turns"] += 1
                stats["by_type"][case_type]["failed"] += 1

        all_results.append(case_result)

        # Progress
        if case_idx % 10 == 0:
            print(f"  Progress: {case_idx}/{len(cases)} cases completed")

    # Calculate summary
    avg_latency = round(sum(stats["latencies"]) / len(stats["latencies"]), 3) if stats["latencies"] else 0.0
    overall_accuracy = round(stats["passed_turns"] / stats["total_turns"] * 100, 2) if stats["total_turns"] else 0.0

    summary = {
        "run_id": run_id,
        "database_reseeded": True,
        "total_cases": stats["total_cases"],
        "total_turns": stats["total_turns"],
        "passed_turns": stats["passed_turns"],
        "failed_turns": stats["failed_turns"],
        "overall_accuracy_percent": overall_accuracy,
        "avg_latency_sec": avg_latency,
        "by_type": {}
    }

    for case_type, data in stats["by_type"].items():
        type_avg_latency = round(sum(data["latencies"]) / len(data["latencies"]), 3) if data["latencies"] else 0.0
        type_accuracy = round(data["passed"] / data["turns"] * 100, 2) if data["turns"] else 0.0

        summary["by_type"][case_type] = {
            "turns": data["turns"],
            "passed": data["passed"],
            "failed": data["failed"],
            "accuracy_percent": type_accuracy,
            "avg_latency_sec": type_avg_latency
        }

    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_path = RESULTS_DIR / f"evaluation_result_{timestamp}.json"
    summary_path = RESULTS_DIR / f"evaluation_summary_{timestamp}.json"

    result_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Print summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nFull results saved to: {result_path}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
