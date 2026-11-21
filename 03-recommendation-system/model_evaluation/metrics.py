import math
from typing import List, Set, Dict, Any


def calculate_ndcg_at_k(recommended_items: List[str], ground_truth: Set[str], k: int = 10) -> float:
    """
    Calculates Normalized Discounted Cumulative Gain at Rank K.
    """
    if not ground_truth or not recommended_items:
        return 0.0

    k_items = recommended_items[:k]
    dcg = 0.0
    for idx, item in enumerate(k_items):
        if item in ground_truth:
            dcg += 1.0 / math.log2(idx + 2)  # idx 0 -> log2(2) = 1.0

    # Ideal DCG (all relevant items ranked at top)
    idcg = 0.0
    for idx in range(min(k, len(ground_truth))):
        idcg += 1.0 / math.log2(idx + 2)

    return float(dcg / idcg) if idcg > 0.0 else 0.0


def calculate_recall_at_k(recommended_items: List[str], ground_truth: Set[str], k: int = 10) -> float:
    """Calculates Recall at Rank K: fraction of relevant items retrieved in top-k."""
    if not ground_truth or not recommended_items:
        return 0.0
    k_items = set(recommended_items[:k])
    hits = len(k_items.intersection(ground_truth))
    return float(hits / len(ground_truth))


def calculate_precision_at_k(recommended_items: List[str], ground_truth: Set[str], k: int = 10) -> float:
    """Calculates Precision at Rank K: fraction of top-k recommended items that are relevant."""
    if not recommended_items or k <= 0:
        return 0.0
    k_items = set(recommended_items[:k])
    hits = len(k_items.intersection(ground_truth))
    return float(hits / k)


def calculate_map_at_k(recommended_items: List[str], ground_truth: Set[str], k: int = 10) -> float:
    """Calculates Average Precision at Rank K."""
    if not ground_truth or not recommended_items:
        return 0.0

    hits = 0
    sum_precisions = 0.0
    k_items = recommended_items[:k]

    for idx, item in enumerate(k_items):
        if item in ground_truth:
            hits += 1
            sum_precisions += hits / (idx + 1)

    return float(sum_precisions / min(k, len(ground_truth))) if ground_truth else 0.0


def calculate_hit_rate_at_k(recommended_items: List[str], ground_truth: Set[str], k: int = 10) -> float:
    """Returns 1.0 if at least one ground-truth item appears in top-k, else 0.0."""
    k_items = set(recommended_items[:k])
    return 1.0 if len(k_items.intersection(ground_truth)) > 0 else 0.0


def calculate_catalog_coverage(all_recommendations: List[List[str]], catalog_items: Set[str]) -> float:
    """Percentage of catalog items recommended across all users."""
    if not catalog_items:
        return 0.0
    unique_recommended = set()
    for recs in all_recommendations:
        unique_recommended.update(recs)
    return float(len(unique_recommended.intersection(catalog_items)) / len(catalog_items))


def evaluate_recommender(
    recommender_fn,  # callable: (user_id) -> List[str]
    test_user_ground_truth: Dict[str, Set[str]],
    catalog_items: Set[str],
    k: int = 10
) -> Dict[str, float]:
    """
    Runs full benchmark evaluation across test users.
    Returns mean NDCG@K, Recall@K, Precision@K, MAP@K, and Catalog Coverage.
    """
    ndcg_list = []
    recall_list = []
    precision_list = []
    map_list = []
    hit_list = []
    all_recs = []

    for user_id, gt_items in test_user_ground_truth.items():
        if not gt_items:
            continue
        recs = recommender_fn(user_id)
        all_recs.append(recs[:k])

        ndcg_list.append(calculate_ndcg_at_k(recs, gt_items, k=k))
        recall_list.append(calculate_recall_at_k(recs, gt_items, k=k))
        precision_list.append(calculate_precision_at_k(recs, gt_items, k=k))
        map_list.append(calculate_map_at_k(recs, gt_items, k=k))
        hit_list.append(calculate_hit_rate_at_k(recs, gt_items, k=k))

    n_users = max(1, len(ndcg_list))
    coverage = calculate_catalog_coverage(all_recs, catalog_items)

    return {
        f"ndcg@{k}": round(float(sum(ndcg_list) / n_users), 4),
        f"recall@{k}": round(float(sum(recall_list) / n_users), 4),
        f"precision@{k}": round(float(sum(precision_list) / n_users), 4),
        f"map@{k}": round(float(sum(map_list) / n_users), 4),
        f"hit_rate@{k}": round(float(sum(hit_list) / n_users), 4),
        "catalog_coverage": round(coverage, 4)
    }
