<a id="readme-top"></a>

<div align="center">
  <img src="https://blog.omnichat.ai/wp-content/uploads/2025/02/AI-Agent-workflowss-en.png" alt="PMT Computer AI Agent Workflow" width="600">

  <h2>PMT Computer AI Agent</h2>
  <p>
    <strong>Enterprise-Grade Omnichannel Customer Support System powered by RAG and Agentic Workflow</strong>
    <br />
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer"><strong>Explore the Documentation »</strong></a>
    <br />
    <br />
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer">View Live Demo</a>
    ·
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer/issues">Report Issue</a>
    ·
    <a href="https://github.com/YannLeTuan/AIAgent_PMTComputer/issues">Request Feature</a>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square" alt="Python Version">
    <img src="https://img.shields.io/badge/LLM-Google_Gemini-orange?style=flat-square" alt="LLM Engine">
    <img src="https://img.shields.io/badge/Vector_DB-FAISS-lightgrey?style=flat-square" alt="Vector Database">
    <img src="https://img.shields.io/badge/Deployment-Streamlit_Cloud-red?style=flat-square" alt="Deployment">
  </p>
</div>

<hr />

## Abstract and Project Overview

The **PMT Computer AI Agent** is an end-to-end, automated customer service system engineered specifically for computer hardware retail. Developed as a capstone graduation project, it transcends the limitations of standard conversational bots by operating as a fully functional, autonomous agent.

The system leverages a sophisticated architecture combining **Retrieval-Augmented Generation (RAG)** for internal knowledge processing and **Tool Calling (Function Calling)** for real-time business operations. This allows the agent to not only answer policy and hardware capability queries but also actively interact with the company's database to check order statuses, verify customer histories, and provide highly personalized technical consulting.

Designed with an omnichannel approach, the architecture serves end-users seamlessly across a highly customized, responsive web interface and a dedicated Telegram bot, ensuring continuous availability and a standardized customer experience.

## System Architecture and Core Capabilities

The project is structured around a modular, microservices-inspired architecture to ensure scalability, maintainability, and accurate telemetry.

### 1. Advanced Retrieval-Augmented Generation (RAG)

- **Knowledge Ingestion:** Processes and indexes a comprehensive internal knowledge base (comprising 12 specialized textual datasets covering hardware specifications, warranty policies, and troubleshooting FAQs).
- **Semantic Search:** Utilizes `sentence-transformers` to generate high-dimensional embeddings, stored and queried locally via **FAISS** (Facebook AI Similarity Search) for low-latency, highly relevant context retrieval.

### 2. Autonomous Agentic Workflow (Tool Calling)

- **Dynamic Decision Making:** Powered by the Google Gemini API, the orchestrator evaluates user intent to determine whether to answer based on semantic context or to invoke specific business logic tools.
- **Database Interoperability:** Safely executes programmatic queries against a relational **SQLite** database (managed via SQLAlchemy ORM) to retrieve dynamic, real-time data such as tracking specific order IDs or pulling up historical customer configurations.

### 3. Contextual State Management (Multi-turn Memory)

- **Session Tracking:** Implements a robust session store utilizing unique thread identifiers to maintain conversational context across multiple turns.
- **Context Window Optimization:** Intelligently summarizes and prunes conversation history to maintain token efficiency without sacrificing the system's ability to handle complex, follow-up inquiries.

### 4. Omnichannel Delivery

- **Web Frontend (Streamlit):** Deployed on Streamlit Community Cloud. The default UI has been fundamentally overridden using custom HTML and CSS to create a modern, asynchronous "Bubble Chat" interface identical to leading communication platforms. It features real-time text streaming to eliminate perceived latency.
- **Messaging Integration (Telegram):** A concurrent bot instance built with `python-telegram-bot`, allowing customers to request support directly through their mobile devices using the exact same underlying RAG and Agent logic.

### 5. Evaluation and Telemetry

- **Quality Assurance Framework:** Includes custom evaluation scripts designed to test the agent's accuracy, context adherence, and hallucination rates against a predefined set of ground-truth interactions.
- **Comprehensive Logging:** System-wide logging tracks API latencies, retrieval confidence scores, and tool execution success rates, providing critical data for continuous model refinement.

## Technology Stack

The system is built entirely on a modern Python ecosystem, ensuring high performance and ease of deployment.

**Application & API Layer**<br/>
![Python](https://img.shields.io/badge/python-3670A0?style=flat-square&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)

**AI & Machine Learning**<br/>
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat-square&logo=google&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-444444?style=flat-square)
![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-Embedding-blue?style=flat-square)

**Data Persistence Layer**<br/>
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat-square&logo=sqlite&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=python&logoColor=white)

**Frontend & Integrations**<br/>
![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=flat-square&logo=streamlit&logoColor=white)
![Telegram API](https://img.shields.io/badge/Telegram_Bot-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat-square&logo=css3&logoColor=white)

## Local Installation and Setup

To run this project locally for development or evaluation purposes, follow these technical guidelines:

1. **Clone the repository**

   ```bash
   git clone [https://github.com/YannLeTuan/AIAgent_PMTComputer.git](https://github.com/YannLeTuan/AIAgent_PMTComputer.git)
   cd AIAgent_PMTComputer
   ```

2. **Initialize the virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory and configure your API keys and parameters:

   ```env
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   TOP_K_RETRIEVAL=3
   TELEGRAM_BOT_TOKEN=your_telegram_token
   ```

5. **Database and Vector Index Initialization**

   ```bash
   # Seed the SQLite database with mock products, customers, and orders
   python -m app.db.seed

   # Process raw text files and build the FAISS vector index
   python -m app.rag.ingest
   ```

6. **Launch the Application**
   ```bash
   # Run the Streamlit web interface
   streamlit run streamlit_app.py
   ```

## Roadmap and Future Enhancements

The core technical foundation is complete. Current and future development phases are focused on business-value features and optimization:

- [x] Initial architecture setup and database seeding.
- [x] RAG pipeline implementation with local FAISS.
- [x] Agent Orchestrator with Tool Calling capabilities.
- [x] Multi-turn memory management.
- [x] Omnichannel deployment (Streamlit + Telegram).
- [x] Asynchronous text streaming and UI/UX modernization.
- [ ] **Phase 2:** Implementation of "Build PC Advisor" (Constraint-based recommendation system).
- [ ] **Phase 2:** Hardware comparison capabilities.
- [ ] **Phase 3:** Final automated evaluation metrics reporting..

## Author & Contact

**Pham Minh Tuan**

- Email: tuanqn8899@gmail.com
- GitHub: [@YannLeTuan](https://github.com/YannLeTuan)
- Project Link: [AIAgent_PMTComputer](https://github.com/YannLeTuan/AIAgent_PMTComputer)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
