import json
import subprocess
import sys
import time
import unicodedata
import uuid
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
API_URL = "http://127.0.0.1:8000/chat"
TEST_CASES_PATH = BASE_DIR / "evaluation" / "test_cases.json"
RESULTS_DIR = BASE_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTATION_ALIASES = {
    "shipped": ["shipped", "đã giao", "được giao", "giao thành công"],
    "processing": ["processing", "đang xử lý", "được xử lý"],
    "cancelled": ["cancelled", "đã hủy", "bị hủy"],
    "delivered": ["delivered", "đã giao thành công", "đã nhận hàng"],
    "tốc độ": ["tốc độ", "nhanh", "nhanh hơn", "truy xuất nhanh"],
    "36 tháng": ["36 tháng", "36 thang"],
    "3 đến 7 ngày": ["3 đến 7 ngày", "3-7 ngày", "3 tới 7 ngày", "3 den 7 ngay"]
}


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text


def semantic_match(answer: str, expected: str) -> bool:
    answer_norm = normalize_text(answer)
    expected_norm = normalize_text(expected)

    if expected_norm in answer_norm:
        return True

    aliases = EXPECTATION_ALIASES.get(expected_norm, [])
    for alias in aliases:
        if normalize_text(alias) in answer_norm:
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


def ensure_test_cases_file_exists():
    if not TEST_CASES_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file test case tại: {TEST_CASES_PATH}\n"
            f"Hãy tạo file này đúng tại thư mục evaluation/test_cases.json"
        )


def load_test_cases():
    ensure_test_cases_file_exists()
    try:
        return json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"File JSON bị lỗi định dạng: {TEST_CASES_PATH}\n"
            f"Chi tiết: {e}"
        )


def reseed_database():
    subprocess.run(
        [sys.executable, "-m", "app.db.seed"],
        cwd=BASE_DIR,
        check=True
    )


def run_turn(thread_id: str, message: str):
    start = time.perf_counter()

    response = requests.post(
        API_URL,
        json={
            "thread_id": thread_id,
            "message": message
        },
        timeout=90
    )

    elapsed = time.perf_counter() - start

    if response.status_code != 200:
        return {
            "ok": False,
            "status_code": response.status_code,
            "answer": "",
            "latency_sec": round(elapsed, 3),
            "error": f"HTTP {response.status_code}"
        }

    data = response.json()

    return {
        "ok": True,
        "status_code": response.status_code,
        "answer": data.get("answer", ""),
        "latency_sec": round(elapsed, 3),
        "error": ""
    }


def main():
    reseed_database()
    cases = load_test_cases()
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

    for case in cases:
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

        for idx, turn in enumerate(turns, start=1):
            result = run_turn(thread_id, turn["input"])

            passed = False
            missing = []
            unexpected = []

            if result["ok"]:
                passed, missing, unexpected = check_keywords(
                    result["answer"],
                    turn.get("must_include", []),
                    turn.get("must_not_include", [])
                )

            turn_result = {
                "turn_index": idx,
                "input": turn["input"],
                "answer": result["answer"],
                "latency_sec": result["latency_sec"],
                "status_code": result["status_code"],
                "http_ok": result["ok"],
                "passed": passed,
                "missing_keywords": missing,
                "unexpected_keywords": unexpected,
                "error": result["error"]
            }

            case_result["turns"].append(turn_result)

            stats["total_turns"] += 1
            stats["latencies"].append(result["latency_sec"])
            stats["by_type"][case_type]["turns"] += 1
            stats["by_type"][case_type]["latencies"].append(result["latency_sec"])

            if passed:
                stats["passed_turns"] += 1
                stats["by_type"][case_type]["passed"] += 1
            else:
                stats["failed_turns"] += 1
                stats["by_type"][case_type]["failed"] += 1

        all_results.append(case_result)

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

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_path = RESULTS_DIR / f"evaluation_result_{timestamp}.json"
    summary_path = RESULTS_DIR / f"evaluation_summary_{timestamp}.json"

    result_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n===== EVALUATION SUMMARY =====")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nChi tiết lưu tại: {result_path}")
    print(f"Tóm tắt lưu tại: {summary_path}")


if __name__ == "__main__":
    main()