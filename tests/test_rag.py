"""
Unit tests for RAG pipeline, chunker, and vector store.
"""

import pytest
from src.rag.chunker import TextChunker
from src.rag.vector_store import SimpleVectorStore
from src.rag.pipeline import RAGPipeline


def test_chunker_splitting():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    text = "Sentence one is here. Sentence two is following. Sentence three completes the paragraph."
    chunks = chunker.split_text(text)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) > 0


def test_vector_store_indexing_and_search():
    store = SimpleVectorStore()
    docs = [
        {"chunk_id": "c1", "text": "Our return policy allows 30 days for full refund.", "category": "REFUND", "title": "Return Policy"},
        {"chunk_id": "c2", "text": "Standard ground shipping takes 3 to 5 business days.", "category": "SHIPPING", "title": "Shipping Policy"},
        {"chunk_id": "c3", "text": "We accept major credit cards including Visa and MasterCard.", "category": "PAYMENT", "title": "Payment Policy"}
    ]
    store.add_documents(docs)
    results = store.hybrid_search("how long does standard delivery take?", k=2)
    assert len(results) > 0
    top_doc, score = results[0]
    assert top_doc["category"] == "SHIPPING"


def test_rag_pipeline_end_to_end():
    pipeline = RAGPipeline()
    # Test RAG retrieval query
    res = pipeline.run("What is your return window?")
    assert len(res["answer"]) > 10
    assert len(res["sources"]) > 0
    assert res["latency_ms"] > 0

    # Test tool dispatch query
    res_tool = pipeline.run("Please check order ORD-1002")
    assert res_tool["tool_call"] is not None
    assert res_tool["tool_call"]["tool_name"] == "order_lookup"
    assert "Alex Murphy" in res_tool["answer"]

