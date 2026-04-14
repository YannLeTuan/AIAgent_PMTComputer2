import json
import uuid

import requests
import streamlit as st

STREAM_URL = "http://127.0.0.1:8000/chat/stream"

st.set_page_config(page_title="PMT Computer Chatbot", page_icon="💻")
st.title("PMT Computer Chatbot")
st.caption("Hỗ trợ sản phẩm, đơn hàng, bảo hành, đổi trả và chính sách của cửa hàng")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Nhập câu hỏi của bạn...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        def _stream_response():
            try:
                with requests.post(
                    STREAM_URL,
                    json={"thread_id": st.session_state.thread_id, "message": user_input},
                    stream=True,
                    timeout=60,
                ) as resp:
                    if resp.status_code != 200:
                        yield f"Lỗi backend: {resp.status_code}"
                        return
                    for raw_line in resp.iter_lines():
                        if not raw_line:
                            continue
                        line = raw_line.decode("utf-8")
                        if not line.startswith("data: "):
                            continue
                        data = line[6:]
                        if data in ("[DONE]", "[ERROR]") or data.startswith("[ERROR]"):
                            return
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            yield data
            except Exception as e:
                yield f"Không gọi được backend: {e}"

        answer = st.write_stream(_stream_response())

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer or ""
    })