import json

import faiss
import numpy as np


class LocalFaissStore:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = None
        self.documents: list[str] = []
        self._loaded = False

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
        if self._loaded:
            return
        self.index = faiss.read_index(self.index_path + ".faiss")
        with open(self.index_path + ".json", "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        self._loaded = True

    def reload(self):
        """Force reload từ disk (dùng sau khi ingest lại)."""
        self._loaded = False
        self.load()

    def search(self, query_embedding: np.ndarray, top_k: int = 4):
        if not self._loaded:
            self.load()

        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.documents[idx])

        return results