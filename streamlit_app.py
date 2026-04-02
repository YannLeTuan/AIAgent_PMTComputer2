import os
import uuid
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="PMT Computer AI Agent",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
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


st.markdown("""
<style>
    .main > div {
        padding-top: 1.2rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        background: #f6f8fb;
        border-right: 1px solid rgba(0,0,0,0.06);
    }

    .pmt-hero {
        padding: 0.8rem 0 1.2rem 0;
    }

    .pmt-title {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
        color: #1f2f46;
    }

    .pmt-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.35rem;
    }

    .pmt-badge-row {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 1rem;
        margin-bottom: 1.2rem;
    }

    .pmt-badge {
        background: #eef4ff;
        color: #2b5fb8;
        border: 1px solid #d9e6ff;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 600;
    }

    .pmt-chat-wrap {
        background: white;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 1rem 1rem 0.3rem 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }

    .pmt-note {
        font-size: 0.92rem;
        color: #6b7280;
        background: #fafbfc;
        border: 1px solid rgba(0,0,0,0.05);
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
    }

    .stChatMessage {
        border-radius: 16px;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.65rem 0.8rem;
        font-weight: 600;
    }

    .sidebar-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1f2f46;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .sidebar-muted {
        color: #6b7280;
        font-size: 0.92rem;
    }

    .sidebar-card {
        background: white;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-list {
        padding-left: 1rem;
        margin: 0.4rem 0 0 0;
    }

    .sidebar-list li {
        margin-bottom: 0.45rem;
    }

    .footer-note {
        margin-top: 1rem;
        color: #8b95a7;
        font-size: 0.82rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


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
    st.markdown("## PMT Computer")
    st.markdown('<div class="sidebar-muted">Nhân viên chăm sóc khách hàng AI, hỗ trợ cho cửa hàng Phạm Minh Tuấn Computer</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Chức năng chính</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="sidebar-card">
<ul class="sidebar-list">
    <li>Tư vấn linh kiện máy tính</li>
    <li>Kiểm tra đơn hàng</li>
    <li>Chính sách bảo hành / đổi trả</li>
    <li>Hỗ trợ sản phẩm theo hãng / nhóm</li>
    <li>Ghi nhớ hội thoại ngắn</li>
    <li>RAG + Tool Calling + Memory</li>
</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Gợi ý câu hỏi</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="sidebar-card">
<ul class="sidebar-list">
    <li>CPU bảo hành bao lâu?</li>
    <li>Tìm SSD Samsung</li>
    <li>Ổ cứng khác SSD thế nào?</li>
    <li>Kiểm tra đơn hàng ORD003</li>
    <li>Khách Phạm Minh Tuấn đã đặt gì?</li>
    <li>Trong các đơn đó, đơn nào đang xử lý?</li>
    <li>Tôi muốn build máy chơi game</li>
</ul>
</div>
""", unsafe_allow_html=True)

    if st.button("Reset dữ liệu demo"):
        reset_demo_state()
        st.rerun()

    if st.button("Xóa hội thoại hiện tại"):
        session_store.clear_session(st.session_state.thread_id)
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="footer-note">PMT Computer • Demo online</div>', unsafe_allow_html=True)


st.markdown("""
<div class="pmt-hero">
    <div class="pmt-title">💻 PMT Computer AI Agent</div>
    <div class="pmt-subtitle">
        Hệ thống AI Agent đa kênh ứng dụng RAG cho chăm sóc khách hàng cửa hàng máy tính
    </div>
    <div class="pmt-badge-row">
        <div class="pmt-badge">Tư vấn linh kiện</div>
        <div class="pmt-badge">Tra cứu đơn hàng</div>
        <div class="pmt-badge">Bảo hành / đổi trả</div>
        <div class="pmt-badge">Memory nhiều lượt</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pmt-note">
Bạn có thể hỏi về sản phẩm, đơn hàng, bảo hành, đổi trả, FAQ linh kiện hoặc tư vấn mua hàng.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pmt-chat-wrap">', unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)