import numpy as np


def compute_cosine_similarity(vec_a: list, vec_b: list) -> float:
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def test_identical_vector_similarity():
    vec = [0.1, 0.5, -0.2, 0.8, -0.4]
    sim = compute_cosine_similarity(vec, vec)
    assert abs(sim - 1.0) < 1e-5


def test_orthogonal_vector_similarity():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [0.0, 1.0, 0.0]
    sim = compute_cosine_similarity(vec_a, vec_b)
    assert abs(sim - 0.0) < 1e-5


def test_opposite_vector_similarity():
    vec_a = [1.0, 2.0, 3.0]
    vec_b = [-1.0, -2.0, -3.0]
    sim = compute_cosine_similarity(vec_a, vec_b)
    assert abs(sim - (-1.0)) < 1e-5
