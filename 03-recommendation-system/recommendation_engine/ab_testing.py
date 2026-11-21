import hashlib
from typing import Dict, Any, List


class ABExperimentManager:
    """
    A/B Testing Framework for recommendation algorithms.
    Deterministic user routing and live CTR / conversion measurement.
    """
    def __init__(self):
        # Default active experiments
        self.experiments: Dict[str, Dict[str, Any]] = {
            "exp_homepage_algo": {
                "id": "exp_homepage_algo",
                "name": "Homepage Recommender Algorithm Trial",
                "variants": [
                    {"id": "control", "name": "Popularity Baseline", "traffic_pct": 34},
                    {"id": "variant_a", "name": "Pure Collaborative SVD", "traffic_pct": 33},
                    {"id": "variant_b", "name": "Dynamic Hybrid Ensemble", "traffic_pct": 33}
                ],
                "metrics": {
                    "control": {"impressions": 1240, "clicks": 68, "conversions": 14},
                    "variant_a": {"impressions": 1210, "clicks": 112, "conversions": 29},
                    "variant_b": {"impressions": 1255, "clicks": 164, "conversions": 48}
                }
            }
        }

    def assign_variant(self, user_id: str, experiment_id: str) -> str:
        """
        Deterministically maps user_id into an experiment bucket using SHA-256.
        Ensures a user consistently sees the same variant.
        """
        exp = self.experiments.get(experiment_id)
        if not exp:
            return "control"

        hash_input = f"{experiment_id}:{user_id}".encode("utf-8")
        hash_val = int(hashlib.sha256(hash_input).hexdigest()[:8], 16)
        bucket = hash_val % 100

        cumulative = 0
        for v in exp["variants"]:
            cumulative += v["traffic_pct"]
            if bucket < cumulative:
                return v["id"]
        return exp["variants"][-1]["id"]

    def record_event(self, experiment_id: str, variant_id: str, event_type: str):
        """Records impressions, clicks, or conversions for a variant."""
        exp = self.experiments.get(experiment_id)
        if not exp or variant_id not in exp["metrics"]:
            return
        m = exp["metrics"][variant_id]
        if event_type == "impression":
            m["impressions"] += 1
        elif event_type == "click":
            m["clicks"] += 1
        elif event_type == "conversion":
            m["conversions"] += 1

    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        exp = self.experiments.get(experiment_id)
        if not exp:
            return {}

        results = []
        for v in exp["variants"]:
            vid = v["id"]
            m = exp["metrics"][vid]
            imp = m["impressions"]
            clk = m["clicks"]
            conv = m["conversions"]
            ctr = round((clk / imp * 100) if imp > 0 else 0.0, 2)
            cvr = round((conv / clk * 100) if clk > 0 else 0.0, 2)
            results.append({
                "variant_id": vid,
                "variant_name": v["name"],
                "traffic_pct": v["traffic_pct"],
                "impressions": imp,
                "clicks": clk,
                "conversions": conv,
                "ctr_pct": ctr,
                "cvr_pct": cvr
            })

        return {
            "experiment_id": exp["id"],
            "name": exp["name"],
            "variants": results
        }


ab_manager = ABExperimentManager()
