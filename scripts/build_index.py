"""
Build and save the vector search index for ShopAssist AI.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import time
from src.rag.chunker import TextChunker
from src.rag.vector_store import SimpleVectorStore
KB_CHUNKS_FILE = BASE_DIR / "data" / "processed" / "knowledge_base_chunks.json"
INDEX_FILE = BASE_DIR / "data" / "processed" / "vector_index.pkl"


def build_and_save_index():
    print(f"Loading knowledge base chunks from {KB_CHUNKS_FILE}...")
    start_t = time.time()
    with open(KB_CHUNKS_FILE, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)

    chunker = TextChunker(chunk_size=600, chunk_overlap=80)
    split_chunks = []
    for doc in raw_chunks:
        split_chunks.extend(chunker.split_document(doc))

    print(f"Chunking finished: {len(raw_chunks)} raw docs -> {len(split_chunks)} semantic chunks.")

    store = SimpleVectorStore()
    print("Computing embeddings and indexing vectors...")
    store.add_documents(split_chunks)

    store.save(INDEX_FILE)
    elapsed = time.time() - start_t
    print(f"Successfully saved index to {INDEX_FILE} ({len(split_chunks)} documents, {elapsed:.2f}s).")


if __name__ == "__main__":
    build_and_save_index()
