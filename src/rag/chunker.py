"""
Document chunker implementation for ShopAssist AI.
Splits long documents and policy texts into overlapping semantic chunks with metadata.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import re


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", "; ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Splits input text into chunks respecting boundaries and overlap."""
        text = text.strip()
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len:
                # Find best separator break point near the end
                split_at = -1
                for sep in self.separators:
                    pos = text.rfind(sep, start + self.chunk_overlap, end)
                    if pos != -1:
                        split_at = pos + len(sep)
                        break
                if split_at != -1 and split_at > start:
                    end = split_at

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_len:
                break
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def split_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Takes a document dictionary with 'text' and produces chunked documents."""
        text = doc.get("text", "")
        raw_chunks = self.split_text(text)
        result = []
        base_id = doc.get("chunk_id", "doc")

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_doc = {
                "chunk_id": f"{base_id}-c{idx+1}",
                "text": chunk_text,
                "title": doc.get("title", ""),
                "source_type": doc.get("source_type", "document"),
                "source_file": doc.get("source_file", ""),
                "category": doc.get("category", "GENERAL"),
                "metadata": {
                    **doc.get("metadata", {}),
                    "chunk_index": idx,
                    "total_chunks": len(raw_chunks)
                }
            }
            result.append(chunk_doc)
        return result

