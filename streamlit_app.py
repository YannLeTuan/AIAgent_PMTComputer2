import html
import os
import re
import uuid
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="PMT Computer",
    page_icon="🖥️",
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
        padding-top: 0.8rem;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: #0f1115;
        border-right: 1px solid rgba(255,255,255,0.06);
        min-width: 300px;
        max-width: 300px;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6 !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.7rem;
    }

    .sidebar-logo {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: linear-gradient(135deg, #d90429, #8d0b22);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 22px rgba(217, 4, 41, 0.28);
    }

    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }

    .sidebar-subtitle {
        color: #b8bec9 !important;
        font-size: 0.92rem;
        line-height: 1.65;
        margin-bottom: 1.2rem;
    }

    .sidebar-section-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.9rem;
        margin-bottom: 0.55rem;
    }

    .sidebar-card {
        background: #171a21;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-card ul {
        margin: 0;
        padding-left: 1.15rem;
    }

    .sidebar-card li {
        margin-bottom: 0.55rem;
        color: #e5e7eb !important;
        line-height: 1.65;
    }

    .sidebar-footer {
        margin-top: 1rem;
        color: #98a2b3 !important;
        font-size: 0.82rem;
        text-align: center;
    }

    .hero-wrap {
        padding-top: 0.2rem;
        padding-bottom: 0.6rem;
    }

    .hero-brand-row {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin-bottom: 0.35rem;
    }

    .hero-logo {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        background: linear-gradient(135deg, #d90429, #8d0b22);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 900;
        font-size: 1.05rem;
        box-shadow: 0 10px 28px rgba(217, 4, 41, 0.22);
        flex-shrink: 0;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #121826;
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
        background: #fff1f3;
        color: #b00020;
        border: 1px solid #ffd0d8;
        padding: 0.42rem 0.82rem;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 700;
    }

    .intro-note {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 18px;
        padding: 1rem 1rem;
        color: #5f6b7a;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
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
        padding: 0.92rem 1rem;
        border-radius: 22px;
        line-height: 1.7;
        font-size: 1rem;
        word-wrap: break-word;
        white-space: normal;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.03);
    }

    .msg-bubble.user {
        background: #d90429;
        color: #ffffff;
        border: 1px solid #b00020;
        border-bottom-right-radius: 9px;
    }

    .msg-bubble.assistant {
        background: #ffffff;
        color: #1f2937;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-bottom-left-radius: 9px;
    }

    .msg-label {
        font-size: 0.77rem;
        font-weight: 800;
        margin-bottom: 0.42rem;
        opacity: 0.82;
        letter-spacing: 0.02em;
    }

    .msg-bubble.user .msg-label {
        color: rgba(255,255,255,0.86);
    }

    .msg-bubble.assistant .msg-label {
        color: #5b6472;
    }

    .msg-bubble p {
        margin: 0 0 0.65rem 0;
    }

    .msg-bubble p:last-child {
        margin-bottom: 0;
    }

    .msg-bubble ul {
        margin-top: 0.2rem;
        margin-bottom: 0.55rem;
        padding-left: 1.25rem;
    }

    .msg-bubble li {
        margin-bottom: 0.32rem;
    }

    .quick-row-title {
        margin-top: 0.4rem;
        margin-bottom: 0.55rem;
        color: #4b5563;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .input-card {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 20px;
        padding: 0.85rem 0.95rem 0.35rem 0.95rem;
        margin-top: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }

    .stTextInput > div > div > input {
        border-radius: 14px !important;
        padding: 0.88rem 1rem !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        background: #fbfcfe !important;
        font-size: 1rem !important;
    }

    .stButton > button {
        width: 100%;
        border-radius: 14px;
        font-weight: 700;
        padding: 0.78rem 0.95rem;
        border: 1px solid rgba(15, 23, 42, 0.08);
    }

    .send-button button {
        background: linear-gradient(135deg, #d90429, #b00020) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 22px rgba(217, 4, 41, 0.2);
    }

    .welcome-card {
        background: #ffffff;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 18px;
        padding: 1rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
    }

    .welcome-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #121826;
        margin-bottom: 0.35rem;
    }

    .welcome-text {
        color: #5f6b7a;
        line-height: 1.7;
        font-size: 0.96rem;
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
                parts.append("<ul>")
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


def submit_prompt(prompt: str):
    clean_input = (prompt or "").strip()
    if not clean_input:
        return

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


init_demo_resources()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">PMT</div>
        <div>
            <div class="sidebar-title">PMT Computer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-subtitle">Trợ lý AI hỗ trợ chăm sóc khách hàng cho cửa hàng linh kiện và thiết bị máy tính PMT Computer.</div>',
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

    st.markdown('<div class="sidebar-footer">PMT Computer • Online demo</div>', unsafe_allow_html=True)


left_pad, center, right_pad = st.columns([1.0, 6.4, 1.0])

with center:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-brand-row">
            <div class="hero-logo">PMT</div>
            <div>
                <div class="hero-title">PMT Computer AI Agent</div>
            </div>
        </div>
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

    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">Bắt đầu nhanh</div>
            <div class="welcome-text">
                Chọn một câu hỏi gợi ý bên dưới hoặc nhập câu hỏi của bạn để trải nghiệm hệ thống.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="quick-row-title">Gợi ý thao tác nhanh</div>', unsafe_allow_html=True)
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            if st.button("CPU bảo hành bao lâu?"):
                submit_prompt("CPU bảo hành bao lâu?")
                st.rerun()
        with q2:
            if st.button("Tìm SSD Samsung"):
                submit_prompt("Tìm SSD Samsung")
                st.rerun()
        with q3:
            if st.button("Kiểm tra ORD003"):
                submit_prompt("Kiểm tra đơn hàng ORD003")
                st.rerun()
        with q4:
            if st.button("Tôi muốn build máy chơi game"):
                submit_prompt("Tôi muốn build máy chơi game")
                st.rerun()

    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"])

    with st.container():
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            input_col, button_col = st.columns([8.9, 1.1])
            with input_col:
                user_input = st.text_input(
                    "",
                    placeholder="Nhập câu hỏi của bạn...",
                    label_visibility="collapsed"
                )
            with button_col:
                st.markdown('<div class="send-button">', unsafe_allow_html=True)
                submitted = st.form_submit_button("Gửi")
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted and user_input.strip():
        submit_prompt(user_input)
        st.rerun()