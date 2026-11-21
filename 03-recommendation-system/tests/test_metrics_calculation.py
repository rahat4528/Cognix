import math
from model_evaluation.metrics import (
    calculate_ndcg_at_k,
    calculate_recall_at_k,
    calculate_precision_at_k,
    calculate_map_at_k,
    calculate_hit_rate_at_k,
    calculate_catalog_coverage
)


def test_ndcg_perfect_and_zero():
    ground_truth = {"item1", "item2"}

    # Perfect ranking: both ground truth items at rank 1 and 2
    perfect_recs = ["item1", "item2", "item3", "item4"]
    ndcg_perfect = calculate_ndcg_at_k(perfect_recs, ground_truth, k=5)
    assert abs(ndcg_perfect - 1.0) < 1e-4

    # Completely irrelevant recommendations
    bad_recs = ["item5", "item6", "item7"]
    ndcg_bad = calculate_ndcg_at_k(bad_recs, ground_truth, k=5)
    assert ndcg_bad == 0.0


def test_recall_and_precision():
    ground_truth = {"item1", "item2", "item3"}
    recs = ["item1", "item4", "item2", "item5", "item6"]

    # In top 5, hits are item1, item2 (2 hits)
    # Recall: 2 / 3 = 0.6667
    recall = calculate_recall_at_k(recs, ground_truth, k=5)
    assert abs(recall - (2.0 / 3.0)) < 1e-4

    # Precision: 2 / 5 = 0.4
    precision = calculate_precision_at_k(recs, ground_truth, k=5)
    assert abs(precision - 0.4) < 1e-4


def test_catalog_coverage():
    catalog = {"i1", "i2", "i3", "i4", "i5"}
    recs_user1 = ["i1", "i2"]
    recs_user2 = ["i2", "i3"]
    coverage = calculate_catalog_coverage([recs_user1, recs_user2], catalog)
    # Unique recs: i1, i2, i3 -> 3 / 5 = 0.60
    assert abs(coverage - 0.60) < 1e-4
