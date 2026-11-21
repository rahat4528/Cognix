from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import TruncatedSVD


class MatrixFactorizationRecommender:
    """
    Genuine Matrix Factorization Recommender utilizing Truncated SVD
    on a sparse User-Item interaction matrix.
    """
    def __init__(self, n_factors: int = 20, random_state: int = 42):
        self.n_factors = n_factors
        self.random_state = random_state
        self.svd: Optional[TruncatedSVD] = None
        self.user_to_idx: Dict[str, int] = {}
        self.idx_to_user: Dict[int, str] = {}
        self.item_to_idx: Dict[str, int] = {}
        self.idx_to_item: Dict[int, str] = {}
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
        self.user_history: Dict[str, set] = {}
        self.item_popularity: List[Tuple[str, float]] = []

    def fit(self, interactions_df: pd.DataFrame):
        """
        Fits Truncated SVD latent factor decomposition.
        interactions_df columns: ['user_id', 'item_id', 'weight']
        """
        unique_users = sorted(interactions_df['user_id'].unique().tolist())
        unique_items = sorted(interactions_df['item_id'].unique().tolist())

        self.user_to_idx = {u: i for i, u in enumerate(unique_users)}
        self.idx_to_user = {i: u for u, i in self.user_to_idx.items()}
        self.item_to_idx = {item: i for i, item in enumerate(unique_items)}
        self.idx_to_item = {i: item for item, i in self.item_to_idx.items()}

        # Build user interaction history
        self.user_history = {}
        for _, row in interactions_df.iterrows():
            u = row['user_id']
            i = row['item_id']
            self.user_history.setdefault(u, set()).add(i)

        # Compute fallback popularity
        pop = interactions_df.groupby('item_id')['weight'].sum().sort_values(ascending=False)
        self.item_popularity = [(item, float(score)) for item, score in pop.items()]

        rows = [self.user_to_idx[u] for u in interactions_df['user_id']]
        cols = [self.item_to_idx[i] for i in interactions_df['item_id']]
        weights = interactions_df['weight'].astype(np.float32).values

        n_users = len(unique_users)
        n_items = len(unique_items)
        sparse_matrix = csr_matrix((weights, (rows, cols)), shape=(n_users, n_items))

        # Adjust n_factors if items/users are smaller than requested factors
        k = min(self.n_factors, n_users - 1, n_items - 1)
        k = max(1, k)

        self.svd = TruncatedSVD(n_components=k, random_state=self.random_state)
        U_Sigma = self.svd.fit_transform(sparse_matrix)  # User factors
        V_Sigma = self.svd.components_                  # Item factors (k x n_items)

        self.user_factors = U_Sigma
        self.item_factors = V_Sigma.T  # (n_items x k)

    def predict_score(self, user_id: str, item_id: str) -> float:
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return 0.0
        u_idx = self.user_to_idx[user_id]
        i_idx = self.item_to_idx[item_id]
        return float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))

    def recommend_for_user(
        self,
        user_id: str,
        top_k: int = 10,
        exclude_interacted: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Returns top-k recommendations ranked by dot-product latent factor affinity.
        """
        if user_id not in self.user_to_idx or self.user_factors is None:
            # Cold-start fallback: return top popular items
            return self.item_popularity[:top_k]

        u_idx = self.user_to_idx[user_id]
        user_vec = self.user_factors[u_idx]

        # Dot product with all items
        scores = np.dot(self.item_factors, user_vec)  # (n_items,)

        history = self.user_history.get(user_id, set())
        ranked_indices = np.argsort(-scores)

        results: List[Tuple[str, float]] = []
        for idx in ranked_indices:
            item_id = self.idx_to_item[int(idx)]
            if exclude_interacted and item_id in history:
                continue
            results.append((item_id, float(scores[idx])))
            if len(results) >= top_k:
                break

        return results
