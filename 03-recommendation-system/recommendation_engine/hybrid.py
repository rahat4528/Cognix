from typing import List, Dict, Tuple, Optional, Any
import numpy as np

from .collaborative import MatrixFactorizationRecommender
from .content_based import ContentBasedRecommender
from .sequential import SequentialSessionRecommender


def min_max_normalize(scores: List[Tuple[str, float]]) -> Dict[str, float]:
    """Scales a list of (item_id, raw_score) to [0.0, 1.0]."""
    if not scores:
        return {}
    vals = [s[1] for s in scores]
    min_v = min(vals)
    max_v = max(vals)
    if max_v - min_v > 1e-7:
        return {item_id: (score - min_v) / (max_v - min_v) for item_id, score in scores}
    else:
        return {item_id: 1.0 for item_id, _ in scores}


class HybridEnsembleRecommender:
    """
    Dynamic Multi-Signal Hybrid Ranker combining Collaborative,
    Content-Based, and Sequential Session signals.
    """
    def __init__(
        self,
        cf_recommender: MatrixFactorizationRecommender,
        cb_recommender: ContentBasedRecommender,
        seq_recommender: SequentialSessionRecommender,
        w_cf: float = 0.45,
        w_cb: float = 0.35,
        w_seq: float = 0.20
    ):
        self.cf = cf_recommender
        self.cb = cb_recommender
        self.seq = seq_recommender
        self.w_cf = w_cf
        self.w_cb = w_cb
        self.w_seq = w_seq

    def recommend(
        self,
        user_id: str,
        user_interactions: List[Tuple[str, float]],
        session_items: List[str],
        top_k: int = 10,
        exclude_interacted: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid score fusion across all three engines.
        Adapts weights dynamically when user history is scarce (cold-start mitigation).
        """
        is_cold_start = len(user_interactions) < 3

        # Dynamic weight adjustment for cold start
        if is_cold_start:
            eff_w_cf = 0.0
            eff_w_cb = 0.65
            eff_w_seq = 0.35
        else:
            eff_w_cf = self.w_cf
            eff_w_cb = self.w_cb
            eff_w_seq = self.w_seq

        # 1. Fetch raw candidate predictions from each model
        cf_preds = self.cf.recommend_for_user(user_id, top_k=top_k * 2, exclude_interacted=exclude_interacted) if not is_cold_start else []
        cb_preds = self.cb.recommend_for_user(user_interactions, top_k=top_k * 2, exclude_interacted=exclude_interacted)
        seq_preds = self.seq.predict_next_items(session_items, top_k=top_k * 2, exclude_seen=exclude_interacted)

        # 2. Normalize score spaces
        norm_cf = min_max_normalize(cf_preds)
        norm_cb = min_max_normalize(cb_preds)
        norm_seq = min_max_normalize(seq_preds)

        # 3. Union candidate item set
        all_candidates = set(norm_cf.keys()) | set(norm_cb.keys()) | set(norm_seq.keys())

        # If candidates are empty (brand new zero-history user with empty session)
        if not all_candidates:
            fallback = self.cf.item_popularity[:top_k]
            return [
                {
                    "item_id": item,
                    "hybrid_score": round(score, 4),
                    "model_contributions": {"popularity": 1.0, "cf": 0.0, "cb": 0.0, "seq": 0.0},
                    "is_cold_start": True
                }
                for item, score in fallback
            ]

        # 4. Compute blended hybrid score
        fused_items = []
        for cand in all_candidates:
            sc_cf = norm_cf.get(cand, 0.0)
            sc_cb = norm_cb.get(cand, 0.0)
            sc_seq = norm_seq.get(cand, 0.0)

            blended_score = (eff_w_cf * sc_cf) + (eff_w_cb * sc_cb) + (eff_w_seq * sc_seq)

            fused_items.append({
                "item_id": cand,
                "hybrid_score": round(blended_score, 4),
                "model_contributions": {
                    "cf": round(sc_cf, 3),
                    "cb": round(sc_cb, 3),
                    "seq": round(sc_seq, 3)
                },
                "is_cold_start": is_cold_start
            })

        # Sort descending by hybrid score
        fused_items.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return fused_items[:top_k]
