# Code Review: Module RAG & Agent

**Phạm vi:** `app/rag/` (ingest.py, vector_store.py, retriever.py) và `app/agent/` (orchestrator.py, memory.py)
**Ngày:** 2026-04-08
**Cập nhật:** 2026-04-09
**Tiêu chí:** (A) Lỗ hổng bảo mật / Bugs ẩn · (B) Hiệu năng · (C) Clean Code

---

## Tóm tắt điểm nghiêm trọng

| Mức          | Số lượng ban đầu | Đã sửa |
| ------------ | ---------------- | ------ |
| 🔴 Critical  | 2                | 2      |
| 🟠 Important | 5                | 4      |
| 🟡 Minor     | 6                | 3      |

---

## A) Lỗ hổng Bảo mật / Bugs ẩn

### ✅ A-1 — Prompt Injection → Tool Abuse không kiểm soát

**File:** `app/agent/tool_runner.py`

**Đã sửa:** `run_tool` dùng dispatch dict làm whitelist ngầm — chỉ các tool có trong dict mới được gọi. Tool destructive (`cancel_order`, `cancel_multiple_orders`) bắt buộc có `customer_email` trước khi thực thi.

---

### ✅ A-2 — Race Condition khi reload FAISS index dưới concurrent requests

**File:** `app/rag/vector_store.py`

**Đã sửa:** `LocalFaissStore` có `self._lock = threading.Lock()`. Cả `reload()` và `search()` đều dùng `with self._lock:` để đảm bảo thread safety.

---

### ✅ A-3 — PII bị ghi vào log không cần thiết

**File:** `app/agent/orchestrator.py`

**Đã sửa:** Xóa `"retrieved_context_preview": contexts[:2]` khỏi `write_log("chat_request", ...)` và xóa `"context_state": context_state` khỏi `write_log("chat_response", ...)` sau tool call. Log chỉ ghi metadata (count, query, latency).

---

### ✅ A-4 — `__import__("os")` inline trong production code

**File:** `app/rag/vector_store.py`

**Đã sửa:** Dùng `from pathlib import Path` và `Path(...)` thay thế hoàn toàn.

---

## B) Hiệu năng / Tốc độ xử lý

### ✅ B-1 — Lazy init Embedding Model không thread-safe

**File:** `app/rag/retriever.py`

**Đã sửa:** `get_embedding_model()` dùng double-check locking với `threading.Lock()` — chỉ khởi tạo model một lần dù có nhiều thread đồng thời.

---

### ✅ B-2 — Duplicate lookup trong `ingest_folder`

**File:** `app/rag/ingest.py`

**Đã sửa:** `_get_chunk_config` trả về `tuple[dict, str]` — một lần lookup cho cả config lẫn chunk_type.

---

### 🟡 B-3 — `astype("float32")` tạo copy array trên mỗi search request

**File:** `app/rag/vector_store.py:55` và `retriever.py:27`

`query_embedding.astype("float32")` luôn tạo một array mới kể cả khi array đã là float32. Nên normalize sớm tại điểm embedding để tránh copy trong hot path.

```python
# Trong embed_texts (retriever.py) — đảm bảo output luôn là float32
def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True).astype("float32")

# Trong vector_store.search — bỏ astype vì đã đảm bảo từ nguồn
distances, indices = self.index.search(query_embedding, top_k)
```

---

### 🟡 B-4 — Blocking `time.sleep` trong retry loop của Gemini client

**File:** `app/agent/orchestrator.py`

`time.sleep(1.5 * (attempt + 1))` block toàn bộ thread. Trong môi trường async (FastAPI/asyncio), đây sẽ block event loop. Nên dùng `asyncio.sleep` nếu migrate sang async, hoặc ít nhất document rõ đây là synchronous-only.

---

## C) Clean Code / Cấu trúc

### ✅ C-1 — `orchestrator.py` vi phạm Single Responsibility

**Đã sửa:** Tách thành 4 module riêng biệt:

