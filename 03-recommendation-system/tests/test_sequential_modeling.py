import numpy as np
from recommendation_engine.sequential import SequentialSessionRecommender


def test_sequential_markov_probabilities(sample_interactions_df):
    seq = SequentialSessionRecommender(decay_factor=0.65, smoothing=0.01)
    seq.fit(sample_interactions_df)

    matrix = seq.transition_matrix
    assert matrix is not None

    # Every row in transition probability matrix must sum to 1.0
    row_sums = np.sum(matrix, axis=1)
    for r_sum in row_sums:
        assert abs(r_sum - 1.0) < 1e-4


def test_sequential_prediction(sample_interactions_df):
    seq = SequentialSessionRecommender(decay_factor=0.65)
    seq.fit(sample_interactions_df)

    # In s1, aud-01 is followed by aud-02
    preds = seq.predict_next_items(["aud-01"], top_k=2, exclude_seen=True)
    assert len(preds) > 0
    # aud-02 should be top candidate
    assert preds[0][0] == "aud-02"
