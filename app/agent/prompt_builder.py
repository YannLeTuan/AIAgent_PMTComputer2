import re

from app.core.config import settings
from app.rag.retriever import retrieve_context

_ORD_RE = re.compile(r"\bORD\d+\b", re.IGNORECASE)
_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def _is_direct_cancel_request(msg: str) -> bool:
    return bool(_ORD_RE.search(msg) and _EMAIL_RE.search(msg))

FOLLOW_ORDER_WORDS = [
    "đơn này", "đơn đó", "đơn kia", "mã đó", "trong các đơn đó", "đơn hàng này",
    "nhận được hàng", "nhận hàng", "bao giờ giao", "giao bao giờ",
    "khi nào giao", "khi nào nhận", "bao giờ tới",
]

FOLLOW_PRODUCT_WORDS = [
    "sản phẩm này", "con này", "mẫu này", "cái này", "loại này"
]

FOLLOW_CUSTOMER_WORDS = [
    "khách này", "người này", "email đó", "khách đó"
]

FOLLOW_MULTI_ORDER_PATTERN = re.compile(
    r"(trong các đơn|các đơn|những đơn|\d+\s*đơn|hai đơn|nhiều đơn)", re.IGNORECASE
)


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

    if FOLLOW_MULTI_ORDER_PATTERN.search(lower) and context_state.get("last_order_codes"):
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

    if context_state.get("context_summary"):
        hints.append(f"Thông tin từ đầu hội thoại: {context_state['context_summary']}")

    return "\n".join(hints).strip()


def build_retrieval_query(user_message: str, context_state: dict):
    parts = [user_message]

    if needs_follow_order_hint(user_message) and context_state.get("last_order_code"):
        parts.append(f"đơn hàng {context_state['last_order_code']}")

    if needs_follow_product_hint(user_message) and context_state.get("last_product_name"):
        parts.append(context_state["last_product_name"])

    return " | ".join(parts)


def build_user_message(user_message: str, context_state: dict):
    skip_rag = _is_direct_cancel_request(user_message)
    retrieval_query = build_retrieval_query(user_message, context_state)

    if skip_rag:
        contexts = []
        context_block = "Không áp dụng RAG cho yêu cầu này."
    else:
        contexts = retrieve_context(retrieval_query, top_k=settings.TOP_K_RETRIEVAL)
        context_block = "\n\n".join(contexts)

    reference_hint = build_reference_hint(user_message, context_state)
    if not reference_hint:
        reference_hint = "Không có tham chiếu hội thoại đặc biệt."

    tool_directive = (
        "- Câu hỏi chứa mã đơn hàng VÀ email → GỌI TOOL cancel_order NGAY, không phân tích chính sách.\n"
        if skip_rag else ""
    )

    return (
        f"Ngữ cảnh tri thức nội bộ:\n{context_block}\n\n"
        f"Ngữ cảnh hội thoại gần đây đã suy ra:\n{reference_hint}\n\n"
        f"Yêu cầu:\n"
        f"{tool_directive}"
        f"- Nếu câu hỏi cần dữ liệu đơn hàng, sản phẩm hoặc khách hàng trong hệ thống, hãy gọi tool phù hợp.\n"
        f"- Nếu câu hỏi là chính sách, thông tin cửa hàng hoặc FAQ, hãy ưu tiên dựa vào ngữ cảnh.\n"
        f"- Nếu là kiến thức máy tính cơ bản, có thể trả lời ngắn gọn và đúng trọng tâm.\n"
        f'- Nếu người dùng đang dùng từ tham chiếu như "đơn này", "con này", "trường hợp đó", hãy tận dụng ngữ cảnh hội thoại đã suy ra.\n'
        f"- Nếu không đủ dữ liệu, hãy nói rõ và hướng người dùng hỏi cụ thể hơn.\n\n"
        f"Câu hỏi người dùng:\n{user_message}"
    ).strip(), retrieval_query, contexts, reference_hint
