import io
import numpy as np
from PIL import Image
from inference.models.classifier import MobileNetClassifier


def test_classifier_determinism(sample_jpeg_bytes):
    classifier = MobileNetClassifier()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))

    res1 = classifier.predict(img, top_k=5)
    res2 = classifier.predict(img, top_k=5)

    # Deterministic top label and score
    assert res1["top_label"] == res2["top_label"]
    assert abs(res1["top_score"] - res2["top_score"]) < 1e-4

    # Top-k items have descending scores
    scores = [p["score"] for p in res1["top_predictions"]]
    assert scores == sorted(scores, reverse=True)


def test_classifier_embedding_normalization(sample_jpeg_bytes):
    classifier = MobileNetClassifier()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))
    res = classifier.predict(img, top_k=5)

    embedding = np.array(res["embedding"], dtype=np.float32)
    assert len(embedding) == 576

    # L2 Norm of normalized embedding must equal 1.0 within floating point precision
    l2_norm = float(np.linalg.norm(embedding))
    assert abs(l2_norm - 1.0) < 1e-3


def test_classifier_uncertainty_threshold(sample_jpeg_bytes):
    classifier = MobileNetClassifier()
    img = Image.open(io.BytesIO(sample_jpeg_bytes))

    # With high threshold (0.999), prediction should be marked uncertain
    res_high = classifier.predict(img, top_k=5, uncertainty_threshold=0.999)
    assert res_high["is_uncertain"] is True

    # With very low threshold (0.001), prediction should not be marked uncertain
    res_low = classifier.predict(img, top_k=5, uncertainty_threshold=0.001)
    assert res_low["is_uncertain"] is False
