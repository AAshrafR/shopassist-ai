"""
RAG Pipeline and Query Router for ShopAssist AI.
Integrates semantic vector retrieval, policy grounding,
business tool execution (orders & tickets), and LLM response generation.
"""

from __future__ import annotations
import os
import json
import re
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.rag.vector_store import SimpleVectorStore
from src.rag.chunker import TextChunker
from src.tools.order_tool import lookup_order_status, extract_order_id
from src.tools.ticket_tool import create_support_ticket

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INDEX_FILE = BASE_DIR / "data" / "processed" / "vector_index.pkl"
KB_CHUNKS_FILE = BASE_DIR / "data" / "processed" / "knowledge_base_chunks.json"


class RAGPipeline:
    def __init__(self, index_path: Path = INDEX_FILE):
        self.index_path = index_path
        self.vector_store: Optional[SimpleVectorStore] = None
        self._initialize_index()

    def _initialize_index(self):
        """Loads existing index from disk or builds from processed chunks."""
        if self.index_path.exists():
            try:
                self.vector_store = SimpleVectorStore.load(self.index_path)
                print(f"Loaded existing vector index with {len(self.vector_store.documents)} chunks.")
                return
            except Exception as e:
                print(f"Warning: could not load index from {self.index_path}: {e}. Rebuilding...")

        # Build index
        self.vector_store = SimpleVectorStore()
        if KB_CHUNKS_FILE.exists():
            with open(KB_CHUNKS_FILE, "r", encoding="utf-8") as f:
                raw_chunks = json.load(f)
            chunker = TextChunker(chunk_size=600, chunk_overlap=80)
            split_chunks = []
            for doc in raw_chunks:
                split_chunks.extend(chunker.split_document(doc))
            self.vector_store.add_documents(split_chunks)
            self.vector_store.save(self.index_path)
            print(f"Built and saved new vector index with {len(split_chunks)} chunks.")
        else:
            print(f"Warning: {KB_CHUNKS_FILE} does not exist. Index is empty.")

    def retrieve(self, query: str, top_k: int = 4, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant knowledge chunks."""
        if not self.vector_store or not self.vector_store.documents:
            return []
        results = self.vector_store.hybrid_search(query, k=top_k, alpha=0.75, category=category)
        formatted = []
        for doc, score in results:
            formatted.append({
                "chunk_id": doc.get("chunk_id", ""),
                "title": doc.get("title", ""),
                "category": doc.get("category", "GENERAL"),
                "source_type": doc.get("source_type", ""),
                "source_file": doc.get("source_file", ""),
                "score": round(float(score), 4),
                "text": doc.get("text", "")
            })
        return formatted

    def generate_grounded_answer(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Synthesizes a helpful, accurate, grounded response using the retrieved knowledge chunks.
        If an external LLM API key is present (e.g. OPENAI_API_KEY or GEMINI_API_KEY),
        it calls the LLM API; otherwise, it uses grounded extraction from top sources.
        """
        # Check if external LLM provider is requested and configured
        llm_provider = os.getenv("LLM_PROVIDER", "grounded_extractive").lower()
        if llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            try:
                import requests
                headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}", "Content-Type": "application/json"}
                context = "\n\n".join([f"Source [{d['title']}]:\n{d['text']}" for d in retrieved_docs])
                payload = {
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": [
                        {"role": "system", "content": "You are ShopAssist AI, a helpful, polite, and precise customer service assistant for an e-commerce platform. Ground your response firmly in the provided context."},
                        {"role": "user", "content": f"Context:\n{context}\n\nCustomer Inquiry: {query}"}
                    ],
                    "temperature": 0.2
                }
                r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=10)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"External LLM invocation error: {e}. Falling back to grounded synthesizer.")

        # Grounded context synthesizer
        if not retrieved_docs:
            return (
                "I apologize, but I could not find specific information regarding your question in our current knowledge base. "
                "Would you like me to connect you with a human support agent or create a support ticket for further assistance?"
            )

        top_doc = retrieved_docs[0]
        policy_docs = [d for d in retrieved_docs if d.get("source_type") == "policy"]

        # If we have official policy text, prioritize exact policy terms
        if policy_docs:
            primary = policy_docs[0]
            clean_body = primary['text']
            if "]\n" in clean_body:
                clean_body = clean_body.split("]\n", 1)[1].strip()
            answer = f"**{primary['title']}**\n\n{clean_body}"
            if len(policy_docs) > 1 and policy_docs[1]['title'] != primary['title']:
                secondary = policy_docs[1]
                sec_body = secondary['text']
                if "]\n" in sec_body:
                    sec_body = sec_body.split("]\n", 1)[1].strip()
                answer += f"\n\n**Related Policy ({secondary['title']}):**\n{sec_body}"
            return answer

        # Otherwise synthesize from canonical FAQ guidance
        guidance_text = top_doc['text']
        if "Guidance:" in guidance_text:
            guidance_part = guidance_text.split("Guidance:", 1)[1].strip()
            return f"{guidance_part}\n\n*(Reference: {top_doc['title']})*"

        return f"**{top_doc['title']}**:\n\n{top_doc['text']}"

    def run(
        self,
        query: str,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end RAG orchestrator:
        1. Analyzes user intent for business tool triggers (order tracking, ticket opening)
        2. Dispatches business tools if appropriate
        3. Retrieves relevant knowledge chunks via semantic hybrid search
        4. Synthesizes context-grounded response
        5. Returns structured answer, citations, executed tools, and latency
        """
        start_time = time.time()
        executed_tool: Optional[Dict[str, Any]] = None
        answer: str = ""
        citations: List[Dict[str, Any]] = []

        query_lower = query.lower()

        # Tool 1: Order Status Lookup
        order_id = extract_order_id(query)
        order_keywords = ["order", "package", "tracking", "track", "delivery status", "where is"]
        if order_id or any(kw in query_lower for kw in ["my order", "track order", "order status", "track my"]):
            if order_id:
                tool_res = lookup_order_status(order_id)
                executed_tool = {
                    "tool_name": "order_lookup",
                    "status": "success" if tool_res["success"] else "not_found",
                    "parameters": {"order_id": order_id},
                    "result": tool_res
                }
                answer = tool_res["message"]
            else:
                answer = "I would be happy to check your order status! Please provide your order number (for example: ORD-1001)."
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query,
                "answer": answer,
                "sources": [],
                "tool_call": executed_tool,
                "latency_ms": latency_ms
            }

        # Tool 2: Ticket Creation
        ticket_triggers = [
            "open a ticket", "create a ticket", "submit ticket", "support ticket",
            "file a complaint", "damaged item", "file a claim", "contact human"
        ]
        if any(trig in query_lower for trig in ticket_triggers):
            name = customer_name or "ShopAssist Customer"
            email = customer_email or "customer@example.com"
            category = "SUPPORT"
            if "damaged" in query_lower or "defective" in query_lower:
                category = "DAMAGED_ITEM"
            elif "refund" in query_lower:
                category = "REFUND"
            elif "billing" in query_lower or "charge" in query_lower:
                category = "BILLING"

            ticket_res = create_support_ticket(
                customer_name=name,
                customer_email=email,
                subject=f"Inquiry: {query[:50]}...",
                description=query,
                category=category,
                priority="High" if "damaged" in query_lower or "complaint" in query_lower else "Medium"
            )
            executed_tool = {
                "tool_name": "create_support_ticket",
                "status": "success",
                "parameters": {"customer_name": name, "category": category},
                "result": ticket_res
            }
            answer = ticket_res["message"]
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": query,
                "answer": answer,
                "sources": [],
                "tool_call": executed_tool,
                "latency_ms": latency_ms
            }

        # Standard RAG Retrieval & Response Generation
        retrieved_docs = self.retrieve(query, top_k=3)
        citations = [
            {
                "title": d["title"],
                "category": d["category"],
                "chunk_id": d["chunk_id"],
                "source_file": d["source_file"],
                "relevance_score": d["score"]
            }
            for d in retrieved_docs
        ]
        answer = self.generate_grounded_answer(query, retrieved_docs)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query,
            "answer": answer,
            "sources": citations,
            "tool_call": None,
            "latency_ms": latency_ms
        }
