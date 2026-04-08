# Code Review: Module RAG & Agent

**Phạm vi:** `app/rag/` (ingest.py, vector_store.py, retriever.py) và `app/agent/` (orchestrator.py, memory.py)
**Ngày:** 2026-04-08
**Tiêu chí:** (A) Lỗ hổng bảo mật / Bugs ẩn · (B) Hiệu năng · (C) Clean Code

---

## Tóm tắt điểm nghiêm trọng

| Mức | Số lượng |
|-----|----------|
| 🔴 Critical | 2 |
| 🟠 Important | 5 |
| 🟡 Minor | 6 |

---

## A) Lỗ hổng Bảo mật / Bugs ẩn

### 🔴 A-1 — Prompt Injection → Tool Abuse không kiểm soát
**File:** `app/agent/orchestrator.py:571`

LLM có toàn quyền điều khiển `fc.name` và `fc.args`. Nếu model bị jailbreak, nó có thể gọi `cancel_order` hoặc `cancel_multiple_orders` với args tùy ý mà không có bất kỳ kiểm tra phân quyền nào ở tầng orchestrator.

```python
# Hiện tại — không an toàn
tool_result = run_tool(fc.name, args)

# Đề xuất — whitelist tên tool + validate args schema tối thiểu
ALLOWED_TOOLS = {
    "check_order_status", "search_product", "list_products",
    "get_product_details", "build_pc_config", "check_compatibility",
    "get_customer_orders", "cancel_order", "cancel_multiple_orders",
}

DESTRUCTIVE_TOOLS = {"cancel_order", "cancel_multiple_orders"}

def run_tool(name: str, args: dict):
    if name not in ALLOWED_TOOLS:
        return {"success": False, "message": f"Tool '{name}' không được phép gọi."}
    if name in DESTRUCTIVE_TOOLS:
        # Bắt buộc phải có customer_email trước khi thực thi
        if not args.get("customer_email"):
            return {"success": False, "message": "Thiếu customer_email để xác thực."}
    dispatch = { ... }
    fn = dispatch.get(name)
    return fn(**args)
```

---

### 🔴 A-2 — Race Condition khi reload FAISS index dưới concurrent requests
**File:** `app/rag/vector_store.py:44-46`

`reload()` set `_loaded = False` rồi gọi `load()`. Nếu 2 thread cùng gọi `search()` trong khoảng giữa hai bước đó, `self.index` sẽ là `None` khi một thread search, dẫn đến `AttributeError`.

```python
# Đề xuất — dùng threading.Lock
import threading

class LocalFaissStore:
    def __init__(self, index_path: str):
        ...
        self._lock = threading.Lock()

    def reload(self):
        with self._lock:
            self._loaded = False
            self.load()

    def search(self, query_embedding, top_k=4):
        with self._lock:
            if not self._loaded:
                self.load()
            if self.index is None or len(self.documents) == 0:
                return []
            distances, indices = self.index.search(
                query_embedding.astype("float32"), top_k
            )
        ...
```

---

### 🟠 A-3 — PII bị ghi vào log không cần thiết
**File:** `app/agent/orchestrator.py:510-518`

`retrieved_context_preview: contexts[:2]` log nội dung chunk tài liệu thô. Nếu chunk chứa dữ liệu nhạy cảm (email, SĐT), sẽ bị ghi vào file log vĩnh viễn. Tương tự, `context_state` được log ở dòng 616 có thể chứa `last_customer_email`.

```python
# Đề xuất — chỉ log metadata, không log nội dung
write_log("chat_request", {
    "thread_id": thread_id,
    "user_message": user_message,
    "retrieval_query": retrieval_query,
    "history_size": len(history),
    "retrieved_context_count": len(contexts),
    # Xóa: "retrieved_context_preview": contexts[:2]
})

# Ở chat_response, xóa context_state khỏi log hoặc mask email
write_log("chat_response", {
    ...
    # "context_state": context_state  ← xóa dòng này
})
```

