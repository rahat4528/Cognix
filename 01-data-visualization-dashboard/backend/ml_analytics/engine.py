from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, precision_recall_curve, average_precision_score
)

def compute_ml_evaluation_metrics(
    true_labels: List[Any],
    predicted_labels: List[Any],
    predicted_scores: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    Computes genuine classification and evaluation metrics using Scikit-Learn
    from real user-supplied arrays of true and predicted values.
    """
    y_true = np.array(true_labels)
    y_pred = np.array(predicted_labels)

    if len(y_true) == 0 or len(y_pred) == 0:
        raise ValueError("Evaluation arrays cannot be empty.")
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: {len(y_true)} true labels vs {len(y_pred)} predicted labels.")

    # Core classification metrics
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    unique_classes = sorted(list(set(y_true) | set(y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=unique_classes).tolist()

    cm_data = {
        "labels": [str(c) for c in unique_classes],
        "matrix": cm
    }

    roc_data = None
    pr_data = None

    if predicted_scores is not None and len(predicted_scores) == len(y_true):
        try:
            scores_arr = np.array(predicted_scores)
            # Binary classification ROC / PR evaluation
            if len(unique_classes) == 2:
                # Convert classes to 0 and 1
                pos_class = unique_classes[1]
                y_true_binary = (y_true == pos_class).astype(int)
                
                # If scores are 2D (probabilities for both classes), take column 1
                if scores_arr.ndim == 2 and scores_arr.shape[1] == 2:
                    scores_arr = scores_arr[:, 1]
                
                fpr, tpr, thresholds = roc_curve(y_true_binary, scores_arr)
                roc_auc = float(auc(fpr, tpr))
                
                precision_pts, recall_pts, pr_thresholds = precision_recall_curve(y_true_binary, scores_arr)
                avg_prec = float(average_precision_score(y_true_binary, scores_arr))

                # Subsample points if > 100 for clean visualization
                step_sub = max(1, len(fpr) // 100)
                roc_data = {
                    "fpr": [round(float(v), 4) for v in fpr[::step_sub]],
                    "tpr": [round(float(v), 4) for v in tpr[::step_sub]],
                    "auc": round(roc_auc, 4)
                }

                step_pr = max(1, len(precision_pts) // 100)
                pr_data = {
                    "precision": [round(float(v), 4) for v in precision_pts[::step_pr]],
                    "recall": [round(float(v), 4) for v in recall_pts[::step_pr]],
                    "average_precision": round(avg_prec, 4)
                }
        except Exception:
            # If scores format does not match curve requirements, pass gracefully
            pass

    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(prec, 4),
        "recall_macro": round(rec, 4),
        "f1_macro": round(f1, 4),
        "confusion_matrix": cm_data,
        "roc_curve": roc_data,
        "pr_curve": pr_data,
        "sample_count": len(y_true),
        "provenance_note": "computed from imported predictions via scikit-learn"
    }
