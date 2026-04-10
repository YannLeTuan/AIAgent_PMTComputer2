<a id="readme-top"></a>

<div align="center">

  <h1>PMT Computer AI Agent</h1>
  <p><strong>Hệ thống AI Agent tư vấn & chăm sóc khách hàng đa kênh cho cửa hàng linh kiện máy tính</strong><br/>
  <em>Enterprise-Grade Omnichannel Customer Support powered by RAG + Agentic Workflow</em></p>

  <p>
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer">View Demo</a>
    ·
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer/issues">Report Bug</a>
    ·
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer/issues">Request Feature</a>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Google_Gemini-2.0_Flash-8E75B2?style=flat-square&logo=google&logoColor=white" alt="Gemini">
    <img src="https://img.shields.io/badge/FAISS-Vector_Search-444?style=flat-square" alt="FAISS">
    <img src="https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
    <img src="https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/SQLite-ORM-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  </p>

</div>

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Channels](#channels)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Overview

**PMT Computer AI Agent** là hệ thống AI Agent end-to-end, được xây dựng cho cửa hàng bán lẻ linh kiện máy tính PMT Computer. Hệ thống vượt ra ngoài giới hạn của chatbot thông thường bằng cách kết hợp hai kiến trúc hiện đại:

- **RAG (Retrieval-Augmented Generation):** Truy xuất ngữ cảnh từ cơ sở tri thức nội bộ gồm 14 tập dữ liệu (chính sách bảo hành, FAQ linh kiện, kịch bản hỏi đáp thực tế,...) thông qua FAISS vector search.
- **Agentic Workflow (Tool Calling):** Google Gemini đóng vai trò orchestrator, tự động quyết định khi nào cần gọi tool để truy vấn database nghiệp vụ thời gian thực (tra đơn hàng, hủy đơn, tìm sản phẩm, tư vấn build PC).

Được triển khai đa kênh: **Streamlit Web UI** và **Telegram Bot**, sử dụng cùng một backend RAG + Agent.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        CHANNELS                              │
│   Streamlit Web UI  │  Telegram Bot  │  REST API (FastAPI)  │
└────────────┬─────────────────┬──────────────────────────────┘
             │                 │
             ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                        │
│   Google Gemini 2.0 Flash  +  Tool Calling (Function Call)  │
│   ┌────────────────┐   ┌──────────────────────────────────┐ │
│   │  Prompt Builder│   │  Multi-turn Memory (Session TTL) │ │
│   │  + RAG Context │   │  + Context Manager               │ │
│   └────────────────┘   └──────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
           ┌───────────────────┼────────────────────┐
           ▼                   ▼                    ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   RAG PIPELINE  │  │   TOOL RUNNER    │  │   SMALL TALK     │
│ FAISS Vector DB │  │ order_tools      │  │ greeting/bye     │
│ 14 knowledge    │  │ product_tools    │  │ bypass RAG       │
│ base txt files  │  │ customer_tools   │  └──────────────────┘
│ sentence-trans- │  │ pc_build_tools   │
│ formers embed.  │  └────────┬─────────┘
└─────────────────┘           │
                              ▼
                   ┌─────────────────────┐
                   │   SQLite DATABASE   │
                   │  Customer | Product │
                   │  Order | SQLAlchemy │
                   └─────────────────────┘
```

---

## Key Features

| Feature | Description |
|---|---|
| **RAG Knowledge Base** | 14 file tri thức tiếng Việt: chính sách, FAQ, kịch bản thực tế. Chunked + embedded bằng `sentence-transformers`, indexed bằng FAISS |
| **Agentic Tool Calling** | Gemini tự quyết định gọi tool phù hợp: tra đơn hàng, hủy đơn, tìm sản phẩm, tư vấn build PC theo ngân sách |
| **Multi-turn Memory** | Session store với TTL 30 phút, thread-safe, tự động trim lịch sử khi vượt 10 lượt |
| **Context Manager** | Nhận diện tham chiếu ("đơn này", "sản phẩm kia") và bảo toàn ngữ cảnh hội thoại |
| **PC Build Advisor** | Tư vấn cấu hình PC theo ngân sách + mục đích (gaming, văn phòng, đồ họa, lập trình) |
| **Security Guard** | Whitelist tool, xác thực email trước khi hủy đơn, không tự bịa thông tin nghiệp vụ |
| **Omnichannel** | Streamlit Web + Telegram Bot + REST API (FastAPI) cùng chung backend |
| **Evaluation Framework** | Test harness đánh giá độ chính xác, context adherence, hallucination rate |

---

## Technology Stack

**AI & Machine Learning**

![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat-square&logo=google&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-444444?style=flat-square)
![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-Embedding-4A90D9?style=flat-square)

**Application & API**

![Python](https://img.shields.io/badge/Python-3670A0?style=flat-square&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)

**Data Layer**

![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?style=flat-square&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square)

**Frontend & Integrations**

![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=flat-square&logo=streamlit&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-%23E34F26.svg?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-%231572B6.svg?style=flat-square&logo=css3&logoColor=white)

---

## Project Structure

```
AIAgent_PMTComputer2/
├── app/
│   ├── agent/          # Orchestrator, memory, context, prompt builder, tool runner
│   ├── api/            # FastAPI REST endpoints
│   ├── channels/       # Streamlit UI, Telegram bot
│   ├── core/           # Config, logger, system prompt
│   ├── db/             # SQLAlchemy models, seed data, session
│   ├── rag/            # Ingest, retriever, FAISS vector store
│   └── tools/          # order, product, customer, pc_build tools
├── data/
│   ├── raw/            # 14 knowledge base .txt files (Vietnamese)
│   └── vector_index/   # FAISS index files
├── tests/              # Pytest unit tests
├── scripts/            # Evaluation & testing scripts
├── streamlit_app.py    # Streamlit entry point
├── requirements.txt
└── .env.example
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- Google Gemini API key ([Get one here](https://aistudio.google.com/))

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/YannLeTuan/AIAgent_PMTComputer.git
cd AIAgent_PMTComputer
```

**2. Create virtual environment**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment**

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
TOP_K_RETRIEVAL=3
TELEGRAM_BOT_TOKEN=your_telegram_token_here   # optional
```

**5. Initialize database**

```bash
python -m app.db.seed
```

**6. Build vector index**

```bash
python -m app.rag.ingest
```

**7. Launch**

```bash
# Streamlit web UI
streamlit run streamlit_app.py

# REST API
uvicorn app.api.main:app --reload

# Telegram Bot (requires TELEGRAM_BOT_TOKEN)
python run_telegram.py
```

---

## Channels

### Streamlit Web UI

Custom chat bubble interface built with HTML/CSS overrides on Streamlit. Hỗ trợ real-time streaming và multi-turn conversation.

### Telegram Bot

Cùng RAG + Agent backend, khách hàng nhắn tin qua Telegram để được hỗ trợ trực tiếp trên điện thoại.

### REST API

`POST /chat` — nhận `session_id` + `message`, trả về câu trả lời của Agent.

```json
{
  "session_id": "user_123",
  "message": "Đơn hàng ORD009 của tôi đang ở đâu?"
}
```

---

## Roadmap

- [x] RAG pipeline với FAISS local vector store
- [x] Agentic workflow với Google Gemini Function Calling
- [x] Multi-turn memory với session TTL
- [x] Omnichannel: Streamlit Web + Telegram + REST API
- [x] PC Build Advisor (budget + use case)
- [x] Security: tool whitelist, email authentication
- [x] Evaluation framework
- [ ] Hardware comparison tool
- [ ] Discord bot integration
- [ ] Automated evaluation metrics dashboard

---

## Author

**Pham Minh Tuan**

- Email: tuanqn8899@gmail.com
- GitHub: [@YannLeTuan](https://github.com/YannLeTuan)
- Project: [AIAgent_PMTComputer](https://github.com/YannLeTuan/AIAgent_PMTComputer)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
