
import re
import time

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logger import write_log
from app.core.prompts import SYSTEM_PROMPT
from app.rag.retriever import retrieve_context
from app.tools.customer_tools import get_customer_orders
from app.tools.order_tools import check_order_status, cancel_order, cancel_multiple_orders
from app.tools.product_tools import search_product, list_products

client = genai.Client(api_key=settings.GEMINI_API_KEY)

MAX_HISTORY_TURNS = 10
SUMMARY_THRESHOLD = 8
GEMINI_MAX_RETRIES = 2

tool_declarations = [
    types.FunctionDeclaration(
        name="check_order_status",
        description="kiểm tra trạng thái đơn hàng theo mã order_code",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_code": {"type": "string"}
            },
            "required": ["order_code"]
        }
    ),
    types.FunctionDeclaration(
        name="cancel_order",
        description="hủy đơn hàng theo mã order_code và lý do reason. Bắt buộc truyền customer_email để xác thực danh tính khách hàng trước khi hủy.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_code": {"type": "string"},
                "reason": {"type": "string"},
                "customer_email": {
                    "type": "string",
                    "description": "email của khách hàng để xác thực danh tính, phải khớp với email đăng ký đơn hàng"
                }
            },
            "required": ["order_code", "reason", "customer_email"]
        }
    ),
    types.FunctionDeclaration(
        name="search_product",
        description="tìm sản phẩm theo từ khóa, có thể tìm theo tên, loại, hãng hoặc sku",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string"}
            },
            "required": ["keyword"]
        }
    ),
    types.FunctionDeclaration(
        name="list_products",
        description="liệt kê danh sách sản phẩm theo nhóm category, hãng brand hoặc giá tối đa max_price",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "brand": {"type": "string"},
                "max_price": {"type": "number"},
                "limit": {"type": "integer"}
            }
        }
    ),
    types.FunctionDeclaration(
        name="cancel_multiple_orders",
        description="hủy nhiều đơn hàng cùng lúc theo danh sách order_codes và lý do reason. Bắt buộc truyền customer_email để xác thực danh tính.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_codes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "reason": {"type": "string"},
                "customer_email": {
                    "type": "string",
                    "description": "email của khách hàng để xác thực danh tính"
                }
            },
            "required": ["order_codes", "reason", "customer_email"]
        }
    ),
    types.FunctionDeclaration(
        name="get_customer_orders",
        description="lấy danh sách đơn hàng của khách hàng theo email",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "customer_email": {"type": "string"}
            },
            "required": ["customer_email"]
        }
    )
]

ORDER_PATTERN = re.compile(r"\bORD\d+\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")

FOLLOW_ORDER_WORDS = [
    "đơn này", "đơn đó", "đơn kia", "mã đó", "trong các đơn đó", "đơn hàng này"
]

FOLLOW_PRODUCT_WORDS = [
    "sản phẩm này", "con này", "mẫu này", "cái này", "loại này"
]

FOLLOW_CUSTOMER_WORDS = [
    "khách này", "người này", "email đó", "khách đó"
]


# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

def run_tool(name: str, args: dict):
    dispatch = {
        "check_order_status": check_order_status,
        "cancel_order": cancel_order,
        "cancel_multiple_orders": cancel_multiple_orders,
        "search_product": search_product,
        "list_products": list_products,
        "get_customer_orders": get_customer_orders,
    }
    fn = dispatch.get(name)
    if fn is None:
        return {"success": False, "message": f"công cụ {name} không tồn tại"}
    return fn(**args)


# ---------------------------------------------------------------------------
# Response normalization
# ---------------------------------------------------------------------------

def normalize_answer(text: str):
    if not text:
        return "Hiện tôi chưa thể trả lời rõ câu hỏi này. Bạn có thể cung cấp chi tiết hơn hoặc hỏi theo mã đơn hàng, email khách hàng, tên sản phẩm hoặc chính sách cụ thể."

    text = text.strip()

    if len(text) < 8:
        return "Hiện tôi chưa có đủ thông tin để trả lời chính xác. Bạn có thể hỏi rõ hơn về đơn hàng, sản phẩm, bảo hành, đổi trả hoặc thông tin của PMT Computer."

    return text


# ---------------------------------------------------------------------------
# History management — smart summarization thay vì hard trim
# ---------------------------------------------------------------------------

