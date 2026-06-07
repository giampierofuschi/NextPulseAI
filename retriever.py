import os
import pickle
import faiss

from sentence_transformers import SentenceTransformer


class Retriever:

    def __init__(self, persist_dir="storage_index"):

        self.persist_dir = persist_dir

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.index = faiss.read_index(
            os.path.join(persist_dir, "faiss.index")
        )

        with open(os.path.join(persist_dir, "metadata.pkl"), "rb") as f:
            self.metadata = pickle.load(f)

    # ─────────────────────────────
    # SEARCH
    # ─────────────────────────────

    def search(self, query, top_k=5):

        q_emb = self.model.encode([query]).astype("float32")

        scores, indices = self.index.search(q_emb, top_k)

        results = []

        for rank, idx in enumerate(indices[0]):

            if idx < 0:
                continue

            meta = self.metadata[idx]

            # Normalizzazione della distanza L2 in uno score di rilevanza (0-1)
            # Valori più vicini a 1.0 indicano una similarità maggiore
            raw_distance = float(scores[0][rank])
            normalized_score = 1 / (1 + raw_distance)

            results.append({
                "score": normalized_score,
                "file_name": meta.get("file_name", ""),
                "file_path": meta.get("file_path", ""),
                "chunk_id": meta.get("chunk_id", -1),
                "text": meta.get("text", "")
            })

        return results