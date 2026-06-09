import os
import pickle
import faiss
import numpy as np
import re

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer


class IndexBuilder:

    def __init__(self, data_dir="knowledge", persist_dir="storage_index"):

        self.data_dir = data_dir
        self.persist_dir = persist_dir

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.index_path = os.path.join(persist_dir, "faiss.index")
        self.meta_path = os.path.join(persist_dir, "metadata.pkl")


    def _clean_text(self, text: str) -> str:
        """Pulisce il testo grezzo dai difetti tipici dei PDF."""
        if not text:
            return ""

        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        text = re.sub(r'\s+', ' ', text)

        return text.strip()


    def build(self):

        print("📦 Building knowledge base...")

        docs = SimpleDirectoryReader(
            self.data_dir,
            recursive=True
        ).load_data()

        splitter = SentenceSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        nodes = splitter.get_nodes_from_documents(docs)

        texts = []
        metadata = []

        for i, n in enumerate(nodes):

            # --- APPLICHIAMO LA PULIZIA QUI ---
            raw_text = n.text
            text = self._clean_text(raw_text)

            if len(text) < 50:  # Ignoriamo i chunk troppo corti che contengono solo rumore
                continue

            texts.append(text)

            metadata.append({
                "text": text,
                "file_path": n.metadata.get("file_path", ""),
                "file_name": os.path.basename(n.metadata.get("file_path", "")),
                "chunk_id": i
            })

        embeddings = self.model.encode(texts)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        os.makedirs(self.persist_dir, exist_ok=True)

        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "wb") as f:
            pickle.dump(metadata, f)

        print("Index built successfully")

if __name__ == "__main__":
    builder = IndexBuilder(data_dir="knowledge")
    builder.build()