def _extract_key_facts(turns: list) -> str:
    """Trích xuất thông tin quan trọng từ các turns bị cắt bỏ."""
    order_codes = set()
    emails = set()
    key_info = []

    for turn in turns:
        text = turn.get("text", "")
        role = turn.get("role", "")

        # Trích xuất mã đơn hàng
        codes = ORDER_PATTERN.findall(text)
        order_codes.update(c.upper() for c in codes)

        # Trích xuất email
        found_emails = EMAIL_PATTERN.findall(text)
        emails.update(found_emails)

        # Trích xuất tên sản phẩm từ câu trả lời bot
        if role == "model":
            for keyword in ["bảo hành", "đã hủy", "đã giao", "đang xử lý", "đang vận chuyển"]:
                if keyword in text.lower():
                    # Lấy 1 dòng ngắn mô tả trạng thái
                    for line in text.split("\n"):
                        line = line.strip()
                        if keyword in line.lower() and len(line) < 120:
                            key_info.append(line)
                            break
                    break

    parts = []
    if order_codes:
        parts.append(f"Các mã đơn hàng đã nhắc tới: {', '.join(sorted(order_codes))}")
    if emails:
        parts.append(f"Email khách hàng: {', '.join(emails)}")
    if key_info:
        parts.append("Thông tin chính: " + "; ".join(key_info[:3]))

    return ". ".join(parts)


def trim_history(history: list, context_state: dict | None = None):
    if len(history) <= MAX_HISTORY_TURNS:
        return history

    # Số turns cần cắt
    excess = len(history) - SUMMARY_THRESHOLD
    trimmed_turns = history[:excess]
    kept_turns = history[excess:]

    # Trích xuất key facts từ turns bị cắt
    summary = _extract_key_facts(trimmed_turns)

    if summary and context_state is not None:
        context_state["context_summary"] = summary

    # Nếu có summary, chèn dưới dạng 1 message hệ thống ở đầu
    if summary:
        summary_msg = {"role": "user", "text": f"[Tóm tắt ngữ cảnh trước đó: {summary}]"}
        return [summary_msg] + kept_turns

    return kept_turns


def history_to_contents(history: list):
    contents = []

    for item in history:
        role = item.get("role")
        text = item.get("text", "").strip()

        if not text:
            continue

        if role == "user":
            contents.append(
                types.Content(role="user", parts=[types.Part(text=text)])
            )
        else:
            contents.append(
                types.Content(role="model", parts=[types.Part(text=text)])
            )

    return contents


# ---------------------------------------------------------------------------
# Context state management
# ---------------------------------------------------------------------------

def copy_context(context_state: dict | None):
    base = {
        "last_order_code": None,
        "last_product_name": None,
        "last_customer_email": None,
        "last_customer_name": None,
        "last_order_codes": [],
        "context_summary": ""
    }

    if not context_state:
        return base

    for k in base:
        if k in context_state:
            base[k] = context_state[k]

    return base


def update_context_from_user_message(user_message: str, context_state: dict):
    order_codes = ORDER_PATTERN.findall(user_message)
    emails = EMAIL_PATTERN.findall(user_message)

    if order_codes:
        context_state["last_order_code"] = order_codes[-1].upper()

    if emails:
        context_state["last_customer_email"] = emails[-1]


def update_context_from_tool_result(tool_name: str, tool_result: dict, args: dict, context_state: dict):
    if tool_name == "check_order_status" and tool_result.get("success"):
        context_state["last_order_code"] = tool_result.get("order_code")
        context_state["last_product_name"] = tool_result.get("product_name")

    elif tool_name == "cancel_order" and tool_result.get("success"):
        context_state["last_order_code"] = args.get("order_code")

    elif tool_name == "search_product" and tool_result.get("success"):
        results = tool_result.get("results", [])
        if results:
            context_state["last_product_name"] = results[0].get("name")

    elif tool_name == "get_customer_orders" and tool_result.get("success"):
        context_state["last_customer_email"] = tool_result.get("customer_email")
        context_state["last_customer_name"] = tool_result.get("customer_name")
        context_state["last_product_name"] = None

        orders = tool_result.get("orders", [])
        order_codes = [x.get("order_code") for x in orders if x.get("order_code")]
        context_state["last_order_codes"] = order_codes

        for item in orders:
            if item.get("status") == "processing":
                context_state["last_order_code"] = item.get("order_code")
                break
        else:
            if order_codes:
                context_state["last_order_code"] = order_codes[0]


# ---------------------------------------------------------------------------
# Reference hint building
# ---------------------------------------------------------------------------

def needs_follow_order_hint(user_message: str):
    lower = user_message.lower()
    return any(x in lower for x in FOLLOW_ORDER_WORDS)


def needs_follow_product_hint(user_message: str):
    lower = user_message.lower()
    return any(x in lower for x in FOLLOW_PRODUCT_WORDS)


def needs_follow_customer_hint(user_message: str):
    lower = user_message.lower()
    return any(x in lower for x in FOLLOW_CUSTOMER_WORDS)