---

### 🟠 A-4 — `__import__("os")` inline trong production code
**File:** `app/rag/vector_store.py:31`

`__import__("os")` là antipattern, khó đọc và có thể bị linter bỏ qua khi kiểm tra dependencies. Không phải lỗ hổng bảo mật trực tiếp nhưng làm mờ bề mặt tấn công khi audit.

```python
# Hiện tại
if not __import__("os").path.exists(faiss_path) or not __import__("os").path.exists(json_path):

# Đề xuất — dùng pathlib (đã import sẵn ở ingest.py, nhất quán hơn)
from pathlib import Path

def load(self):
    if self._loaded:
        return
    faiss_path = Path(self.index_path + ".faiss")
    json_path = Path(self.index_path + ".json")
    if not faiss_path.exists() or not json_path.exists():
        raise FileNotFoundError(...)
```

---

## B) Hiệu năng / Tốc độ xử lý

### 🟠 B-1 — Lazy init Embedding Model không thread-safe
**File:** `app/rag/retriever.py:11-15`

`get_embedding_model()` dùng double-check pattern không có lock. Dưới Streamlit multi-thread (hoặc FastAPI), hai request đồng thời có thể khởi tạo `SentenceTransformer` hai lần — tốn ~2GB RAM.

```python
import threading
_model = None
_model_lock = threading.Lock()

def get_embedding_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # double-check sau khi có lock
                _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model
```

---

### 🟠 B-2 — Duplicate lookup trong `ingest_folder`
**File:** `app/rag/ingest.py:99-102`

`_get_chunk_config` đã loop qua `_FILENAME_CHUNK_TYPE` ở dòng 97. Ngay sau đó, dòng 99-102 lại loop lần nữa chỉ để lấy `chunk_type` để print. Với nhiều file, đây là O(2n) không cần thiết.

```python
# Đề xuất — trả về cả config lẫn chunk_type từ một hàm
def _get_chunk_config(file_path: Path) -> tuple[dict, str]:
    stem = file_path.stem
    for key, chunk_type in _FILENAME_CHUNK_TYPE.items():
        if key in stem:
            return _CHUNK_CONFIG[chunk_type], chunk_type
    return _CHUNK_CONFIG["standard"], "standard"

# Trong ingest_folder:
cfg, chunk_type = _get_chunk_config(file_path)
chunks = split_text(raw_text, chunk_size=cfg["chunk_size"], overlap=cfg["overlap"])
print(f"  {file_path.name}: {len(chunks)} chunks [{chunk_type}, ...]")
```

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
**File:** `app/agent/orchestrator.py:470-472`

`time.sleep(1.5 * (attempt + 1))` block toàn bộ thread. Trong môi trường async (FastAPI/asyncio), đây sẽ block event loop. Nên dùng `asyncio.sleep` nếu migrate sang async, hoặc ít nhất document rõ đây là synchronous-only.

---

## C) Clean Code / Cấu trúc

### 🟠 C-1 — `orchestrator.py` vi phạm Single Responsibility (633 dòng)
**File:** `app/agent/orchestrator.py`

File này đang làm 5 việc khác nhau: quản lý context, xây dựng prompt, gọi Gemini, xử lý tool, và small talk. Đề xuất tách thành:

```
app/agent/
├── orchestrator.py       # chỉ còn chat_with_agent() — điều phối
├── context_manager.py    # copy_context, update_context_*, trim_history, _extract_key_facts
├── prompt_builder.py     # build_user_message, build_reference_hint, build_retrieval_query
├── tool_runner.py        # run_tool, tool_declarations
└── small_talk.py         # get_small_talk_answer, normalize_simple
```

---

### 🟠 C-2 — DRY violation: `_default_context` định nghĩa 2 lần
**File:** `app/agent/memory.py:15-23` và `app/agent/orchestrator.py:283-300`

Cấu trúc context dict được hardcode ở cả hai file. Nếu thêm field mới (ví dụ `last_sku`), phải sửa 2 chỗ.

