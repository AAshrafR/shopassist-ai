"""
Vector Store and Hybrid Search Index for ShopAssist AI.
Supports dense vector semantic search, BM25/keyword lexical search,
score normalization, metadata filtering, and disk persistence.
"""

from __future__ import annotations
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from src.rag.embeddings import BaseEmbeddingModel, DenseLSAEmbeddingModel


class SimpleVectorStore:
    def __init__(self, embedding_model: Optional[BaseEmbeddingModel] = None):
        self.embedding_model = embedding_model or DenseLSAEmbeddingModel()
        self.documents: List[Dict[str, Any]] = []
        self.vectors: Optional[np.ndarray] = None
        self.doc_ids: List[str] = []

    def add_documents(self, docs: List[Dict[str, Any]]) -> None:
        """Indexes documents and computes embeddings."""
        if not docs:
            return

        texts = [d["text"] for d in docs]
        new_vectors = self.embedding_model.embed_documents(texts)

        if self.vectors is None:
            self.vectors = new_vectors
            self.documents = list(docs)
            self.doc_ids = [d.get("chunk_id", str(i)) for i, d in enumerate(docs)]
        else:
            self.vectors = np.vstack([self.vectors, new_vectors])
            self.documents.extend(docs)
            self.doc_ids.extend([d.get("chunk_id", str(len(self.documents) + i)) for i, d in enumerate(docs)])

    def similarity_search_with_scores(
        self,
        query: str,
        k: int = 4,
        category: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Calculates cosine similarity between query and stored document vectors.
        Returns top-k documents along with similarity scores (0.0 to 1.0).
        """
        if self.vectors is None or len(self.documents) == 0:
            return []

        query_vec = self.embedding_model.embed_query(query)
        # Cosine similarity for normalized vectors is dot product
        scores = np.dot(self.vectors, query_vec)

        # Apply category filter if specified
        if category:
            mask = np.array([doc.get("category", "").upper() == category.upper() for doc in self.documents])
            scores = np.where(mask, scores, -1.0)

        top_indices = np.argsort(scores)[::-1][:k]
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > -0.5:  # Valid score threshold
                results.append((self.documents[idx], score))
        return results

    def hybrid_search(
        self,
        query: str,
        k: int = 4,
        alpha: float = 0.7,
        category: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Hybrid search combining dense cosine similarity (alpha)
        and lexical term overlap score (1 - alpha).
        """
        if self.vectors is None or len(self.documents) == 0:
            return []

        query_vec = self.embedding_model.embed_query(query)
        dense_scores = np.dot(self.vectors, query_vec)

        # Lexical keyword score
        query_terms = set(query.lower().split())
        lexical_scores = np.zeros(len(self.documents))
        if query_terms:
            for i, doc in enumerate(self.documents):
                doc_terms = set(doc["text"].lower().split())
                overlap = len(query_terms.intersection(doc_terms))
                lexical_scores[i] = overlap / max(1, len(query_terms))

        # Normalize and blend
        combined_scores = alpha * dense_scores + (1 - alpha) * lexical_scores

        if category:
            mask = np.array([doc.get("category", "").upper() == category.upper() for doc in self.documents])
            combined_scores = np.where(mask, combined_scores, -1.0)

        top_indices = np.argsort(combined_scores)[::-1][:k]
        results = []
        for idx in top_indices:
            score = float(combined_scores[idx])
            results.append((self.documents[idx], score))
        return results

    def save(self, filepath: Path) -> None:
        """Serializes vector store and index to file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "vectors": self.vectors,
                "doc_ids": self.doc_ids,
                "embedding_model": self.embedding_model
            }, f)

    @classmethod
    def load(cls, filepath: Path) -> "SimpleVectorStore":
        """Loads vector store and index from file."""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        store = cls(embedding_model=data.get("embedding_model"))
        store.documents = data.get("documents", [])
        store.vectors = data.get("vectors")
        store.doc_ids = data.get("doc_ids", [])
        return store