def build_reference_hint(user_message: str, context_state: dict):
    hints = []
    lower = user_message.lower()

    if needs_follow_order_hint(user_message) and context_state.get("last_order_code"):
        hints.append(f"Đơn hàng đang được nhắc tới gần nhất là {context_state['last_order_code']}.")

    if ("trong các đơn đó" in lower or "2 đơn" in lower or "các đơn" in lower or "những đơn" in lower) and context_state.get("last_order_codes"):
        joined = ", ".join(context_state["last_order_codes"])
        hints.append(f"Danh sách đơn hàng gần nhất đang được nhắc tới gồm: {joined}.")
        hints.append("Nếu người dùng đang hỏi ở số nhiều, hãy xem xét toàn bộ danh sách đơn hàng này, không chỉ một đơn duy nhất.")

    if needs_follow_product_hint(user_message) and context_state.get("last_product_name"):
        hints.append(f"Sản phẩm đang được nhắc tới gần nhất là {context_state['last_product_name']}.")

    if needs_follow_customer_hint(user_message):
        if context_state.get("last_customer_email"):
            hints.append(f"Khách hàng đang được nhắc tới gần nhất có email {context_state['last_customer_email']}.")
        if context_state.get("last_customer_name"):
            hints.append(f"Tên khách hàng gần nhất là {context_state['last_customer_name']}.")

    if "vậy" in lower and context_state.get("last_order_code"):
        hints.append(f'Ngữ cảnh gần nhất liên quan tới đơn hàng {context_state["last_order_code"]}.')

    # Thêm context summary từ các turns đã bị trim
    if context_state.get("context_summary"):
        hints.append(f"Thông tin từ đầu hội thoại: {context_state['context_summary']}")

    return "\n".join(hints).strip()


# ---------------------------------------------------------------------------
# RAG retrieval query building — không inject câu trả lời vào query
# ---------------------------------------------------------------------------

def build_retrieval_query(user_message: str, context_state: dict):
    parts = [user_message]

    # Chỉ bổ sung entity tham chiếu, KHÔNG inject nội dung đáp án
    if needs_follow_order_hint(user_message) and context_state.get("last_order_code"):
        parts.append(f"đơn hàng {context_state['last_order_code']}")

    if needs_follow_product_hint(user_message) and context_state.get("last_product_name"):
        parts.append(context_state["last_product_name"])

    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Small talk bypass
# ---------------------------------------------------------------------------

def normalize_simple(text: str):
    return (text or "").strip().lower()


def get_small_talk_answer(user_message: str):
    msg = normalize_simple(user_message)

    # Chỉ match khi message TOÀN BỘ là small talk (ngắn, không chứa keyword nghiệp vụ)
    business_keywords = ["đơn", "ord", "sản phẩm", "bảo hành", "đổi trả", "kiểm tra",
                         "tìm", "hủy", "email", "khách", "giá", "mua", "build", "tư vấn"]
    if any(kw in msg for kw in business_keywords):
        return None

    if "cảm ơn" in msg or "cam on" in msg:
        return "Không có gì ạ. Nếu bạn cần tra cứu đơn hàng, sản phẩm, bảo hành hoặc chính sách của PMT Computer thì cứ nhắn tôi nhé."

    if msg in ["chào", "xin chào", "hello", "hi"]:
        return "Xin chào, tôi là trợ lý của PMT Computer. Tôi có thể hỗ trợ về sản phẩm, đơn hàng, bảo hành, đổi trả và thông tin cửa hàng."

    if "tạm biệt" in msg or "bye" in msg:
        return "Cảm ơn bạn đã liên hệ PMT Computer. Khi cần hỗ trợ thêm, bạn cứ nhắn lại nhé."

    return None


# ---------------------------------------------------------------------------
# Message building
# ---------------------------------------------------------------------------

def build_user_message(user_message: str, context_state: dict):
    retrieval_query = build_retrieval_query(user_message, context_state)
    contexts = retrieve_context(retrieval_query, top_k=settings.TOP_K_RETRIEVAL)
    context_block = "\n\n".join(contexts)

    reference_hint = build_reference_hint(user_message, context_state)
    if not reference_hint:
        reference_hint = "Không có tham chiếu hội thoại đặc biệt."

    return (
        f"Ngữ cảnh tri thức nội bộ:\n{context_block}\n\n"
        f"Ngữ cảnh hội thoại gần đây đã suy ra:\n{reference_hint}\n\n"
        f"Yêu cầu:\n"
        f"- Nếu câu hỏi cần dữ liệu đơn hàng, sản phẩm hoặc khách hàng trong hệ thống, hãy gọi tool phù hợp.\n"
        f"- Nếu câu hỏi là chính sách, thông tin cửa hàng hoặc FAQ, hãy ưu tiên dựa vào ngữ cảnh.\n"
        f"- Nếu là kiến thức máy tính cơ bản, có thể trả lời ngắn gọn và đúng trọng tâm.\n"
        f'- Nếu người dùng đang dùng từ tham chiếu như "đơn này", "con này", "trường hợp đó", hãy tận dụng ngữ cảnh hội thoại đã suy ra.\n'
        f"- Nếu không đủ dữ liệu, hãy nói rõ và hướng người dùng hỏi cụ thể hơn.\n\n"
        f"Câu hỏi người dùng:\n{user_message}"
    ).strip(), retrieval_query, contexts, reference_hint


