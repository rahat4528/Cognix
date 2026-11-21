import os
import json
import time
from typing import Dict, Any
import pandas as pd

from recommendation_engine.collaborative import MatrixFactorizationRecommender
from recommendation_engine.content_based import ContentBasedRecommender
from recommendation_engine.sequential import SequentialSessionRecommender
from recommendation_engine.hybrid import HybridEnsembleRecommender
from data_processing.temporal_splitter import TemporalDataSplitter
from model_evaluation.metrics import evaluate_recommender


def train_and_evaluate_all(
    items_df: pd.DataFrame,
    interactions_df: pd.DataFrame,
    output_dir: str = "./model_evaluation"
) -> Dict[str, Any]:
    """
    Executes full offline training pipeline with temporal train/validation/test split.
    Trains Collaborative, Content-Based, Sequential, and Hybrid models.
    Computes genuine NDCG@10, Recall@10, MAP@10, and coverage metrics.
    Saves results to benchmark_results.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.time()

    # 1. Temporal splitting (60% Train, 20% Val, 20% Test)
    splitter = TemporalDataSplitter(train_ratio=0.60, val_ratio=0.20)
    train_df, val_df, test_df = splitter.split(interactions_df, timestamp_col="timestamp")

    catalog_set = set(items_df['id'].unique())

    # Build test user ground truth (items in test_df)
    test_ground_truth = {}
    for user_id, group in test_df.groupby("user_id"):
        test_ground_truth[user_id] = set(group['item_id'].unique())

    # 2. Train Collaborative Filtering (on train_df)
    cf = MatrixFactorizationRecommender(n_factors=15, random_state=42)
    cf.fit(train_df)

    # 3. Train Content-Based (on catalog)
    cb = ContentBasedRecommender(max_features=500)
    cb.fit(items_df)

    # 4. Train Sequential Model (on train_df as sessions)
    train_sessions = train_df.copy()
    if 'session_id' not in train_sessions.columns:
        train_sessions['session_id'] = train_sessions['user_id']
    seq = SequentialSessionRecommender(decay_factor=0.65)
    seq.fit(train_sessions)

    # 5. Train Hybrid Ensemble
    hybrid = HybridEnsembleRecommender(cf, cb, seq, w_cf=0.45, w_cb=0.35, w_seq=0.20)

    # User interactions map for test users
    user_train_interactions = {}
    for u, group in train_df.groupby("user_id"):
        user_train_interactions[u] = list(zip(group['item_id'], group['weight']))

    # 6. Evaluate all algorithms
    eval_results = {}

    # Popularity baseline
    pop_items = [item for item, _ in cf.item_popularity]
    eval_results["Popularity Baseline"] = evaluate_recommender(
        lambda u: pop_items,
        test_ground_truth,
        catalog_set,
        k=10
    )

    # Collaborative Filtering
    eval_results["Collaborative Filtering (SVD)"] = evaluate_recommender(
        lambda u: [i for i, _ in cf.recommend_for_user(u, top_k=10)],
        test_ground_truth,
        catalog_set,
        k=10
    )

    # Content-Based Filtering
    eval_results["Content-Based (TF-IDF)"] = evaluate_recommender(
        lambda u: [i for i, _ in cb.recommend_for_user(user_train_interactions.get(u, []), top_k=10)],
        test_ground_truth,
        catalog_set,
        k=10
    )

    # Hybrid Ensemble
    eval_results["Hybrid Ensemble"] = evaluate_recommender(
        lambda u: [r["item_id"] for r in hybrid.recommend(u, user_train_interactions.get(u, []), [], top_k=10)],
        test_ground_truth,
        catalog_set,
        k=10
    )

    summary = {
        "dataset_metadata": {
            "total_items": len(catalog_set),
            "total_interactions": len(interactions_df),
            "train_interactions": len(train_df),
            "val_interactions": len(val_df),
            "test_interactions": len(test_df),
            "test_eval_users": len(test_ground_truth)
        },
        "temporal_split": {
            "train_ratio": 0.60,
            "val_ratio": 0.20,
            "test_ratio": 0.20,
            "train_cutoff_timestamp": float(train_df['timestamp'].max()) if not train_df.empty else 0,
            "test_start_timestamp": float(test_df['timestamp'].min()) if not test_df.empty else 0
        },
        "benchmarks": eval_results,
        "elapsed_seconds": round(time.time() - t0, 3)
    }

    # Save to disk
    out_file = os.path.join(output_dir, "benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(summary, f, indent=2)

    return summary
