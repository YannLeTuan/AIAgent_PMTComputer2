import concurrent.futures
import os
import tempfile

import numpy as np
import pytest


def _build_store(index_path: str):
    from app.rag.vector_store import LocalFaissStore
    rng = np.random.default_rng(42)
    embs = rng.random((5, 8)).astype("float32")
    embs /= np.linalg.norm(embs, axis=1, keepdims=True)
    docs = [f"doc_{i}" for i in range(5)]
    store = LocalFaissStore(index_path)
    store.build(embs, docs)
    store.save()
    return store, embs


def test_load_raises_file_not_found_with_clear_message():
    with tempfile.TemporaryDirectory() as tmpdir:
        from app.rag.vector_store import LocalFaissStore
        store = LocalFaissStore(os.path.join(tmpdir, "nonexistent"))
        with pytest.raises(FileNotFoundError, match="ingest_folder"):
            store.load()


def test_reload_then_search_returns_results():
    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))
        store.reload()
        results = store.search(embs[0:1], top_k=3)
        assert len(results) == 3
        assert all(isinstance(r, str) for r in results)


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


def test_index_and_documents_stay_in_sync_after_reload():
    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))
        for _ in range(5):
            store.reload()
            results = store.search(embs[0:1], top_k=2)
            assert len(results) <= store.index.ntotal


def test_store_has_threading_lock():
    import threading
    from app.rag.vector_store import LocalFaissStore
    store = LocalFaissStore("dummy_path")
    assert hasattr(store, "_lock"), (
        "LocalFaissStore thiếu _lock — cần thêm threading.Lock() trong __init__"
    )
    assert isinstance(store._lock, type(threading.Lock())), (
        "_lock phải là threading.Lock"
    )


def test_concurrent_searches_read_index_exactly_once():
    import threading
    import faiss as _faiss
    from unittest.mock import patch

    with tempfile.TemporaryDirectory() as tmpdir:
        store, embs = _build_store(os.path.join(tmpdir, "idx"))

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
