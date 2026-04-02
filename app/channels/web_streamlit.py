import uuid

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

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

    try:
        response = requests.post(
            API_URL,
            json={
                "thread_id": st.session_state.thread_id,
                "message": user_input
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["answer"]
        else:
            answer = f"Lỗi backend: {response.status_code}"

    except Exception as e:
        answer = f"Không gọi được backend: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)