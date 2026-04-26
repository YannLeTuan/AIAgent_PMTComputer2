import re

from app.agent.memory import DEFAULT_CONTEXT

MAX_HISTORY_TURNS = 10
SUMMARY_THRESHOLD = 8

ORDER_PATTERN = re.compile(r"\bORD\d+\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def _extract_key_facts(turns: list) -> str:
    order_codes = set()
    emails = set()
    key_info = []

    for turn in turns:
        text = turn.get("text", "")
        role = turn.get("role", "")

        codes = ORDER_PATTERN.findall(text)
        order_codes.update(c.upper() for c in codes)

        found_emails = EMAIL_PATTERN.findall(text)
        emails.update(found_emails)

        if role == "model":
            for keyword in ["bảo hành", "đã hủy", "đã giao", "đang xử lý", "đang vận chuyển"]:
                if keyword in text.lower():
                    for line in text.split("\n"):
                        line = line.strip()
                        if keyword in line.lower() and len(line) < 120:
                            key_info.append(line)
                            break
                    break

    parts: list[str] = []
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

    excess = len(history) - SUMMARY_THRESHOLD
    trimmed_turns = history[:excess]
    kept_turns = history[excess:]

    summary = _extract_key_facts(trimmed_turns)

    if summary and context_state is not None:
        context_state["context_summary"] = summary

    if summary:
        summary_msg = {"role": "user", "text": f"[Tóm tắt ngữ cảnh trước đó: {summary}]"}
        return [summary_msg] + kept_turns

    return kept_turns


def copy_context(context_state: dict | None):
    import copy
    base = copy.deepcopy(DEFAULT_CONTEXT)

    if not context_state:
        return base

    for k in base:
        if k in context_state:
            base[k] = copy.deepcopy(context_state[k])

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

    elif tool_name == "cancel_multiple_orders" and tool_result.get("success"):
        codes = args.get("order_codes", [])
        if codes:
            context_state["last_order_code"] = codes[-1]
            context_state["last_order_codes"] = list(codes)

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

    elif tool_name == "get_product_details" and tool_result.get("success"):
        context_state["last_product_name"] = tool_result.get("name")
