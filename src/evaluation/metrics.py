"""
Evaluation metrics computation for ShopAssist AI RAG and Tool execution.
Computes Precision@K, Recall@K, MRR, Tool Execution Accuracy, and Latency percentiles.
"""

from typing import List, Dict, Any
import numpy as np


def compute_retrieval_metrics(
    retrieved_docs: List[Dict[str, Any]],
    expected_category: str,
    k: int = 3
) -> Dict[str, float]:
    """
    Computes Precision@K, Recall@K, and Reciprocal Rank for retrieved documents.
    """
    if not retrieved_docs:
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "mrr": 0.0}

    top_docs = retrieved_docs[:k]
    matches = 0
    first_match_rank = 0

    for idx, doc in enumerate(top_docs):
        doc_cat = doc.get("category", "").upper()
        if doc_cat == expected_category.upper():
            matches += 1
            if first_match_rank == 0:
                first_match_rank = idx + 1

    precision = matches / max(1, len(top_docs))
    # Recall approximation: is at least one relevant document retrieved in top-k
    recall = 1.0 if matches > 0 else 0.0
    mrr = (1.0 / first_match_rank) if first_match_rank > 0 else 0.0

    return {
        "precision_at_k": round(precision, 4),
        "recall_at_k": round(recall, 4),
        "mrr": round(mrr, 4)
    }


def compute_tool_accuracy(
    executed_tool: Any,
    expected_tool: str,
    expected_param: str = None
) -> float:
    """
    Evaluates whether the query correctly dispatched the expected business tool.
    """
    if expected_tool in ("rag_search", "none", None):
        return 1.0 if executed_tool is None else 0.0

    if not executed_tool:
        return 0.0

    tool_name = executed_tool.get("tool_name")
    if expected_tool in ("create_ticket", "create_support_ticket") and tool_name in ("create_ticket", "create_support_ticket"):
        return 1.0
    if tool_name != expected_tool:
        return 0.0

    if expected_param and expected_tool == "order_lookup":
        actual_id = executed_tool.get("parameters", {}).get("order_id")
        return 1.0 if actual_id == expected_param else 0.5

    return 1.0


def compute_latency_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculates p50, p90, p99, mean, and std of response latencies."""
    if not latencies:
        return {"mean": 0.0, "p50": 0.0, "p90": 0.0, "p99": 0.0}
    arr = np.array(latencies)
    return {
        "mean_ms": round(float(np.mean(arr)), 2),
        "p50_ms": round(float(np.percentile(arr, 50)), 2),
        "p90_ms": round(float(np.percentile(arr, 90)), 2),
        "p99_ms": round(float(np.percentile(arr, 99)), 2)
    }
