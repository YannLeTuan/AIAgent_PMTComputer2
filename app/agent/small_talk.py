def normalize_simple(text: str):
    return (text or "").strip().lower()


def get_small_talk_answer(user_message: str):
    msg = normalize_simple(user_message)

    business_keywords = ["đơn", "ord", "sản phẩm", "bảo hành", "đổi trả", "kiểm tra",
                         "tìm", "hủy", "email", "khách", "giá", "mua", "build", "tư vấn",
                         "thông số", "tương thích", "cấu hình", "specs", "socket", "tdp"]
    if any(kw in msg for kw in business_keywords):
        return None

    if "cảm ơn" in msg or "cam on" in msg:
        return "Không có gì ạ. Nếu bạn cần tra cứu đơn hàng, sản phẩm, bảo hành hoặc chính sách của PMT Computer thì cứ nhắn tôi nhé."

    if msg in ["chào", "xin chào", "hello", "hi"]:
        return "Xin chào, tôi là trợ lý của PMT Computer. Tôi có thể hỗ trợ về sản phẩm, đơn hàng, bảo hành, đổi trả và thông tin cửa hàng."

    if "tạm biệt" in msg or "bye" in msg:
        return "Cảm ơn bạn đã liên hệ PMT Computer. Khi cần hỗ trợ thêm, bạn cứ nhắn lại nhé."

    return None
