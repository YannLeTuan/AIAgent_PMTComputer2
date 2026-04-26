import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes_chat import router as chat_router
from app.channels.facebook_bot import router as facebook_router

MAX_REQUESTS_PER_MINUTE = 20

_request_counts: dict[str, list[float]] = defaultdict(list)

app = FastAPI(title="PMT Computer AI Agent API")


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/chat" and request.method == "POST":
        client_ip = request.client.host if request.client else "unknown"
        if client_ip in ("127.0.0.1", "::1"):
            return await call_next(request)
        now = time.time()
        window = 60.0

        _request_counts[client_ip] = [
            ts for ts in _request_counts[client_ip] if now - ts < window
        ]

        if len(_request_counts[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"detail": "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút."}
            )

        _request_counts[client_ip].append(now)

    return await call_next(request)


app.include_router(chat_router)
app.include_router(facebook_router)


@app.get("/")
def root():
    return {
        "message": "PMT Computer AI Agent API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    from app.agent.memory import session_store
    return {
        "status": "ok",
        "active_sessions": session_store.active_session_count()
    }
