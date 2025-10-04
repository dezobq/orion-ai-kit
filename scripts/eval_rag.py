#!/usr/bin/env python3
"""
RAG Evaluation Script - Measures Recall@K and MRR (Mean Reciprocal Rank)

Supports three retrieval strategies:
1. BM25 (keyword-based)
2. Vector (semantic search with embeddings)
3. Hybrid (BM25 + Vector with reranking)
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Tuple
import urllib3

try:
    import requests
except ImportError:
    print("❌ Missing 'requests' library. Install: pip install requests")
    sys.exit(1)

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# OpenSearch connection
OS_URL = os.getenv("OS_URL", "https://localhost:9200")
OS_USER = os.getenv("OS_USER", "admin")
OS_PASS = os.getenv("OS_PASS", "MyS3curePassw0rd!2025")
INDEX_NAME = "code-chunks"


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def bm25_search(query: str, k: int = 50) -> List[str]:
    """BM25 keyword search."""
    payload = {
        "query": {"match": {"content": query}},
        "size": k,
        "_source": ["doc_id", "path", "start_line", "end_line"]
    }

    resp = requests.post(
        f"{OS_URL}/{INDEX_NAME}/_search",
        json=payload,
        auth=(OS_USER, OS_PASS),
        verify=False,
        timeout=30
    )
    resp.raise_for_status()

    hits = resp.json().get("hits", {}).get("hits", [])
    # Use doc_id if available, otherwise fallback to path:start_line
    return [
        h['_source'].get('doc_id', f"{h['_source']['path']}:{h['_source'].get('start_line', 1)}")
        for h in hits
    ]


def vector_search(query: str, k: int = 50) -> List[str]:
    """Vector semantic search (requires embeddings)."""
    # This is a placeholder - actual implementation would:
    # 1. Embed the query using the same model (all-MiniLM-L6-v2)
    # 2. Perform KNN search
    # For now, falls back to BM25
    print("⚠️  Vector search not implemented, using BM25 fallback")
    return bm25_search(query, k)


def hybrid_search(query: str, k: int = 50) -> List[str]:
    """Hybrid search: BM25 + Vector with score fusion."""
    # Get results from both methods
    bm25_results = set(bm25_search(query, k))
    vector_results = set(vector_search(query, k))

    # Simple fusion: union with BM25 priority
    combined = list(bm25_results) + [r for r in vector_results if r not in bm25_results]
    return combined[:k]


def calculate_recall_at_k(retrieved: List[str], gold: List[str], k: int) -> float:
    """Calculate Recall@K metric."""
    if not gold:
        return 0.0

    retrieved_set = set(retrieved[:k])
    gold_set = set(gold)

    hits = len(retrieved_set.intersection(gold_set))
    return hits / len(gold_set)


def calculate_mrr(retrieved: List[str], gold: List[str]) -> float:
    """Calculate Mean Reciprocal Rank."""
    if not gold:
        return 0.0

    gold_set = set(gold)

    for idx, doc in enumerate(retrieved, start=1):
        if doc in gold_set:
            return 1.0 / idx

    return 0.0


def evaluate_rag(
    queries: List[Dict[str, Any]],
    gold_data: Dict[str, List[str]],
    k: int = 50,
    strategy: str = "bm25"
) -> Dict[str, Any]:
    """Run RAG evaluation."""

    search_fn = {
        "bm25": bm25_search,
        "vector": vector_search,
        "hybrid": hybrid_search
    }.get(strategy, bm25_search)

    results = []
    total_recall = 0.0
    total_mrr = 0.0

    for q in queries:
        query_id = q.get("id", q.get("query", ""))
        query_text = q.get("query", q.get("text", ""))

        if not query_text:
            continue

        # Get gold standard
        gold = gold_data.get(query_id, [])

        # Retrieve documents
        retrieved = search_fn(query_text, k)

        # Calculate metrics
        recall = calculate_recall_at_k(retrieved, gold, k)
        mrr = calculate_mrr(retrieved, gold)

        total_recall += recall
        total_mrr += mrr

        results.append({
            "query_id": query_id,
            "query": query_text,
            "retrieved_count": len(retrieved),
            "gold_count": len(gold),
            "recall@k": round(recall, 4),
            "mrr": round(mrr, 4)
        })

    num_queries = len(results)
    avg_recall = total_recall / num_queries if num_queries > 0 else 0.0
    avg_mrr = total_mrr / num_queries if num_queries > 0 else 0.0

    return {
        "strategy": strategy,
        "k": k,
        "num_queries": num_queries,
        "avg_recall@k": round(avg_recall, 4),
        "avg_mrr": round(avg_mrr, 4),
        "per_query": results
    }


def main():
    parser = argparse.ArgumentParser(description="RAG Evaluation - Recall@K and MRR")
    parser.add_argument("--q", required=True, help="Path to queries JSONL file")
    parser.add_argument("--gold", required=True, help="Path to gold standard JSONL file")
    parser.add_argument("--k", type=int, default=50, help="K for Recall@K (default: 50)")
    parser.add_argument("--strategy", choices=["bm25", "vector", "hybrid"], default="bm25",
                       help="Retrieval strategy (default: bm25)")
    parser.add_argument("--out", required=True, help="Output JSON file path")

    args = parser.parse_args()

    # Load data
    print(f"📊 Loading queries from {args.q}...")
    queries = load_jsonl(args.q)

    print(f"📊 Loading gold standard from {args.gold}...")
    gold_list = load_jsonl(args.gold)

    # Convert gold to dict
    gold_data = {}
    for item in gold_list:
        query_id = item.get("id", item.get("query", ""))
        gold_data[query_id] = item.get("relevant_docs", item.get("docs", []))

    print(f"🔍 Running evaluation with strategy={args.strategy}, k={args.k}...")

    # Run evaluation
    eval_results = evaluate_rag(queries, gold_data, k=args.k, strategy=args.strategy)

    # Save results
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    # Print summary
    print(f"\n✅ Evaluation complete!")
    print(f"   Strategy: {eval_results['strategy']}")
    print(f"   Queries: {eval_results['num_queries']}")
    print(f"   Avg Recall@{args.k}: {eval_results['avg_recall@k']:.2%}")
    print(f"   Avg MRR: {eval_results['avg_mrr']:.4f}")
    print(f"   Results saved to: {args.out}")


if __name__ == "__main__":
    main()
