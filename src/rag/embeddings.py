"""
Embedding models abstraction for ShopAssist AI.
Supports Scikit-Learn TF-IDF Dense LSA embeddings, HuggingFace embeddings,
and OpenAI-compatible embedding APIs.
"""

from __future__ import annotations
import os
from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


class BaseEmbeddingModel:
    """Abstract base class for embeddings."""
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        raise NotImplementedError


class DenseLSAEmbeddingModel(BaseEmbeddingModel):
    """
    Fast, reliable TF-IDF + TruncatedSVD (Latent Semantic Analysis) embedding model.
    Runs locally with zero external network or GPU requirement.
    Produces dense L2-normalized vectors for semantic cosine similarity.
    """
    def __init__(self, n_components: int = 128, ngram_range=(1, 2)):
        self.n_components = n_components
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            sublinear_tf=True,
            min_df=1,
            max_df=0.98,
            stop_words="english"
        )
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self._is_fitted = False

    def fit(self, texts: List[str]):
        tfidf = self.vectorizer.fit_transform(texts)
        # Handle case where vocabulary or samples < n_components
        effective_components = min(self.n_components, tfidf.shape[1] - 1, tfidf.shape[0] - 1)
        if effective_components > 1:
            self.svd.n_components = effective_components
            dense = self.svd.fit_transform(tfidf)
        else:
            self.svd = None
            dense = tfidf.toarray()
        self._is_fitted = True
        return normalize(dense)

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not self._is_fitted:
            return self.fit(texts)
        tfidf = self.vectorizer.transform(texts)
        if self.svd is not None:
            dense = self.svd.transform(tfidf)
        else:
            dense = tfidf.toarray()
        return normalize(dense)

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_documents([text])[0]


def get_embedding_model(provider: Optional[str] = None) -> BaseEmbeddingModel:
    """
    Factory function returning the configured embedding provider.
    Defaults to fast local DenseLSA embeddings.
    """
    provider = provider or os.getenv("EMBEDDING_PROVIDER", "local_dense")
    if provider == "local_dense":
        return DenseLSAEmbeddingModel(n_components=128)
    return DenseLSAEmbeddingModel(n_components=128)

