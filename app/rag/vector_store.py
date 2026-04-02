import pickle

import faiss
import numpy as np


class LocalFaissStore:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = None
        self.documents = []

    def build(self, embeddings: np.ndarray, documents: list[str]):
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype("float32"))
        self.documents = documents

    def save(self):
        faiss.write_index(self.index, self.index_path + ".faiss")
        with open(self.index_path + ".pkl", "wb") as f:
            pickle.dump(self.documents, f)

    def load(self):
        self.index = faiss.read_index(self.index_path + ".faiss")
        with open(self.index_path + ".pkl", "rb") as f:
            self.documents = pickle.load(f)

    def search(self, query_embedding: np.ndarray, top_k: int = 4):
        distances, indices = self.index.search(query_embedding.astype("float32"), top_k)

        results = []
        for idx in indices[0]:
            if idx != -1:
                results.append(self.documents[idx])

        return results