
from typing import Sequence


def precision_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int
) -> float:
    """
    Calculate Precision@K.

    Precision@K = Relevant retrieved documents / K
    """

    if k < 1:
        raise ValueError("k must be at least 1.")

    retrieved = list(retrieved_ids[:k])
    relevant = set(relevant_ids)

    relevant_retrieved = sum(
        1 for faq_id in retrieved if faq_id in relevant
    )

    return relevant_retrieved / k


def recall_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int
) -> float | None:
    """
    Calculate Recall@K.

    Recall@K = Relevant retrieved documents / Total relevant documents

    Returns None when there are no relevant documents.
    """

    if k < 1:
        raise ValueError("k must be at least 1.")

    relevant = set(relevant_ids)

    if not relevant:
        return None

    retrieved = set(retrieved_ids[:k])

    relevant_retrieved = len(retrieved.intersection(relevant))

    return relevant_retrieved / len(relevant)


def calculate_f1(
    precision: float,
    recall: float
) -> float:
    """
    Calculate F1-score from precision and recall.
    """

    if precision < 0 or recall < 0:
        raise ValueError("Precision and recall cannot be negative.")

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)
    


def hit_rate_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Sequence[str],
    k: int
) -> float | None:
    """
    Return 1.0 if at least one relevant FAQ appears
    in the top K results, otherwise 0.0.

    Returns None when there are no relevant FAQ labels.
    """

    if k < 1:
        raise ValueError("k must be at least 1.")

    relevant = set(relevant_ids)

    if not relevant:
        return None

    retrieved = set(retrieved_ids[:k])

    return float(bool(retrieved.intersection(relevant)))