```
app/agent/
├── orchestrator.py       # chat_with_agent() — điều phối luồng chạy
├── context_manager.py    # copy_context, update_context_*, trim_history, _extract_key_facts
├── prompt_builder.py     # build_user_message, build_reference_hint, build_retrieval_query
├── tool_runner.py        # run_tool, tool_declarations
└── small_talk.py         # get_small_talk_answer, normalize_simple
```

---

### ✅ C-2 — DRY violation: `_default_context` định nghĩa 2 lần

**Đã sửa:** `DEFAULT_CONTEXT` được export từ `memory.py` làm source of truth. `orchestrator.py` (nay `context_manager.py`) import và dùng lại.

---

### ✅ C-3 — Magic number `8` trong `normalize_answer`

**File:** `app/agent/orchestrator.py`

**Đã sửa:** Đặt hằng số `MIN_MEANINGFUL_RESPONSE_LEN = 8` ở đầu file.

---

### 🟡 C-4 — `print()` trong production code

**File:** `app/rag/ingest.py:103, 119-121`

Nên thay bằng `logging.info()` để có thể điều chỉnh log level mà không sửa code.

```python
import logging
logger = logging.getLogger(__name__)

logger.info("  %s: %d chunks [%s, size=%d, overlap=%d]",
            file_path.name, len(chunks), chunk_type,
            cfg["chunk_size"], cfg["overlap"])
```

---

### ✅ C-5 — Hardcoded string `"2 đơn"` trong logic nghiệp vụ

**File:** `app/agent/prompt_builder.py`

**Đã sửa:** Dùng `FOLLOW_MULTI_ORDER_PATTERN = re.compile(r"(trong các đơn|các đơn|những đơn|\d+\s*đơn|hai đơn|nhiều đơn)", re.IGNORECASE)` thay cho chuỗi hardcode. Agent giờ nhận đúng "3 đơn", "4 đơn", "nhiều đơn", v.v.

---

### 🟡 C-6 — Module-level singleton `session_store` khó test

**File:** `app/agent/memory.py:70`

`session_store = InMemorySessionStore()` ở module level làm cho unit test phải patch module, không thể inject mock. Nên chuyển việc khởi tạo sang `streamlit_app.py`.

---

## Danh sách ưu tiên sửa

| Ưu tiên | ID  | Mô tả ngắn                                 | File                          | Trạng thái |
| ------- | --- | ------------------------------------------ | ----------------------------- | ---------- |
| 1       | A-1 | Whitelist tool + validate destructive args | tool_runner.py                | ✅ Done    |
| 2       | A-2 | Lock cho FAISS reload/search               | vector_store.py               | ✅ Done    |
| 3       | B-1 | Thread-safe lazy init model                | retriever.py                  | ✅ Done    |
| 4       | A-3 | Bỏ PII khỏi log                            | orchestrator.py               | ✅ Done    |
| 5       | C-2 | Hợp nhất DEFAULT_CONTEXT                   | memory.py + context_manager.py | ✅ Done    |
| 6       | A-4 | Thay `__import__("os")` bằng pathlib       | vector_store.py               | ✅ Done    |
| 7       | B-2 | Bỏ duplicate lookup trong ingest           | ingest.py                     | ✅ Done    |
| 8       | C-1 | Tách orchestrator.py thành modules nhỏ     | app/agent/ (4 modules mới)    | ✅ Done    |
| 9       | C-5 | Regex thay hardcode "2 đơn"                | prompt_builder.py             | ✅ Done    |
| 10      | C-3 | Hằng số MIN_MEANINGFUL_RESPONSE_LEN        | orchestrator.py               | ✅ Done    |
| —       | B-3 | `astype("float32")` tạo copy không cần     | vector_store.py, retriever.py | 🟡 Backlog |
| —       | B-4 | Blocking sleep trong retry Gemini          | orchestrator.py               | 🟡 Backlog |
| —       | C-4 | `print()` → `logging.info()`               | ingest.py                     | 🟡 Backlog |
| —       | C-6 | Module-level singleton session_store       | memory.py                     | 🟡 Backlog |
