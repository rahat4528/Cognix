from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd


class SequentialSessionRecommender:
    """
    First-order Markov Chain session recommender modeling transition
    probabilities between contiguous browsing and purchasing events.
    """
    def __init__(self, decay_factor: float = 0.65, smoothing: float = 0.01):
        self.decay_factor = decay_factor
        self.smoothing = smoothing
        self.item_to_idx: Dict[str, int] = {}
        self.idx_to_item: Dict[int, str] = {}
        self.transition_matrix: Optional[np.ndarray] = None
        self.global_popularity: List[Tuple[str, float]] = []

    def fit(self, sessions_df: pd.DataFrame):
        """
        sessions_df columns: ['session_id', 'item_id', 'timestamp']
        Ordered by timestamp within session.
        """
        unique_items = sorted(sessions_df['item_id'].unique().tolist())
        self.item_to_idx = {item: i for i, item in enumerate(unique_items)}
        self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}
        n_items = len(unique_items)

        # Transition count matrix with Laplace smoothing
        counts = np.full((n_items, n_items), self.smoothing, dtype=np.float64)

        # Group by session and record pairs (item_t-1 -> item_t)
        for _, session_group in sessions_df.groupby('session_id'):
            items = session_group.sort_values('timestamp')['item_id'].tolist()
            for t in range(len(items) - 1):
                i_from = self.item_to_idx.get(items[t])
                i_to = self.item_to_idx.get(items[t + 1])
                if i_from is not None and i_to is not None:
                    counts[i_from, i_to] += 1.0

        # Row-normalize to transition probability matrix
        row_sums = counts.sum(axis=1, keepdims=True)
        self.transition_matrix = counts / row_sums

        # Global item frequencies
        item_counts = sessions_df['item_id'].value_counts()
        self.global_popularity = [(item, float(cnt)) for item, cnt in item_counts.items()]

    def predict_next_items(
        self,
        session_item_ids: List[str],
        top_k: int = 10,
        exclude_seen: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Predicts next items based on session interaction sequence
        with exponential time decay prioritizing recent actions.
        """
        if not session_item_ids or self.transition_matrix is None:
            return self.global_popularity[:top_k]

        valid_items = [item for item in session_item_ids if item in self.item_to_idx]
        if not valid_items:
            return self.global_popularity[:top_k]

        n_items = len(self.item_to_idx)
        aggregated_scores = np.zeros(n_items, dtype=np.float64)

        # Apply exponential decay from most recent item to earliest
        seq_len = len(valid_items)
        for step, item in enumerate(valid_items):
            weight = self.decay_factor ** (seq_len - 1 - step)
            idx = self.item_to_idx[item]
            aggregated_scores += weight * self.transition_matrix[idx]

        sorted_indices = np.argsort(-aggregated_scores)
        seen_set = set(session_item_ids)

        results: List[Tuple[str, float]] = []
        for idx in sorted_indices:
            item_id = self.idx_to_item[int(idx)]
            if exclude_seen and item_id in seen_set:
                continue
            results.append((item_id, float(aggregated_scores[idx])))
            if len(results) >= top_k:
                break

        return results
