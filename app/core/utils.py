import unicodedata


def normalize_text(text: str) -> str:
    """Chuẩn hóa text: lowercase, bỏ dấu tiếng Việt, strip khoảng trắng."""
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text
