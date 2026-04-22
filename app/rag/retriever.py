import numpy as np
from google import genai

from app.core.config import settings
from app.rag.vector_store import LocalFaissStore

_client = genai.Client(api_key=settings.GEMINI_API_KEY)
store = LocalFaissStore(settings.VECTOR_INDEX_PATH)

_EMBED_MODEL = "gemini-embedding-001"
_BATCH_SIZE = 50


def embed_texts(texts: list[str]) -> np.ndarray:
    all_vecs = []
    for i in range(0, len(texts), _BATCH_SIZE):
        batch = texts[i: i + _BATCH_SIZE]
        resp = _client.models.embed_content(
            model=_EMBED_MODEL,
            contents=batch,
        )
        all_vecs.extend([e.values for e in resp.embeddings])
    return np.array(all_vecs, dtype="float32")


def retrieve_context(query: str, top_k: int = 4) -> list[str]:
    resp = _client.models.embed_content(
        model=_EMBED_MODEL,
        contents=[query],
    )
    query_vec = np.array([resp.embeddings[0].values], dtype="float32")
    return store.search(query_vec, top_k=top_k)