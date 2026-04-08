"""
Tests cho B-1: get_embedding_model() phải thread-safe (chỉ init SentenceTransformer 1 lần).
"""
import concurrent.futures
import threading
from unittest.mock import patch, MagicMock


def test_get_embedding_model_init_called_once_under_concurrency():
    """
    Không có lock → SentenceTransformer() có thể bị khởi tạo nhiều lần.
    Có lock (double-check) → chỉ khởi tạo đúng 1 lần.
    """
    import app.rag.retriever as retriever_module

    original_model = retriever_module._model
    try:
        retriever_module._model = None  # reset về trạng thái chưa init

        init_count = [0]
        barrier = threading.Barrier(8)

        real_cls = None  # không cần, ta mock hoàn toàn

        def fake_sentence_transformer(model_name):
            import time
            init_count[0] += 1
            time.sleep(0.02)  # Mô phỏng I/O chậm → GIL switch → trigger race
            mock = MagicMock()
            mock.encode = lambda texts, **kw: [[0.0] * 384] * (
                len(texts) if isinstance(texts, list) else 1
            )
            return mock

        with patch("app.rag.retriever.SentenceTransformer", side_effect=fake_sentence_transformer):
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
                futs = [
                    ex.submit(lambda: (barrier.wait(), retriever_module.get_embedding_model()))
                    for _ in range(8)
                ]
                concurrent.futures.wait(futs)

        assert init_count[0] == 1, (
            f"SentenceTransformer() bị khởi tạo {init_count[0]} lần — "
            "get_embedding_model() thiếu threading.Lock"
        )

    finally:
        retriever_module._model = original_model


def test_get_embedding_model_returns_same_instance_always():
    """Mọi lần gọi get_embedding_model() phải trả về cùng một object."""
    import app.rag.retriever as retriever_module
    m1 = retriever_module.get_embedding_model()
    m2 = retriever_module.get_embedding_model()
    assert m1 is m2
