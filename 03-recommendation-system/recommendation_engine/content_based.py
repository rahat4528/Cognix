from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedRecommender:
    """
    Content-Based Filtering utilizing TF-IDF feature matrices
    over item categories, attributes, and descriptions.
    """
    def __init__(self, max_features: int = 1000):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=max_features)
        self.item_ids: List[str] = []
        self.item_to_idx: Dict[str, int] = {}
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.similarity_matrix: Optional[np.ndarray] = None

    def fit(self, items_df: pd.DataFrame):
        """
        items_df columns: ['id', 'title', 'category', 'tags', 'description']
        """
        self.item_ids = items_df['id'].tolist()
        self.item_to_idx = {item_id: idx for idx, item_id in enumerate(self.item_ids)}

        # Build unified content corpus per item
        corpus = []
        for _, row in items_df.iterrows():
            text = f"{row.get('title', '')} {row.get('category', '')} {row.get('tags', '')} {row.get('description', '')}"
            corpus.append(text)

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        # Precompute item-item cosine similarity matrix
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def similar_items(self, item_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Finds items most similar to the given item based on content attributes."""
        if item_id not in self.item_to_idx or self.similarity_matrix is None:
            return []

        idx = self.item_to_idx[item_id]
        sim_scores = self.similarity_matrix[idx]
        sorted_indices = np.argsort(-sim_scores)

        results = []
        for i in sorted_indices:
            cand_id = self.item_ids[i]
            if cand_id == item_id:
                continue
            results.append((cand_id, float(sim_scores[i])))
            if len(results) >= top_k:
                break
        return results

    def recommend_for_user(
        self,
        user_interactions: List[Tuple[str, float]],  # [(item_id, weight)]
        top_k: int = 10,
        exclude_interacted: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Builds user preference centroid from interacted item vectors
        and ranks catalog by cosine similarity to the centroid.
        """
        if not user_interactions or self.tfidf_matrix is None:
            return []

        interacted_indices = []
        weights = []
        interacted_set = set()

        for item_id, weight in user_interactions:
            interacted_set.add(item_id)
            if item_id in self.item_to_idx:
                interacted_indices.append(self.item_to_idx[item_id])
                weights.append(weight)

        if not interacted_indices:
            return []

        # Weighted average of TF-IDF vectors
        sub_matrix = self.tfidf_matrix[interacted_indices].toarray()
        weights_arr = np.array(weights, dtype=np.float32).reshape(-1, 1)
        user_centroid = np.sum(sub_matrix * weights_arr, axis=0, keepdims=True)
        user_norm = np.linalg.norm(user_centroid)

        if user_norm > 0:
            user_centroid /= user_norm

        # Compute cosine similarity between user centroid and all item vectors
        scores = cosine_similarity(user_centroid, self.tfidf_matrix).flatten()
        sorted_indices = np.argsort(-scores)

        results = []
        for i in sorted_indices:
            cand_id = self.item_ids[i]
            if exclude_interacted and cand_id in interacted_set:
                continue
            results.append((cand_id, float(scores[i])))
            if len(results) >= top_k:
                break

        return results
