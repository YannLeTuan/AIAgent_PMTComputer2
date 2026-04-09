import time

from google import genai
from google.genai import types

from app.agent.context_manager import (
    copy_context, trim_history,
    update_context_from_user_message, update_context_from_tool_result,
)
from app.agent.prompt_builder import build_user_message
from app.agent.small_talk import get_small_talk_answer
from app.agent.tool_runner import run_tool, tool_declarations
from app.core.config import settings
from app.core.logger import write_log
from app.core.prompts import SYSTEM_PROMPT

client = genai.Client(api_key=settings.GEMINI_API_KEY)

GEMINI_MAX_RETRIES = 2
MIN_MEANINGFUL_RESPONSE_LEN = 8


def normalize_answer(text: str):
    if not text:
        return "Hiện tôi chưa thể trả lời rõ câu hỏi này. Bạn có thể cung cấp chi tiết hơn hoặc hỏi theo mã đơn hàng, email khách hàng, tên sản phẩm hoặc chính sách cụ thể."

    text = text.strip()

    if len(text) < MIN_MEANINGFUL_RESPONSE_LEN:
        return "Hiện tôi chưa có đủ thông tin để trả lời chính xác. Bạn có thể hỏi rõ hơn về đơn hàng, sản phẩm, bảo hành, đổi trả hoặc thông tin của PMT Computer."

    return text


def history_to_contents(history: list):
    contents = []

    for item in history:
        role = item.get("role")
        text = item.get("text", "").strip()

        if not text:
            continue

        if role == "user":
            contents.append(
                types.Content(role="user", parts=[types.Part(text=text)])
            )
        else:
            contents.append(
                types.Content(role="model", parts=[types.Part(text=text)])
            )

    return contents


def _call_gemini(contents: list, temperature: float = 0.2):
    last_error = None
    for attempt in range(GEMINI_MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[types.Tool(function_declarations=tool_declarations)],
                    temperature=temperature
                )
            )
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "429" in err_str or "503" in err_str or "500" in err_str:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise last_error


def chat_with_agent(user_message: str, history: list | None = None, context_state: dict | None = None, thread_id: str | None = None):
    start_time = time.perf_counter()
    small_talk_answer = get_small_talk_answer(user_message)
    if small_talk_answer:
        write_log("chat_response", {
            "thread_id": thread_id,
            "user_message": user_message,
            "answer": small_talk_answer,
            "tool_called": False,
            "latency_sec": round(time.perf_counter() - start_time, 3),
            "small_talk_bypass": True
        })

        context_state = copy_context(context_state)
        history = trim_history(history or [], context_state)
        new_history = history + [
            {"role": "user", "text": user_message},
            {"role": "model", "text": small_talk_answer}
        ]

        return {
            "answer": small_talk_answer,
            "history": trim_history(new_history, context_state),
            "context_state": context_state
        }

    context_state = copy_context(context_state)
    history = trim_history(history or [], context_state)

    update_context_from_user_message(user_message, context_state)

    full_message, retrieval_query, contexts, reference_hint = build_user_message(user_message, context_state)

    write_log("chat_request", {
        "thread_id": thread_id,
        "user_message": user_message,
        "retrieval_query": retrieval_query,
        "reference_hint": reference_hint,
        "history_size": len(history),
        "retrieved_context_count": len(contexts),
    })

    contents = history_to_contents(history) + [
        types.Content(role="user", parts=[types.Part(text=full_message)])
    ]

    try:
        response = _call_gemini(contents)

        candidates = response.candidates or []
        if not candidates:
            fallback = normalize_answer("")
            return {
                "answer": fallback,
                "history": history + [
                    {"role": "user", "text": user_message},
                    {"role": "model", "text": fallback}
                ],
                "context_state": context_state
            }

        candidate = candidates[0]
        parts = candidate.content.parts

        function_calls = []
        for part in parts:
            if getattr(part, "function_call", None):
                function_calls.append(part.function_call)

        if not function_calls:
            final_text = normalize_answer(response.text)
            new_history = history + [
                {"role": "user", "text": user_message},
                {"role": "model", "text": final_text}
            ]

            write_log("chat_response", {
                "thread_id": thread_id,
                "user_message": user_message,
                "answer": final_text,
                "tool_called": False,
                "latency_sec": round(time.perf_counter() - start_time, 3)
            })

            return {
                "answer": final_text,
                "history": trim_history(new_history, context_state),
                "context_state": context_state
            }

        current_turn_contents = contents + [candidate.content]

        for fc in function_calls:
            args = dict(fc.args)

            write_log("tool_call", {
                "thread_id": thread_id,
                "tool_name": fc.name,
                "tool_args": args
            })

            tool_result = run_tool(fc.name, args)

            write_log("tool_result", {
                "thread_id": thread_id,
                "tool_name": fc.name,
                "tool_result": tool_result
            })

            update_context_from_tool_result(fc.name, tool_result, args, context_state)

            current_turn_contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=fc.name,
                            response={"result": tool_result}
                        )
                    ]
                )
            )

        final_response = _call_gemini(current_turn_contents)

        final_text = normalize_answer(final_response.text)

        new_history = history + [
            {"role": "user", "text": user_message},
            {"role": "model", "text": final_text}
        ]

        write_log("chat_response", {
            "thread_id": thread_id,
            "user_message": user_message,
            "answer": final_text,
            "tool_called": True,
            "latency_sec": round(time.perf_counter() - start_time, 3),
        })

        return {
            "answer": final_text,
            "history": trim_history(new_history, context_state),
            "context_state": context_state
        }

    except Exception as e:
        write_log("chat_error", {
            "thread_id": thread_id,
            "user_message": user_message,
            "error": str(e),
            "latency_sec": round(time.perf_counter() - start_time, 3)
        })
        raise
