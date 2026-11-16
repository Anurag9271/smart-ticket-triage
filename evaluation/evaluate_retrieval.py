
import json
from pathlib import Path

from rag.retriever import FAQRetriever
from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    calculate_f1,
    hit_rate_at_k,
)


DATASET_PATH = Path("evaluation/datasets/retrieval_eval.json")
TOP_K = 3


def normalize_faq_id(metadata: dict) -> str:
    """Convert ChromaDB metadata into our evaluation FAQ ID."""

    source = Path(metadata["source"]).stem
    faq_number = metadata["faq_number"]

    return f"{source}_{faq_number}"


def evaluate_retrieval():
    # Step 1: Load labelled evaluation queries
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    # Step 2: Initialize the existing RAG retriever
    retriever = FAQRetriever()

    precision_scores = []
    recall_scores = []
    failed_queries = []
    evaluated_queries = 0
    hit_at_1_scores = []
    hit_at_3_scores = []

    # Step 3: Evaluate each customer query
    for record in dataset:
        ticket = record["ticket"]
        expected_ids = record["relevant_faq_ids"]

        # Retrieve the top K FAQs
        results = retriever.retrieve(
            query=ticket,
            top_k=TOP_K,
        )

        # Convert ChromaDB metadata to canonical FAQ IDs
        metadata_list = results["metadatas"][0]

        retrieved_ids = [
            normalize_faq_id(metadata)
            for metadata in metadata_list
        ]

        if record["answerable"]:
            hit_at_1_scores.append(
                hit_rate_at_k(retrieved_ids, expected_ids, 1)
            )

            hit_at_3_scores.append(
                hit_rate_at_k(retrieved_ids, expected_ids, 3)
            )

        # Step 4: Calculate retrieval metrics
        # Queries with no labelled relevant FAQs are
        # evaluated separately for answerability.
        if not expected_ids:
            continue

        precision = precision_at_k(
            retrieved_ids, expected_ids, TOP_K
        )

        recall = recall_at_k(
            retrieved_ids, expected_ids, TOP_K
        )

        precision_scores.append(precision)
        recall_scores.append(recall)
        evaluated_queries += 1

        # Record cases where relevant FAQs were missed
        if recall < 1.0:
            failed_queries.append({
                "id": record["id"],
                "ticket": ticket,
                "expected": expected_ids,
                "retrieved": retrieved_ids,
                "recall": recall,
            })

    # Step 5: Aggregate metrics
    avg_precision = sum(precision_scores) / evaluated_queries
    avg_recall = sum(recall_scores) / evaluated_queries

    f1 = calculate_f1(avg_precision, avg_recall)

    avg_hit_at_1 = sum(hit_at_1_scores) / len(hit_at_1_scores)
    avg_hit_at_3 = sum(hit_at_3_scores) / len(hit_at_3_scores)

    print("\n========== ANSWERABLE QUERY RANKING ==========")
    print(f"Answerable queries: {len(hit_at_1_scores)}")
    print(f"Hit Rate@1: {avg_hit_at_1:.4f}")
    print(f"Hit Rate@3: {avg_hit_at_3:.4f}")

    # Step 6: Display results
    print("\n========== RAG RETRIEVAL EVALUATION ==========")
    print(f"Total dataset queries: {len(dataset)}")
    print(f"Queries with relevant FAQ labels: {evaluated_queries}")
    print(f"Queries without relevant FAQ labels: {len(dataset) - evaluated_queries}")

    print(f"\nPrecision@{TOP_K}: {avg_precision:.4f}")
    print(f"Recall@{TOP_K}:    {avg_recall:.4f}")
    print(f"F1-score:         {f1:.4f}")

    print(f"\nQueries with incomplete retrieval: {len(failed_queries)}")

    for failure in failed_queries:
        print(f"\nID: {failure['id']}")
        print(f"Ticket: {failure['ticket']}")
        print(f"Expected: {failure['expected']}")
        print(f"Retrieved: {failure['retrieved']}")
        print(f"Recall: {failure['recall']:.4f}")


if __name__ == "__main__":
    evaluate_retrieval()