```python
# Đề xuất — đặt tại memory.py làm source of truth
DEFAULT_CONTEXT: dict = {
    "last_order_code": None,
    "last_product_name": None,
    "last_customer_email": None,
    "last_customer_name": None,
    "last_order_codes": [],
    "context_summary": ""
}

# orchestrator.py:copy_context — import và dùng lại
from app.agent.memory import DEFAULT_CONTEXT

def copy_context(context_state: dict | None) -> dict:
    base = DEFAULT_CONTEXT.copy()
    if context_state:
        for k in base:
            if k in context_state:
                base[k] = context_state[k]
    return base
```

---

### 🟡 C-3 — Magic number `8` trong `normalize_answer`
**File:** `app/agent/orchestrator.py:198`

`if len(text) < 8` không có giải thích. Nên đặt thành hằng số có tên.

```python
MIN_MEANINGFUL_RESPONSE_LEN = 8  # ít hơn 8 ký tự = câu trả lời không có ý nghĩa

def normalize_answer(text: str):
    ...
    if len(text) < MIN_MEANINGFUL_RESPONSE_LEN:
        return "Hiện tôi chưa có đủ thông tin..."
```

---

### 🟡 C-4 — `print()` trong production code
**File:** `app/rag/ingest.py:103, 119-121`

Nên thay bằng `logging.info()` để có thể điều chỉnh log level mà không sửa code.

```python
import logging
logger = logging.getLogger(__name__)

# Thay print(...) bằng:
logger.info("  %s: %d chunks [%s, size=%d, overlap=%d]",
            file_path.name, len(chunks), chunk_type,
            cfg["chunk_size"], cfg["overlap"])
```

---

### 🟡 C-5 — Hardcoded string `"2 đơn"` trong logic nghiệp vụ
**File:** `app/agent/orchestrator.py:370`

```python
if ("trong các đơn đó" in lower or "2 đơn" in lower or ...):
```

String `"2 đơn"` là brittle — người dùng có thể viết "hai đơn", "3 đơn", "nhiều đơn". Nên mở rộng hoặc dùng regex.

```python
FOLLOW_MULTI_ORDER_PATTERN = re.compile(
    r"(trong các đơn|các đơn|những đơn|\d+ đơn|hai đơn|nhiều đơn)", re.IGNORECASE
)

# Trong build_reference_hint:
if FOLLOW_MULTI_ORDER_PATTERN.search(lower) and context_state.get("last_order_codes"):
    ...
```

---

### 🟡 C-6 — Module-level singleton `session_store` khó test
**File:** `app/agent/memory.py:68`

`session_store = InMemorySessionStore()` ở module level làm cho unit test phải patch module, không thể inject mock.

```python
# Đề xuất — dùng dependency injection ở tầng gọi (streamlit_app.py hoặc router)
# memory.py chỉ export class, không tạo instance
# Ở streamlit_app.py:
from app.agent.memory import InMemorySessionStore
session_store = InMemorySessionStore()
```

---

## Danh sách ưu tiên sửa

| Ưu tiên | ID | Mô tả ngắn | File |
|---------|----|------------|------|
| 1 | A-1 | Whitelist tool + validate destructive args | orchestrator.py:571 |
| 2 | A-2 | Lock cho FAISS reload/search | vector_store.py:44 |
| 3 | B-1 | Thread-safe lazy init model | retriever.py:11 |
| 4 | A-3 | Bỏ PII khỏi log | orchestrator.py:510-518 |
| 5 | C-2 | Hợp nhất DEFAULT_CONTEXT | memory.py + orchestrator.py |
| 6 | A-4 | Thay `__import__("os")` bằng pathlib | vector_store.py:31 |
| 7 | B-2 | Bỏ duplicate lookup trong ingest | ingest.py:99 |
| 8 | C-1 | Tách orchestrator.py thành modules nhỏ | orchestrator.py |
