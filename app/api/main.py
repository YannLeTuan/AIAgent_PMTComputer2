from fastapi import FastAPI

from app.api.routes_chat import router as chat_router

app = FastAPI(title="PMT Computer AI Agent API")

app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "PMT Computer AI Agent API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health():
    return {"status": "ok"}