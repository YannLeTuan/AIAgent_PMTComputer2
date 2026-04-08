"""
Tests cho A-2 (thread safety reload/search) và A-4 (pathlib thay __import__("os")).
"""
import concurrent.futures
import os
import tempfile

import numpy as np
import pytest


def _build_store(index_path: str):
    """Tạo LocalFaissStore với 5 embeddings giả, dim=8."""
    from app.rag.vector_store import LocalFaissStore
    rng = np.random.default_rng(42)
    embs = rng.random((5, 8)).astype("float32")
    embs /= np.linalg.norm(embs, axis=1, keepdims=True)
    docs = [f"doc_{i}" for i in range(5)]
    store = LocalFaissStore(index_path)
    store.build(embs, docs)
    store.save()
    return store, embs


# ---------------------------------------------------------------------------
# A-4: FileNotFoundError có message rõ ràng khi index chưa build
# ---------------------------------------------------------------------------
def test_load_raises_file_not_found_with_clear_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        from app.rag.vector_store import LocalFaissStore
        store = LocalFaissStore(os.path.join(tmpdir, "nonexistent"))
        with pytest.raises(FileNotFoundError, match="ingest_folder"):
            store.load()


# ---------------------------------------------------------------------------
# A-2: reload() rồi search() ngay sau đó vẫn trả kết quả hợp lệ (sequential)
# ---------------------------------------------------------------------------
def test_reload_then_search_returns_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))
        store.reload()
        results = store.search(embs[0:1], top_k=3)
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)


# ---------------------------------------------------------------------------
# A-2: concurrent reload + search không raise exception
# ---------------------------------------------------------------------------
def test_concurrent_reload_and_search_does_not_raise():
    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))
        query = embs[0:1]
        errors = []

        def do_reload():
            try:
                store.reload()
            except Exception as e:
                errors.append(("reload", type(e).__name__, str(e)))

        def do_search():
            try:
                store.search(query, top_k=2)
            except Exception as e:
                errors.append(("search", type(e).__name__, str(e)))

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = [
                ex.submit(do_reload if i % 3 == 0 else do_search)
                for i in range(24)
            ]
            concurrent.futures.wait(futs)

        assert errors == [], f"Lỗi trong concurrent access: {errors}"


# ---------------------------------------------------------------------------
# A-2: index và documents luôn đồng bộ sau reload (không mismatch)
# ---------------------------------------------------------------------------
def test_index_and_documents_stay_in_sync_after_reload():
    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))
        for _ in range(5):
            store.reload()
            results = store.search(embs[0:1], top_k=2)
            assert len(results) <= store.index.ntotal


# ---------------------------------------------------------------------------
# A-2: LocalFaissStore phải có threading.Lock để bảo vệ reload/search
# ---------------------------------------------------------------------------
def test_store_has_threading_lock():
    """
    Kiểm tra cấu trúc phòng thủ: store phải expose _lock để đảm bảo
    reload() và search() không xung đột khi chạy đồng thời.
    Nếu không có lock, concurrent reload + search có thể trả về
    index/documents không đồng bộ.
    """
    import threading
    from app.rag.vector_store import LocalFaissStore
    store = LocalFaissStore("dummy_path")
    assert hasattr(store, "_lock"), (
        "LocalFaissStore thiếu _lock — cần thêm threading.Lock() trong __init__"
    )
    assert isinstance(store._lock, type(threading.Lock())), (
        "_lock phải là threading.Lock"
    )


# ---------------------------------------------------------------------------
# A-2: faiss.read_index chỉ được gọi đúng 1 lần dù nhiều thread search đồng thời
# ---------------------------------------------------------------------------
def test_concurrent_searches_read_index_exactly_once():
    """
    Không có lock → faiss.read_index bị gọi N lần (race).
    Có lock (double-check) → chỉ gọi 1 lần.
    """
    import threading
    import faiss as _faiss
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))

        # Reset về trạng thái chưa load
        store._loaded = False
        store.index = None
        store.documents = []

        read_count = [0]
        original_read = _faiss.read_index
        barrier = threading.Barrier(6)

        def counting_read(path):
            read_count[0] += 1
            return original_read(path)

        with patch("app.rag.vector_store.faiss.read_index", side_effect=counting_read):
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
                futs = [
                    ex.submit(lambda: (barrier.wait(), store.search(embs[0:1], top_k=2)))
                    for _ in range(6)
                ]
                concurrent.futures.wait(futs)

        assert read_count[0] == 1, (
            f"faiss.read_index bị gọi {read_count[0]} lần thay vì 1 — "
            "threading.Lock chưa bảo vệ đúng trong load()"
        )
