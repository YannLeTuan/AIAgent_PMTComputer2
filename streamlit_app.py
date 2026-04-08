import os
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
    /* DO NOT use display:none on stHeader — it contains stExpandSidebarButton.
       Hiding the whole header permanently kills the sidebar re-open button. */
    [data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }

    /* Hide only the visual clutter inside the header */
    [data-testid="stHeaderActionElements"],
    [data-testid="stHeaderLogo"],
    [data-testid="stAppDeployButton"],
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* Collapse button (inside sidebar, arrow pointing left) */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.10) !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background: #eef4ff !important;
        border-color: #9db8e8 !important;
    }

    /* Expand button (in header toolbar, shown when sidebar is collapsed) — Streamlit 1.55 */
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.10) !important;
    }
    [data-testid="stExpandSidebarButton"]:hover {
        background: #eef4ff !important;
        border-color: #9db8e8 !important;
    }

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
        min-width: 230px !important;
        max-width: 230px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        width: 230px !important;
        min-width: 230px !important;
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
        font-size: 1.2rem;
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
        font-size: 0.88rem;
        font-weight: 800;
        color: var(--pmt-text);
        margin-top: 1rem;
        margin-bottom: 0.55rem;
    }

    .sidebar-card {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        margin-bottom: 1rem;
        box-shadow: none;
    }

    .sidebar-card ul {
        margin: 0;
        padding: 0;
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 0.28rem;
    }

    .sidebar-card li {
        display: block;
        text-align: left;
        font-size: 0.80rem;
        line-height: 1.4;
        color: #2b4a7a;
        background: transparent;
        border: none;
        border-bottom: 1px solid #e8edf5;
        border-radius: 0;
        padding: 0.38rem 0.1rem;
        white-space: normal;
    }

    .sidebar-card li:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }

    .sidebar-card li::before {
        content: none;
    }

    .sidebar-footer {
        margin-top: 1rem;
        color: #8a93a5;
        font-size: 0.82rem;
        text-align: center;
    }

    .hero-wrap {
        padding-top: 0.4rem;
        padding-bottom: 0.2rem;
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
        margin-bottom: 0.3rem;
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
        font-size: 0.75rem;
        padding: 0.45rem 0.4rem;
        border: 1px solid rgba(15, 23, 42, 0.1);
        background: #ffffff;
        color: var(--pmt-text);
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] .stButton > button {
        font-size: 70% !important;
        padding: 0.25rem 0.4rem !important;
        min-height: 0 !important;
    }

    .stButton > button:hover {
        border-color: #a8bce6;
        background: #fcfdff;
    }

    /* Native st.chat_message() styling */
    [data-testid="stChatMessage"] {
        padding: 0.4rem 0;
        gap: 0.75rem;
    }

    /* User bubble — blue pill */
    [data-testid="stChatMessage"][data-testid*="user"] .stChatMessageContent,
    [data-testid="stChatMessageContent"] {
        font-size: 0.97rem;
        line-height: 1.65;
    }

    /* Badge clickable buttons */
    #badge-row + div .stButton > button {
        background: #eef4ff !important;
        color: #163a70 !important;
        border: 1.5px solid #9db8e8 !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 0.55rem 0.5rem !important;
        box-shadow: 0 2px 8px rgba(22, 58, 112, 0.10) !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    #badge-row + div .stButton > button:hover {
        background: #dceaff !important;
        border-color: #2b5fb8 !important;
        color: #102d57 !important;
        box-shadow: 0 4px 16px rgba(22, 58, 112, 0.20) !important;
        transform: translateY(-2px) !important;
    }
    #badge-row + div .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 1px 4px rgba(22, 58, 112, 0.10) !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def init_demo_resources():
    db_file = Path("ecommerce.db")
    vector_file = Path("data/vector_index/faiss_index.faiss")
    vector_meta = Path("data/vector_index/faiss_index.json")

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
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.035)

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

if not st.session_state.messages:
    st.markdown("""
<div class="hero-wrap">
    <div class="hero-topline">AI Customer Support • PMT Computer</div>
    <div class="hero-title"><span class="hero-title-accent">PMT Computer</span> AI Agent</div>
    <div class="hero-subtitle">
        Hệ thống AI Agent đa kênh ứng dụng RAG cho chăm sóc khách hàng cửa hàng máy tính
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div id="badge-row"><p style="font-size:0.85rem;font-weight:700;color:#1f2f46;margin:0 0 0.45rem 0;">Thao tác nhanh</p></div>', unsafe_allow_html=True)
    badge_cols = st.columns(4)
    with badge_cols[0]:
        if st.button("Tư vấn build PC", key="badge_build"):
            prompt_to_send = "Tôi muốn build PC, bạn có thể tư vấn giúp tôi không?"
    with badge_cols[1]:
        if st.button("Tra cứu đơn hàng", key="badge_order"):
            prompt_to_send = "Tôi muốn tra cứu đơn hàng của mình"
    with badge_cols[2]:
        if st.button("Bảo hành / đổi trả", key="badge_warranty"):
            prompt_to_send = "Chính sách bảo hành và đổi trả của PMT Computer như thế nào?"
    with badge_cols[3]:
        if st.button("Thông tin cửa hàng", key="badge_info"):
            prompt_to_send = "Cho tôi biết thông tin, địa chỉ và giờ làm việc của PMT Computer"

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Nhập câu hỏi của bạn...")
prompt = user_input or prompt_to_send

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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

    with st.chat_message("assistant"):
        st.write_stream(stream_generator(result["answer"]))

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    st.rerun()