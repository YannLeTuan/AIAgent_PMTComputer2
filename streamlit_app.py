import html
import os
import re
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
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        max-width: 1450px;
    }

    [data-testid="stSidebar"] {
        background: #f7f8fb;
        border-right: 1px solid rgba(15, 23, 42, 0.08);
        min-width: 290px;
        max-width: 290px;
    }

    .sidebar-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1f2f46;
        margin-bottom: 0.25rem;
    }

    .sidebar-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .sidebar-section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1f2f46;
        margin-top: 0.8rem;
        margin-bottom: 0.55rem;
    }

    .sidebar-card {
        background: white;
        border: 1px solid rgba(15, 23, 42, 0.07);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03);
    }

    .sidebar-card ul {
        margin: 0;
        padding-left: 1.15rem;
    }

    .sidebar-card li {
        margin-bottom: 0.55rem;
        color: #2d3748;
        line-height: 1.65;
    }

    .hero-wrap {
        padding-top: 0.3rem;
        padding-bottom: 0.8rem;
    }

    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #1f2f46;
        margin: 0;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: 0.35rem;
        margin-bottom: 1rem;
    }

    .hero-badge-row {
        display: flex;
        gap: 0.65rem;
        flex-wrap: wrap;
        margin-bottom: 0.8rem;
    }

    .hero-badge {
        background: #eef4ff;
        color: #295eb7;
        border: 1px solid #dce7ff;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 600;
    }

    .intro-note {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.07);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        color: #5f6b7a;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03);
    }

    .chat-shell {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 24px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        padding: 1.1rem 1rem 0.8rem 1rem;
    }

    .msg-row {
        display: flex;
        margin-bottom: 0.95rem;
        width: 100%;
    }

    .msg-row.user {
        justify-content: flex-end;
    }

    .msg-row.assistant {
        justify-content: flex-start;
    }

    .msg-bubble {
        max-width: 76%;
        padding: 0.88rem 1rem;
        border-radius: 20px;
        line-height: 1.65;
        font-size: 1rem;
        word-wrap: break-word;
        white-space: normal;
    }

    .msg-bubble.user {
        background: #e9f1ff;
        color: #1e3a5f;
        border: 1px solid #d8e7ff;
        border-bottom-right-radius: 8px;
    }

    .msg-bubble.assistant {
        background: #f7f8fb;
        color: #1f2937;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-bottom-left-radius: 8px;
    }

    .msg-label {
        font-size: 0.77rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        opacity: 0.75;
        letter-spacing: 0.02em;
    }

    .msg-bubble p {
        margin: 0 0 0.65rem 0;
    }

    .msg-bubble p:last-child {
        margin-bottom: 0;
    }

    .msg-bubble ul {
        margin-top: 0.2rem;
        margin-bottom: 0.6rem;
        padding-left: 1.25rem;
    }

    .msg-bubble li {
        margin-bottom: 0.35rem;
    }

    .input-shell {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 18px;
        padding: 0.75rem 0.8rem 0.25rem 0.8rem;
        margin-top: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03);
    }

    .stTextInput > div > div > input {
        border-radius: 12px !important;
        padding: 0.78rem 0.95rem !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        background: #fbfcfe !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.72rem 0.9rem;
    }

    .sidebar-footer {
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


def simple_markdown_to_html(text: str) -> str:
    text = text or ""
    lines = text.splitlines()
    parts = []
    in_list = False

    def format_inline(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return s

    for raw in lines:
        stripped = raw.strip()

        if not stripped:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                parts.append('<ul>')
                in_list = True
            item = format_inline(stripped[2:].strip())
            parts.append(f"<li>{item}</li>")
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<p>{format_inline(stripped)}</p>")

    if in_list:
        parts.append("</ul>")

    return "".join(parts) if parts else "<p></p>"


def render_message(role: str, content: str):
    role_class = "user" if role == "user" else "assistant"
    label = "Bạn" if role == "user" else "PMT Assistant"
    bubble_html = simple_markdown_to_html(content)

    st.markdown(
        f"""
        <div class="msg-row {role_class}">
            <div class="msg-bubble {role_class}">
                <div class="msg-label">{label}</div>
                {bubble_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


init_demo_resources()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.markdown('<div class="sidebar-title">PMT Computer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-subtitle">Nhân viên chăm sóc khách hàng AI, hỗ trợ cho cửa hàng Phạm Minh Tuấn Computer</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section-title">Chức năng chính</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card">
        <ul>
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
        <ul>
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

    st.markdown('<div class="sidebar-footer">PMT Computer • Demo online</div>', unsafe_allow_html=True)


left_pad, center, right_pad = st.columns([1.1, 6.2, 1.1])

with center:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-title">💻 PMT Computer AI Agent</div>
        <div class="hero-subtitle">
            Hệ thống AI Agent đa kênh ứng dụng RAG cho chăm sóc khách hàng cửa hàng máy tính
        </div>
        <div class="hero-badge-row">
            <div class="hero-badge">Tư vấn linh kiện</div>
            <div class="hero-badge">Tra cứu đơn hàng</div>
            <div class="hero-badge">Bảo hành / đổi trả</div>
            <div class="hero-badge">Memory nhiều lượt</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="intro-note">
        Bạn có thể hỏi về sản phẩm, đơn hàng, bảo hành, đổi trả, FAQ linh kiện hoặc tư vấn mua hàng.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"])

    st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="input-shell">', unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            input_col, button_col = st.columns([8.8, 1.2])
            with input_col:
                user_input = st.text_input(
                    "",
                    placeholder="Nhập câu hỏi của bạn...",
                    label_visibility="collapsed"
                )
            with button_col:
                submitted = st.form_submit_button("Gửi")

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and user_input.strip():
        clean_input = user_input.strip()

        st.session_state.messages.append({
            "role": "user",
            "content": clean_input
        })

        history = session_store.get_history(st.session_state.thread_id)
        context_state = session_store.get_context(st.session_state.thread_id)

        result = chat_with_agent(
            clean_input,
            history,
            context_state,
            thread_id=st.session_state.thread_id
        )

        session_store.set_history(st.session_state.thread_id, result["history"])
        session_store.set_context(st.session_state.thread_id, result["context_state"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"]
        })

        st.rerun()