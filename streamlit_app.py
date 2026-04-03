import html
import os
import re
import uuid
import time
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
    [data-testid="stHeader"] {display: none;}
    [data-testid="stTopBlock"] {display: none;}

    :root {
        --pmt-bg: #f4f6fb;
        --pmt-surface: #ffffff;
        --pmt-border: rgba(15, 23, 42, 0.08);
        --pmt-text: #1f2f46;
        --pmt-muted: #687385;
        --pmt-primary: #163a70;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .main > div {
        padding-top: 0rem;
    }

    .block-container {
        max-width: 850px !important;
        margin: 0 auto !important;
        padding-top: 2rem;
        padding-bottom: 7rem; 
    }

    div[data-testid="stChatInput"] {
        max-width: 850px !important;
        margin: 0 auto !important;
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
        margin-bottom: 0.8rem;
    }

    .sidebar-logo {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        background: linear-gradient(135deg, #102d57 0%, #1f5fae 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        font-weight: 800;
        box-shadow: 0 10px 20px rgba(22, 58, 112, 0.18);
    }

    .sidebar-brand-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--pmt-text);
        line-height: 1.1;
        margin: 0;
    }

    .sidebar-brand-subtitle {
        color: var(--pmt-muted);
        font-size: 0.93rem;
        line-height: 1.5;
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
        background: rgba(255,255,255,0.95);
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
        padding-top: 0.4rem;
        padding-bottom: 0.8rem;
    }

    .hero-topline {
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 700;
        color: #295eb7;
        background: #edf3ff;
        border: 1px solid #dbe7ff;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        margin-bottom: 0.85rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: var(--pmt-text);
        margin: 0;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }

    .hero-title-accent {
        color: var(--pmt-primary);
    }

    .hero-subtitle {
        color: var(--pmt-muted);
        font-size: 1rem;
        margin-top: 0.45rem;
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

    .quick-actions-title {
        font-size: 0.92rem;
        font-weight: 800;
        color: var(--pmt-text);
        margin-bottom: 0.55rem;
        margin-top: 0.5rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88rem;
        padding: 0.45rem 0.7rem;
        border: 1px solid rgba(15, 23, 42, 0.1);
        background: #ffffff;
        color: var(--pmt-text);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #a8bce6;
        background: #fcfdff;
    }

    .msg-row {
        display: flex;
        width: 100%;
        margin-bottom: 1.8rem;
    }

    .msg-row.user {
        justify-content: flex-end;
    }

    .msg-row.assistant {
        justify-content: flex-start;
        align-items: flex-start;
    }

    .bot-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #102d57 0%, #1f5fae 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.65rem;
        font-weight: 800;
        margin-right: 12px;
        margin-top: 4px;
        flex-shrink: 0;
        box-shadow: 0 2px 5px rgba(22, 58, 112, 0.15);
    }

    .msg-bubble {
        font-size: 0.98rem;
        line-height: 1.65;
        word-wrap: break-word;
    }

    .msg-bubble.user {
        max-width: 75%;
        padding: 0.85rem 1.15rem;
        border-radius: 20px;
        background-color: #4072c2;
        color: #ffffff;
        border-bottom-right-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    .msg-bubble.assistant {
        max-width: 92%;
        padding: 0.2rem 0;
        border-radius: 0;
        background-color: transparent;
        color: #1c1e21;
    }

    .msg-bubble p { margin: 0 0 0.6rem 0; }
    .msg-bubble p:last-child { margin-bottom: 0; }
    .msg-bubble ul { margin: 0.3rem 0; padding-left: 1.5rem; }
    .msg-bubble li { margin-bottom: 0.25rem; }
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

def stream_generator(text: str):
    words = text.split(" ")
    for i in range(0, len(words), 2):
        yield " ".join(words[i:i+2]) + " "
        time.sleep(0.015)

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
    bubble_html = simple_markdown_to_html(content)
    if role == "user":
        return f"""
        <div class="msg-row user">
            <div class="msg-bubble user">
                {bubble_html}
            </div>
        </div>
        """
    else:
        return f"""
        <div class="msg-row assistant">
            <div class="bot-avatar">PMT</div>
            <div class="msg-bubble assistant">
                {bubble_html}
            </div>
        </div>
        """

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

    st.markdown('<div class="sidebar-section-title">Gợi ý câu hỏi</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-card">
        <ul>
            <li>Ổ cứng SSD khác HDD thế nào?</li>
            <li>Tôi muốn build PC chơi game</li>
            <li>Kiểm tra đơn hàng của tôi</li>
            <li>Liệt kê danh sách các CPU</li>
            <li>Mainboard nào hỗ trợ Intel Gen 14?</li>
            <li>Shop có hỗ trợ trả góp không?</li>
            <li>Cho tôi xin địa chỉ cửa hàng</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Reset dữ liệu", use_container_width=True):
            reset_demo_state()
            st.rerun()
    with col_b:
        if st.button("Xóa hội thoại", use_container_width=True):
            session_store.clear_session(st.session_state.thread_id)
            st.session_state.messages = []
            st.rerun()

    st.markdown('<div class="sidebar-footer">PMT Computer • Demo online</div>', unsafe_allow_html=True)


prompt_to_send = None

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
        <div class="hero-badge">Memory multi-turn</div>
    </div>
</div>
""", unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown('<div class="quick-actions-title">Gợi ý thao tác nhanh</div>', unsafe_allow_html=True)

    row1 = st.columns(2)
    with row1[0]:
        if st.button("Ổ cứng SSD khác HDD như thế nào?", use_container_width=True):
            prompt_to_send = "Ổ cứng SSD khác HDD như thế nào?"
    with row1[1]:
        if st.button("Tôi muốn build PC chơi game", use_container_width=True):
            prompt_to_send = "Tôi muốn build PC chơi game"

    row2 = st.columns(2)
    with row2[0]:
        if st.button("Kiểm tra đơn hàng của tôi", use_container_width=True):
            prompt_to_send = "Kiểm tra đơn hàng của tôi"
    with row2[1]:
        if st.button("Liệt kê danh sách các CPU", use_container_width=True):
            prompt_to_send = "Liệt kê danh sách các CPU"

for msg in st.session_state.messages:
    st.markdown(get_message_html(msg["role"], msg["content"]), unsafe_allow_html=True)

user_input = st.chat_input("Nhập câu hỏi của bạn...")
prompt = user_input or prompt_to_send

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(get_message_html("user", prompt), unsafe_allow_html=True)

    history = session_store.get_history(st.session_state.thread_id)
    context_state = session_store.get_context(st.session_state.thread_id)

    result = chat_with_agent(
        prompt,
        history,
        context_state,
        thread_id=st.session_state.thread_id
    )

    session_store.set_history(st.session_state.thread_id, result["history"])
    session_store.set_context(st.session_state.thread_id, result["context_state"])

    placeholder = st.empty()
    streamed_text = ""
    for chunk in stream_generator(result["answer"]):
        streamed_text += chunk
        placeholder.markdown(get_message_html("assistant", streamed_text), unsafe_allow_html=True)
        
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    st.rerun()