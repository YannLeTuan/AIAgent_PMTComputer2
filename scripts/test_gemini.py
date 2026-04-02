from google import genai
from app.core.config import settings


def main():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents="Hãy trả lời ngắn gọn: hệ thống chăm sóc khách hàng tự động là gì?"
    )

    print("=== Gemini Response ===")
    print(response.text)


if __name__ == "__main__":
    main()