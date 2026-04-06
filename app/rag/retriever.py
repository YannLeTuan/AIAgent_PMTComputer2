import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.rag.vector_store import LocalFaissStore

_model = None
store = LocalFaissStore(settings.VECTOR_INDEX_PATH)


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    return np.array(
        model.encode(texts, normalize_embeddings=True)
    )


def retrieve_context(query: str, top_k: int = 4) -> list[str]:
    model = get_embedding_model()
    query_vec = np.array([
        model.encode(query, normalize_embeddings=True)
    ])
    return store.search(query_vec, top_k=top_k)