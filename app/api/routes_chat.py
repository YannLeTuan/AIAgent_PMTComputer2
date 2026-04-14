import asyncio
import json
import threading

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent, stream_chat_with_agent
from app.api.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    history = session_store.get_history(req.thread_id)
    context_state = session_store.get_context(req.thread_id)

    result = await asyncio.to_thread(
        chat_with_agent,
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


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    history = session_store.get_history(req.thread_id)
    context_state = session_store.get_context(req.thread_id)

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def _run():
        try:
            for item in stream_chat_with_agent(req.message, history, context_state, req.thread_id):
                asyncio.run_coroutine_threadsafe(queue.put(item), loop).result()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(queue.put({"__error__": str(e)}), loop).result()
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop).result()

    threading.Thread(target=_run, daemon=True).start()

    async def event_generator():
        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, dict):
                if "__error__" in item:
                    yield f"data: [ERROR] {item['__error__']}\n\n"
                    break
                session_store.set_history(req.thread_id, item["history"])
                session_store.set_context(req.thread_id, item["context_state"])
                yield "data: [DONE]\n\n"
            else:
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
