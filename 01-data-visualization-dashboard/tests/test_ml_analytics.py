import os
import sys
import pytest
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from ml_analytics.engine import compute_ml_evaluation_metrics

def test_scikit_learn_evaluation_metrics():
    # Known ground truth and predictions
    y_true = [0, 1, 0, 1, 0, 1, 1, 0]
    y_pred = [0, 1, 0, 0, 0, 1, 1, 1]
    y_scores = [0.1, 0.9, 0.2, 0.4, 0.15, 0.85, 0.75, 0.6]

    res = compute_ml_evaluation_metrics(y_true, y_pred, y_scores)

    # Verify against direct scikit-learn functions
    expected_acc = accuracy_score(y_true, y_pred)
    expected_prec = precision_score(y_true, y_pred, average="macro")
    expected_rec = recall_score(y_true, y_pred, average="macro")
    expected_f1 = f1_score(y_true, y_pred, average="macro")

    assert res["accuracy"] == round(expected_acc, 4)
    assert res["precision_macro"] == round(expected_prec, 4)
    assert res["recall_macro"] == round(expected_rec, 4)
    assert res["f1_macro"] == round(expected_f1, 4)

    # Verify confusion matrix
    cm_expected = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    assert res["confusion_matrix"]["matrix"] == cm_expected

    # Verify ROC curve is computed and present
    assert res["roc_curve"] is not None
    assert "auc" in res["roc_curve"]
    assert 0.0 <= res["roc_curve"]["auc"] <= 1.0

def test_mismatched_length_rejection():
    with pytest.raises(ValueError):
        compute_ml_evaluation_metrics([0, 1, 0], [1, 0])
