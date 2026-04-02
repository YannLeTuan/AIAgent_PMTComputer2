from fastapi import APIRouter

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    history = session_store.get_history(req.thread_id)
    context_state = session_store.get_context(req.thread_id)

    result = chat_with_agent(
        req.message,
        history,
        context_state,
        thread_id=req.thread_id
    )

    session_store.set_history(req.thread_id, result["history"])
    session_store.set_context(req.thread_id, result["context_state"])

    return ChatResponse(
        thread_id=req.thread_id,
        answer=result["answer"]
    )