# ---------------------------------------------------------------------------
# Gemini API call với retry
# ---------------------------------------------------------------------------

def _call_gemini(contents: list, temperature: float = 0.2):
    last_error = None
    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[types.Tool(function_declarations=tool_declarations)],
                    temperature=temperature
                )
            )
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            # Chỉ retry cho lỗi tạm thời
            if "429" in err_str or "503" in err_str or "500" in err_str:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise last_error


# ---------------------------------------------------------------------------
# Main chat entry point
# ---------------------------------------------------------------------------

def chat_with_agent(user_message: str, history: list | None = None, context_state: dict | None = None, thread_id: str | None = None):
    start_time = time.perf_counter()
    small_talk_answer = get_small_talk_answer(user_message)
    if small_talk_answer:
        write_log("chat_response", {
            "thread_id": thread_id,
            "user_message": user_message,
            "answer": small_talk_answer,
            "tool_called": False,
            "latency_sec": round(time.perf_counter() - start_time, 3),
            "small_talk_bypass": True
        })

        context_state = copy_context(context_state)
        history = trim_history(history or [], context_state)
        new_history = history + [
            {"role": "user", "text": user_message},
            {"role": "model", "text": small_talk_answer}
        ]

        return {
            "answer": small_talk_answer,
            "history": trim_history(new_history, context_state),
            "context_state": context_state
        }

    context_state = copy_context(context_state)
    history = trim_history(history or [], context_state)

    update_context_from_user_message(user_message, context_state)

    full_message, retrieval_query, contexts, reference_hint = build_user_message(user_message, context_state)

    write_log("chat_request", {
        "thread_id": thread_id,
        "user_message": user_message,
        "retrieval_query": retrieval_query,
        "reference_hint": reference_hint,
        "history_size": len(history),
        "retrieved_context_count": len(contexts),
        "retrieved_context_preview": contexts[:2]
    })

    contents = history_to_contents(history) + [
        types.Content(role="user", parts=[types.Part(text=full_message)])
    ]

    try:
        response = _call_gemini(contents)

        candidates = response.candidates or []
        if not candidates:
            fallback = normalize_answer("")
            return {
                "answer": fallback,
                "history": history + [
                    {"role": "user", "text": user_message},
                    {"role": "model", "text": fallback}
                ],
                "context_state": context_state
            }

        candidate = candidates[0]
        parts = candidate.content.parts

        function_calls = []
        for part in parts:
            if getattr(part, "function_call", None):
                function_calls.append(part.function_call)

        if not function_calls:
            final_text = normalize_answer(response.text)
            new_history = history + [
                {"role": "user", "text": user_message},
                {"role": "model", "text": final_text}
            ]

            write_log("chat_response", {
                "thread_id": thread_id,
                "user_message": user_message,
                "answer": final_text,
                "tool_called": False,
                "latency_sec": round(time.perf_counter() - start_time, 3)
            })

            return {
                "answer": final_text,
                "history": trim_history(new_history, context_state),
                "context_state": context_state
            }

        current_turn_contents = contents + [candidate.content]

        for fc in function_calls:
            args = dict(fc.args)

            write_log("tool_call", {
                "thread_id": thread_id,
                "tool_name": fc.name,
                "tool_args": args
            })

            tool_result = run_tool(fc.name, args)

            write_log("tool_result", {
                "thread_id": thread_id,
                "tool_name": fc.name,
                "tool_result": tool_result
            })

            update_context_from_tool_result(fc.name, tool_result, args, context_state)

            current_turn_contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"result": tool_result}
                        )
                    ]
                )
            )

        final_response = _call_gemini(current_turn_contents)

        final_text = normalize_answer(final_response.text)

        new_history = history + [
            {"role": "user", "text": user_message},
            {"role": "model", "text": final_text}
        ]

        write_log("chat_response", {
            "thread_id": thread_id,
            "user_message": user_message,
            "answer": final_text,
            "tool_called": True,
            "latency_sec": round(time.perf_counter() - start_time, 3),
            "context_state": context_state
        })

        return {
            "answer": final_text,
            "history": trim_history(new_history, context_state),
            "context_state": context_state
        }

    except Exception as e:
        write_log("chat_error", {
            "thread_id": thread_id,
            "user_message": user_message,
            "error": str(e),
            "latency_sec": round(time.perf_counter() - start_time, 3)
        })
        raise
