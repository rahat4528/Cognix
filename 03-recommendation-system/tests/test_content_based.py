from recommendation_engine.content_based import ContentBasedRecommender


def test_content_based_fit_and_similar_items(sample_items_df):
    cb = ContentBasedRecommender(max_features=100)
    cb.fit(sample_items_df)

    # Similar items for aud-01 should be aud-02 (both Audio with ANC/Bluetooth tags)
    sims = cb.similar_items("aud-01", top_k=2)
    assert len(sims) > 0
    assert sims[0][0] == "aud-02"
    # Cosine similarity must be in [0.0, 1.0]
    assert 0.0 <= sims[0][1] <= 1.0


def test_content_based_user_recommendations(sample_items_df):
    cb = ContentBasedRecommender(max_features=100)
    cb.fit(sample_items_df)

    # User who interacted with audio headphones
    user_ints = [("aud-01", 5.0)]
    recs = cb.recommend_for_user(user_ints, top_k=2, exclude_interacted=True)

    assert len(recs) > 0
    # aud-02 should be highest ranked content match
    assert recs[0][0] == "aud-02"
    assert recs[0][1] > 0.0
