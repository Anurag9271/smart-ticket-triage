
import json
from pathlib import Path
from statistics import mean, median

from rag.retriever import FAQRetriever


# Evaluation dataset location
DATASET_PATH = Path("evaluation/datasets/retrieval_eval.json")

# Thresholds we want to compare
THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60]


def summarize_distances(records, label):
    """
    Display distance statistics for a group of queries.
    """

    distances = [record["distance"] for record in records]

    print(f"\n{label}")
    print("-" * 45)
    print(f"Queries: {len(distances)}")

    if not distances:
        return

    print(f"Minimum distance: {min(distances):.4f}")
    print(f"Maximum distance: {max(distances):.4f}")
    print(f"Average distance: {mean(distances):.4f}")
    print(f"Median distance:  {median(distances):.4f}")


def compare_thresholds(answerable_records, unanswerable_records):
    """
    Compare different cosine-distance thresholds.

    Lower distance = higher semantic similarity.

    A query passes the filter when:
        distance <= threshold
    """

    print("\n========== THRESHOLD COMPARISON ==========")

    print(
        f"{'Threshold':<12}"
        f"{'Answer Accept':<16}"
        f"{'Unanswer Reject':<18}"
        f"{'False Accept':<15}"
        f"{'False Reject':<15}"
    )

    for threshold in THRESHOLDS:

        # Answerable queries correctly accepted
        true_accept = sum(
            record["distance"] <= threshold
            for record in answerable_records
        )

        # Answerable queries incorrectly rejected
        false_reject = len(answerable_records) - true_accept

        # Unanswerable queries incorrectly accepted
        false_accept = sum(
            record["distance"] <= threshold
            for record in unanswerable_records
        )

        # Unanswerable queries correctly rejected
        true_reject = len(unanswerable_records) - false_accept

        # Calculate rates
        answer_accept_rate = (
            true_accept / len(answerable_records)
            if answerable_records else 0.0
        )

        unanswer_reject_rate = (
            true_reject / len(unanswerable_records)
            if unanswerable_records else 0.0
        )

        print(
            f"{threshold:<12.2f}"
            f"{answer_accept_rate:<16.2%}"
            f"{unanswer_reject_rate:<18.2%}"
            f"{false_accept:<15}"
            f"{false_reject:<15}"
        )


def evaluate_distances():
    """
    Evaluate cosine distances for all customer queries
    and compare candidate thresholds.
    """

    # Step 1: Load evaluation dataset
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    # Step 2: Initialize the existing FAQ retriever
    retriever = FAQRetriever()

    answerable_records = []
    unanswerable_records = []

    # Step 3: Retrieve FAQ evidence for each query
    for record in dataset:

        results = retriever.retrieve(
            query=record["ticket"],
            top_k=3,
        )

        distances = results["distances"][0]

        if not distances:
            raise RuntimeError(
                f"No retrieval results for {record['id']}"
            )

        # The smallest distance is the closest FAQ match
        best_distance = min(distances)

        result = {
            "id": record["id"],
            "ticket": record["ticket"],
            "distance": best_distance,
        }

        if record["answerable"]:
            answerable_records.append(result)
        else:
            unanswerable_records.append(result)

    # Step 4: Display distance statistics
    print("\n========== DISTANCE ANALYSIS ==========")

    summarize_distances(
        answerable_records,
        "ANSWERABLE QUERIES",
    )

    summarize_distances(
        unanswerable_records,
        "UNANSWERABLE QUERIES",
    )

    # Step 5: Identify difficult answerable queries
    print("\n========== HIGHEST ANSWERABLE DISTANCES ==========")

    for record in sorted(
        answerable_records,
        key=lambda item: item["distance"],
        reverse=True,
    )[:5]:

        print(
            f"{record['id']} | "
            f"{record['distance']:.4f} | "
            f"{record['ticket']}"
        )

    # Step 6: Identify potentially risky unanswerable queries
    print("\n========== LOWEST UNANSWERABLE DISTANCES ==========")

    for record in sorted(
        unanswerable_records,
        key=lambda item: item["distance"],
    )[:5]:

        print(
            f"{record['id']} | "
            f"{record['distance']:.4f} | "
            f"{record['ticket']}"
        )

    # Step 7: Compare candidate thresholds
    compare_thresholds(
        answerable_records,
        unanswerable_records,
    )


if __name__ == "__main__":
    evaluate_distances()
