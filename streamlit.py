import os
import uuid
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="PMT Computer AI Agent",
    page_icon="💻",
    layout="wide"
)


def load_cloud_secrets_to_env():
    keys = [
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "TOP_K_RETRIEVAL"
    ]
    for key in keys:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])


load_cloud_secrets_to_env()

from app.agent.memory import session_store
from app.agent.orchestrator import chat_with_agent
from app.db.seed import seed
from app.rag.ingest import ingest_folder


@st.cache_resource(show_spinner=False)
def init_demo_resources():
    db_file = Path("ecommerce.db")
    vector_file = Path("data/vector_index/faiss_index.faiss")
    vector_meta = Path("data/vector_index/faiss_index.pkl")

    if not db_file.exists():
        seed()

    if not vector_file.exists() or not vector_meta.exists():
        ingest_folder("data/raw")

    return True


def reset_demo_state():
    seed()
    ingest_folder("data/raw")
    if "thread_id" in st.session_state:
        session_store.clear_session(st.session_state.thread_id)
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())


init_demo_resources()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title("PMT Computer")
    st.caption("AI Agent demo cho đồ án tốt nghiệp")

    st.markdown(
        """
**Chức năng chính**
- Tư vấn linh kiện máy tính
- Kiểm tra đơn hàng
- Chính sách bảo hành / đổi trả
- Hỗ trợ sản phẩm theo hãng / nhóm
- Ghi nhớ hội thoại ngắn
- RAG + Tool Calling + Memory
"""
    )

    st.markdown("---")
    st.markdown("**Gợi ý câu hỏi**")
    st.markdown(
        """
- CPU bảo hành bao lâu?
- Tìm SSD Samsung
- Ổ cứng khác SSD thế nào?
- Kiểm tra đơn hàng ORD003
- Khách phamminhtuan.pmt@gmail.com đã đặt gì?
- Trong các đơn đó, đơn nào đang xử lý?
- Tôi muốn build máy chơi game
"""
    )

    st.markdown("---")
    if st.button("Reset dữ liệu demo", use_container_width=True):
        reset_demo_state()
        st.rerun()

    if st.button("Xóa hội thoại hiện tại", use_container_width=True):
        session_store.clear_session(st.session_state.thread_id)
        st.session_state.messages = []
        st.rerun()

st.title("💻 PMT Computer AI Agent")
st.caption("Hệ thống AI Agent đa kênh ứng dụng RAG cho chăm sóc khách hàng cửa hàng máy tính")

col1, col2 = st.columns([2, 1])

with col2:
    st.info(
        """
**Thông tin demo**
- Nền tảng: Streamlit Community Cloud
- Mô hình: Gemini
- Tri thức: RAG từ tài liệu nội bộ
- Nghiệp vụ: SQLite + tool calling
- Memory: hội thoại nhiều lượt
"""
    )

with col1:
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
            with st.spinner("PMT Computer đang xử lý..."):
                history = session_store.get_history(st.session_state.thread_id)
                context_state = session_store.get_context(st.session_state.thread_id)

                result = chat_with_agent(
                    user_input,
                    history,
                    context_state,
                    thread_id=st.session_state.thread_id
                )

                session_store.set_history(st.session_state.thread_id, result["history"])
                session_store.set_context(st.session_state.thread_id, result["context_state"])

                answer = result["answer"]
                st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })