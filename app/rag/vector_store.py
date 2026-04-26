import json
import threading
from pathlib import Path

import faiss
import numpy as np


class LocalFaissStore:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = None
        self.documents: list[str] = []
        self._loaded = False
        self._lock = threading.Lock()

    def build(self, embeddings: np.ndarray, documents: list[str]):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype("float32"))
        self.documents = documents
        self._loaded = True

    def save(self):
        faiss.write_index(self.index, self.index_path + ".faiss")
        with open(self.index_path + ".json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False)

    def load(self):
        with self._lock:
            if self._loaded:
                return
            faiss_path = Path(self.index_path + ".faiss")
            json_path = Path(self.index_path + ".json")
            if not faiss_path.exists() or not json_path.exists():
                raise FileNotFoundError(
                    f"Vector index files not found: {faiss_path} / {json_path}. "
                    "Run ingest_folder() to build the index first."
                )
            index = faiss.read_index(str(faiss_path))
            with open(json_path, "r", encoding="utf-8") as f:
                documents = json.load(f)
            self.index = index
            self.documents = documents
            self._loaded = True

    def reload(self):
        with self._lock:
            self._loaded = False
        self.load()

    def search(self, query_embedding: np.ndarray, top_k: int = 4):
        if not self._loaded:
            self.load()

        with self._lock:
            if self.index is None or len(self.documents) == 0:
                return []
            distances, indices = self.index.search(query_embedding.astype("float32"), top_k)
            docs_snapshot = self.documents
            n_docs = len(docs_snapshot)

        results = []
        for idx in indices[0]:
            if 0 <= idx < n_docs:
                results.append(docs_snapshot[idx])

        return results