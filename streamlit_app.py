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
    :root {
        --pmt-bg: #f5f7fb;
        --pmt-surface: #ffffff;
        --pmt-border: rgba(15, 23, 42, 0.08);
        --pmt-text: #1f2f46;
        --pmt-muted: #687385;
        --pmt-primary: #163a70;
        --pmt-primary-2: #275faa;
        --pmt-primary-soft: #eef4ff;
        --pmt-user-bg: #dcecff;
        --pmt-user-text: #17345d;
        --pmt-bot-bg: #f7f8fb;
        --pmt-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .main > div {
        padding-top: 0.6rem;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7f8fc 0%, #f2f5fb 100%);
        border-right: 1px solid var(--pmt-border);
        min-width: 310px;
        max-width: 310px;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.85rem;
    }

    .sidebar-logo {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: linear-gradient(135deg, #102d57 0%, #1f5fae 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        font-weight: 900;
        box-shadow: 0 10px 20px rgba(22, 58, 112, 0.18);
        letter-spacing: 0.04em;
    }

    .sidebar-brand-title {
        font-size: 1.55rem;
        font-weight: 900;
        color: var(--pmt-text);
        line-height: 1.05;
        margin: 0;
    }

    .sidebar-brand-subtitle {
        color: var(--pmt-muted);
        font-size: 0.93rem;
        line-height: 1.55;
        margin-top: 0.35rem;
    }

    .sidebar-section-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--pmt-text);
        margin-top: 1rem;
        margin-bottom: 0.55rem;
    }

    .sidebar-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid var(--pmt-border);
        border-radius: 20px;
        padding: 1rem 1rem 0.95rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.03);
    }

    .sidebar-card ul {
        margin: 0;
        padding-left: 1.15rem;
    }

    .sidebar-card li {
        margin-bottom: 0.52rem;
        line-height: 1.65;
        color: #243244;
    }

    .sidebar-footer {
        margin-top: 1rem;
        color: #8a93a5;
        font-size: 0.82rem;
        text-align: center;
    }

    .hero-wrap {
        padding-top: 0.35rem;
        padding-bottom: 0.8rem;
    }

    .hero-topline {
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 800;
        color: #295eb7;
        background: #edf3ff;
        border: 1px solid #dbe7ff;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.85rem;
    }

    .hero-title {
        font-size: 2.85rem;
        font-weight: 900;
        color: var(--pmt-text);
        margin: 0;
        line-height: 1.08;
        letter-spacing: -0.02em;
    }

    .hero-title-accent {
        color: var(--pmt-primary);
    }

    .hero-subtitle {
        color: var(--pmt-muted);
        font-size: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        line-height: 1.7;
    }

    .hero-badge-row {
        display: flex;
        gap: 0.65rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }

    .hero-badge {
        background: #eef4ff;
        color: #2b5fb8;
        border: 1px solid #dce7ff;
        padding: 0.42rem 0.85rem;
        border-radius: 999px;
        font-size: 0.86rem;
        font-weight: 700;
    }

    .intro-note {
        background: var(--pmt-surface);
        border: 1px solid var(--pmt-border);
        border-radius: 18px;
        padding: 1rem 1.05rem;
        color: var(--pmt-muted);
        margin-bottom: 0.95rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03);
    }

    .welcome-card {
        background: linear-gradient(180deg, #ffffff 0%, #fbfcff 100%);
        border: 1px solid var(--pmt-border);
        border-radius: 22px;
        padding: 1.1rem 1.1rem 1rem 1.1rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03);
        margin-bottom: 1rem;
    }

    .welcome-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--pmt-text);
        margin-bottom: 0.45rem;
    }

    .welcome-subtitle {
        color: var(--pmt-muted);
        line-height: 1.65;
        margin-bottom: 0.9rem;
    }

    .quick-actions-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: var(--pmt-text);
        margin-bottom: 0.55rem;
    }

    .chat-shell {
        background: var(--pmt-surface);
        border: 1px solid var(--pmt-border);
        border-radius: 24px;
        box-shadow: var(--pmt-shadow);
        padding: 1.05rem 1rem 1rem 1rem;
    }

    .msg-row {
        display: flex;
        margin-bottom: 1rem;
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
        padding: 0.95rem 1.05rem;
        border-radius: 22px;
        line-height: 1.7;
        font-size: 1rem;
        word-wrap: break-word;
        white-space: normal;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02);
    }

    .msg-bubble.user {
        background: var(--pmt-user-bg);
        color: var(--pmt-user-text);
        border: 1px solid #cddfff;
        border-bottom-right-radius: 8px;
    }

    .msg-bubble.assistant {
        background: var(--pmt-bot-bg);
        color: #1f2937;
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-bottom-left-radius: 8px;
    }

    .msg-label {
        font-size: 0.76rem;
        font-weight: 800;
        margin-bottom: 0.42rem;
        opacity: 0.72;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }

    .msg-bubble p {
        margin: 0 0 0.65rem 0;
    }

    .msg-bubble p:last-child {
        margin-bottom: 0;
    }

    .msg-bubble ul {
        margin-top: 0.25rem;
        margin-bottom: 0.6rem;
        padding-left: 1.25rem;
    }

    .msg-bubble li {
        margin-bottom: 0.35rem;
    }

    .input-guide {
        text-align: center;
        color: #7b8798;
        font-size: 0.88rem;
        margin-top: 0.85rem;
        margin-bottom: 0.25rem;
    }

    .footer-note {
        text-align: center;
        color: #8b95a7;
        font-size: 0.82rem;
        margin-top: 0.95rem;
    }

    /* Chat input native */
    div[data-testid="stChatInput"] {
        margin-top: 0.85rem;
    }

    div[data-testid="stChatInput"] > div {
        background: #ffffff;
        border: 1px solid var(--pmt-border);
        border-radius: 22px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.03);
        padding-top: 0.25rem;
        padding-bottom: 0.1rem;
    }

    div[data-testid="stChatInput"] textarea,
    div[data-testid="stChatInput"] input {
        background: #fbfcfe !important;
        border-radius: 14px !important;
    }

    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #14386a 0%, #275faa 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
    }

    .quick-btn button {
        border-radius: 999px !important;
        font-weight: 700 !important;
        border: 1px solid #dce7ff !important;
        background: #eef4ff !important;
        color: #2b5fb8 !important;
        padding: 0.55rem 0.8rem !important;
    }

    .sidebar-action button {
        border-radius: 14px !important;
        font-weight: 800 !important;
        padding: 0.78rem 0.9rem !important;
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


def get_message_html(role: str, content: str) -> str:
    role_class = "user" if role == "user" else "assistant"
    label = "Bạn" if role == "user" else "PMT Assistant"
    bubble_html = simple_markdown_to_html(content)

    return f"""
    <div class="msg-row {role_class}">
        <div class="msg-bubble {role_class}">
            <div class="msg-label">{label}</div>
            {bubble_html}
        </div>
    </div>
    """


def render_chat_block(messages: list[dict]):
    if not messages:
        return
    full_chat_html = '<div class="chat-shell">'
    for msg in messages:
        full_chat_html += get_message_html(msg["role"], msg["content"])
    full_chat_html += '</div>'
    st.markdown(full_chat_html, unsafe_allow_html=True)


def process_prompt(prompt: str):
    clean_input = prompt.strip()
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

    st.rerun()


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
            <div class="sidebar-brand-title">PMT Computer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-brand-subtitle">Trợ lý AI chăm sóc khách hàng cho hệ thống PMT Computer, hỗ trợ sản phẩm, đơn hàng, bảo hành và tư vấn mua hàng.</div>',
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

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="sidebar-action">', unsafe_allow_html=True)
        if st.button("Reset dữ liệu demo", use_container_width=True):
            reset_demo_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="sidebar-action">', unsafe_allow_html=True)
        if st.button("Xóa hội thoại", use_container_width=True):
            session_store.clear_session(st.session_state.thread_id)
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-footer">PMT Computer • Demo online</div>', unsafe_allow_html=True)


left_pad, center, right_pad = st.columns([1.0, 6.4, 1.0])

with center:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-topline">AI Customer Support • PMT Computer</div>
        <div class="hero-title"><span class="hero-title-accent">PMT Computer</span> AI Agent</div>
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

    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">Bắt đầu nhanh</div>
            <div class="welcome-subtitle">
                Chọn một gợi ý bên dưới để trải nghiệm nhanh các chức năng chính của hệ thống.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="quick-actions-title">Gợi ý thao tác nhanh</div>', unsafe_allow_html=True)

        row1 = st.columns(4)
        with row1[0]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("CPU bảo hành bao lâu?", use_container_width=True):
                process_prompt("CPU bảo hành bao lâu?")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1[1]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Tìm SSD Samsung", use_container_width=True):
                process_prompt("Tìm SSD Samsung")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1[2]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Kiểm tra đơn ORD003", use_container_width=True):
                process_prompt("Kiểm tra đơn hàng ORD003")
            st.markdown('</div>', unsafe_allow_html=True)

        with row1[3]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Khách Phạm Minh Tuấn đã đặt gì?", use_container_width=True):
                process_prompt("Khách phamminhtuan.pmt@gmail.com đã đặt gì?")
            st.markdown('</div>', unsafe_allow_html=True)

        row2 = st.columns(4)
        with row2[0]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Ổ cứng khác SSD thế nào?", use_container_width=True):
                process_prompt("Ổ cứng khác SSD thế nào?")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2[1]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Trong các đơn đó, đơn nào đang xử lý?", use_container_width=True):
                process_prompt("Trong các đơn đó, đơn nào đang xử lý?")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2[2]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Tôi muốn build máy chơi game", use_container_width=True):
                process_prompt("Tôi muốn build máy chơi game")
            st.markdown('</div>', unsafe_allow_html=True)

        with row2[3]:
            st.markdown('<div class="quick-btn">', unsafe_allow_html=True)
            if st.button("Phạm Minh Tuấn là ai?", use_container_width=True):
                process_prompt("Phạm Minh Tuấn là ai?")
            st.markdown('</div>', unsafe_allow_html=True)

    render_chat_block(st.session_state.messages)

    st.markdown('<div class="input-guide">Nhập câu hỏi mới để tiếp tục hội thoại với PMT Computer AI Agent</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Nhập câu hỏi của bạn...")

    if user_input:
        process_prompt(user_input)

    st.markdown('<div class="footer-note">Bản demo phục vụ đánh giá đồ án • PMT Computer AI Agent</div>', unsafe_allow_html=True)