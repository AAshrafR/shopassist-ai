"""
Data preprocessing, cleaning, normalization, and knowledge base extraction
for the Bitext customer support dataset and store policies.
"""

from __future__ import annotations
import re
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "bitext_customer_support.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
POLICIES_DIR = BASE_DIR / "docs" / "policies"

CLEANED_CSV_PATH = PROCESSED_DIR / "cleaned_customer_support.csv"
KB_CHUNKS_PATH = PROCESSED_DIR / "knowledge_base_chunks.json"
EVAL_DATASET_PATH = PROCESSED_DIR / "eval_dataset.json"


def clean_text(text: str) -> str:
    """Normalize whitespace and remove artifacts."""
    if not isinstance(text, str):
        return ""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_dataset(input_csv: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Cleans and normalizes the Bitext customer support dataset.
    - Strips whitespace
    - Normalizes placeholder tags
    - Deduplicates instruction/response pairs
    - Adds text length metrics
    """
    print(f"Loading raw dataset from {input_csv}...")
    df = pd.read_csv(input_csv)
    initial_len = len(df)

    # Clean text columns
    for col in ["instruction", "category", "intent", "response"]:
        df[col] = df[col].astype(str).apply(clean_text)

    # Standardize categories and intents
    df["category"] = df["category"].str.upper()
    df["intent"] = df["intent"].str.lower()

    # Drop duplicate instruction + response pairs
    df = df.drop_duplicates(subset=["instruction", "response"]).reset_index(drop=True)

    # Calculate text length metrics
    df["instruction_length"] = df["instruction"].str.len()
    df["response_length"] = df["response"].str.len()

    # Filter out empty or trivially short rows
    df = df[(df["instruction_length"] >= 5) & (df["response_length"] >= 15)].reset_index(drop=True)

    print(f"Data cleaning completed: {initial_len} -> {len(df)} rows retained.")
    return df


def load_policy_documents(policies_dir: Path = POLICIES_DIR) -> List[Dict[str, Any]]:
    """
    Parses Markdown store policy documents into structured chunks with headers.
    """
    chunks = []
    if not policies_dir.exists():
        print(f"Policies dir {policies_dir} not found.")
        return chunks

    for md_file in sorted(policies_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        policy_title = title_match.group(1).strip() if title_match else md_file.stem.replace("_", " ").title()

        # Split on sections (## Header)
        sections = re.split(r"\n(?=##\s+)", content)
        for i, sec in enumerate(sections):
            sec = sec.strip()
            if not sec or sec.startswith("# ") and "##" not in sec:
                continue  # Skip document title header chunk
            header_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
            section_title = header_match.group(1).strip() if header_match else f"Section {i}"
            clean_body = re.sub(r"^##\s+.+$", "", sec, flags=re.MULTILINE).strip()

            if clean_body:
                chunks.append({
                    "chunk_id": f"policy-{md_file.stem}-{i}",
                    "source_type": "policy",
                    "source_file": md_file.name,
                    "title": f"{policy_title} - {section_title}",
                    "category": md_file.stem.split("_")[0].upper(),
                    "text": f"[{policy_title} > {section_title}]\n{clean_body}",
                    "metadata": {
                        "policy": policy_title,
                        "section": section_title,
                        "file": md_file.name
                    }
                })

    print(f"Loaded {len(chunks)} policy chunks from {policies_dir}.")
    return chunks


def build_knowledge_base_chunks(
    df: pd.DataFrame,
    sample_per_intent: int = 15
) -> List[Dict[str, Any]]:
    """
    Extracts high-quality canonical Q&A pairs from Bitext dataset
    combined with store policy chunks to create the knowledge base.
    """
    kb_chunks = []

    # 1. Add policy chunks
    policy_chunks = load_policy_documents()
    kb_chunks.extend(policy_chunks)

    # 2. Extract representative FAQ answers per intent
    for intent, group in df.groupby("intent"):
        category = group["category"].iloc[0]
        # Pick top distinct response variants
        sampled = group.drop_duplicates(subset=["response"]).head(sample_per_intent)
        for idx, row in sampled.iterrows():
            cid = f"faq-{category.lower()}-{intent}-{idx}"
            kb_chunks.append({
                "chunk_id": cid,
                "source_type": "bitext_faq",
                "source_file": "bitext_dataset",
                "title": f"FAQ: {intent.replace('_', ' ').title()}",
                "category": category,
                "text": f"Customer Inquiry Type: {intent.replace('_', ' ')}\nSample Question: {row['instruction']}\nGuidance: {row['response']}",
                "metadata": {
                    "category": category,
                    "intent": intent,
                    "sample_query": row["instruction"]
                }
            })

    print(f"Total knowledge base chunks created: {len(kb_chunks)}")
    return kb_chunks


def create_evaluation_dataset(df: pd.DataFrame, n_samples: int = 120) -> List[Dict[str, Any]]:
    """
    Creates a balanced evaluation set covering all intents and categories,
    with queries, ground truth intents, expected categories, and sample answers.
    """
    eval_samples = []
    # Take a balanced sample across intents
    intents = df["intent"].unique()
    per_intent = max(1, n_samples // len(intents))

    for intent in intents:
        subset = df[df["intent"] == intent]
        sampled = subset.sample(n=min(per_intent, len(subset)), random_state=42)
        for _, row in sampled.iterrows():
            eval_samples.append({
                "query": row["instruction"],
                "category": row["category"],
                "intent": row["intent"],
                "ground_truth_answer": row["response"]
            })

    # Add specific domain business queries for tool evaluation
    domain_test_cases = [
        {
            "query": "Where is my order ORD-1001?",
            "category": "ORDER",
            "intent": "track_order",
            "expected_tool": "order_lookup",
            "expected_order_id": "ORD-1001",
            "ground_truth_answer": "Order ORD-1001 for Sarah Connor has shipped with FedEx tracking FDX-998822110."
        },
        {
            "query": "Check status of order ORD-1002 please",
            "category": "ORDER",
            "intent": "track_order",
            "expected_tool": "order_lookup",
            "expected_order_id": "ORD-1002",
            "ground_truth_answer": "Order ORD-1002 for Alex Murphy was delivered on 2026-11-03."
        },
        {
            "query": "Can I return an item after 20 days?",
            "category": "REFUND",
            "intent": "check_refund_policy",
            "expected_tool": "rag_search",
            "ground_truth_answer": "Yes, customers have thirty (30) calendar days from delivery to request a return."
        },
        {
            "query": "I received a damaged keyboard, please open a support ticket for me",
            "category": "FEEDBACK",
            "intent": "complaint",
            "expected_tool": "create_ticket",
            "ground_truth_answer": "A support ticket will be opened for your damaged item."
        },
        {
            "query": "What payment methods do you accept?",
            "category": "PAYMENT",
            "intent": "check_payment_methods",
            "expected_tool": "rag_search",
            "ground_truth_answer": "We accept major credit/debit cards, Apple Pay, Google Pay, PayPal, Klarna, and Afterpay."
        }
    ]
    eval_samples.extend(domain_test_cases)
    print(f"Created evaluation benchmark with {len(eval_samples)} cases.")
    return eval_samples


def run_pipeline():
    """Executes the full preprocessing pipeline."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_cleaned = clean_dataset(RAW_DATA_PATH)
    df_cleaned.to_csv(CLEANED_CSV_PATH, index=False)
    print(f"Saved cleaned dataset to {CLEANED_CSV_PATH}")

    kb_chunks = build_knowledge_base_chunks(df_cleaned)
    with open(KB_CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(kb_chunks, f, indent=2)
    print(f"Saved knowledge base chunks to {KB_CHUNKS_PATH}")

    eval_data = create_evaluation_dataset(df_cleaned)
    with open(EVAL_DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2)
    print(f"Saved evaluation dataset to {EVAL_DATASET_PATH}")


if __name__ == "__main__":
    run_pipeline()
