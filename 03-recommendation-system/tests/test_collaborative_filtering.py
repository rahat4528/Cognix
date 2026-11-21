import numpy as np
from recommendation_engine.collaborative import MatrixFactorizationRecommender


def test_matrix_factorization_fit_and_shapes(sample_interactions_df):
    model = MatrixFactorizationRecommender(n_factors=2, random_state=42)
    model.fit(sample_interactions_df)

    # 4 distinct users, 5 distinct items
    assert len(model.user_to_idx) == 4
    assert len(model.item_to_idx) == 5
    assert model.user_factors.shape[0] == 4
    assert model.item_factors.shape[0] == 5


def test_matrix_factorization_recommendation_ranking(sample_interactions_df):
    model = MatrixFactorizationRecommender(n_factors=2, random_state=42)
    model.fit(sample_interactions_df)

    recs = model.recommend_for_user("u1", top_k=3, exclude_interacted=True)
    assert len(recs) > 0
    # User 1 already interacted with aud-01 and aud-02, so recs should exclude them
    rec_items = [item for item, _ in recs]
    assert "aud-01" not in rec_items
    assert "aud-02" not in rec_items

    # Scores must be strictly descending
    scores = [s for _, s in recs]
    assert scores == sorted(scores, reverse=True)


def test_matrix_factorization_cold_start_fallback(sample_interactions_df):
    model = MatrixFactorizationRecommender(n_factors=2, random_state=42)
    model.fit(sample_interactions_df)

    # Unknown user should receive popularity fallback
    recs = model.recommend_for_user("unknown_user_999", top_k=3)
    assert len(recs) == 3
    # Top popular item in sample is cmp-01 or aud-01
    assert recs[0][0] in ["cmp-01", "aud-01"]
