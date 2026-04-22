import asyncio
import hashlib
import hmac
import httpx

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent
from app.core.config import settings

router = APIRouter()

GRAPH_API_URL = "https://graph.facebook.com/v19.0/me/messages"


def _verify_signature(body: bytes, signature_header: str) -> bool:
    """Xác minh request thật sự đến từ Meta, không phải giả mạo."""
    if not settings.FACEBOOK_APP_SECRET:
        return True
    if not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.FACEBOOK_APP_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)


async def _send_message(recipient_id: str, text: str) -> None:
    """Gửi tin nhắn về cho user qua Graph API."""
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    headers = {"Content-Type": "application/json"}
    params = {"access_token": settings.FACEBOOK_PAGE_TOKEN}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GRAPH_API_URL,
            json=payload,
            headers=headers,
            params=params,
        )
        resp.raise_for_status()


@router.get("/webhook/facebook", response_class=PlainTextResponse)
async def verify_webhook(request: Request):
    """
    Meta gọi vào đây 1 lần khi mình đăng ký webhook.
    Mình phải trả lại hub.challenge để xác nhận mình là chủ server.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.FACEBOOK_VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    raise HTTPException(status_code=403, detail="Verify token không khớp")


@router.post("/webhook/facebook")
async def receive_message(request: Request):
    """
    Meta gọi vào đây mỗi khi có tin nhắn mới từ user.
    """
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Chữ ký không hợp lệ")

    data = await request.json()

    if data.get("object") != "page":
        return {"status": "ignored"}

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text", "").strip()

            # Bỏ qua echo (tin nhắn do bot tự gửi)
            if message.get("is_echo") or not text or not sender_id:
                continue

            history = session_store.get_history(sender_id)
            context_state = session_store.get_context(sender_id)

            try:
                result = await asyncio.to_thread(
                    chat_with_agent,
                    text,
                    history,
                    context_state,
                    sender_id,
                )
                session_store.set_history(sender_id, result["history"])
                session_store.set_context(sender_id, result["context_state"])
                await _send_message(sender_id, result["answer"])
            except Exception:
                await _send_message(
                    sender_id,
                    "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau.",
                )

    # Meta yêu cầu phải trả 200 OK nhanh, không thì sẽ retry liên tục
    return {"status": "ok"}
