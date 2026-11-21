import os
import sys
import pytest
import pandas as pd
import numpy as np

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from data_processing.transformations import apply_transformation_step, execute_pipeline, evaluate_safe_expression

def test_filter_and_sort_transformations():
    df = pd.DataFrame({
        "product": ["Widget A", "Widget B", "Widget C", "Widget D"],
        "price": [10.0, 50.0, 25.0, 5.0],
        "stock": [100, 20, 50, 200]
    })

    # Filter price > 15
    step_filter = {"op": "filter", "params": {"column": "price", "operator": ">", "value": 15}}
    df_filtered = apply_transformation_step(df, step_filter)
    assert len(df_filtered) == 2
    assert set(df_filtered["product"]) == {"Widget B", "Widget C"}

    # Sort by price descending
    step_sort = {"op": "sort", "params": {"columns": ["price"], "ascending": False}}
    df_sorted = apply_transformation_step(df_filtered, step_sort)
    assert df_sorted.iloc[0]["product"] == "Widget B"
    assert df_sorted.iloc[1]["product"] == "Widget C"

def test_safe_ast_derived_columns():
    df = pd.DataFrame({
        "revenue": [100.0, 200.0, 500.0],
        "cost": [60.0, 110.0, 250.0]
    })

    # Safe math formula: (revenue - cost) / revenue
    result_series = evaluate_safe_expression(df, "(revenue - cost) / revenue")
    assert round(result_series.iloc[0], 2) == 0.40
    assert round(result_series.iloc[1], 2) == 0.45
    assert round(result_series.iloc[2], 2) == 0.50

    # Test math functions
    sqrt_series = evaluate_safe_expression(df, "sqrt(revenue)")
    assert round(sqrt_series.iloc[0], 2) == 10.0

def test_ast_security_rejections():
    df = pd.DataFrame({"a": [1, 2, 3]})
    
    # Arbitrary code execution or import attempts must fail
    with pytest.raises(ValueError):
        evaluate_safe_expression(df, "__import__('os').system('ls')")

    with pytest.raises(ValueError):
        evaluate_safe_expression(df, "eval('1 + 1')")

    with pytest.raises(ValueError):
        evaluate_safe_expression(df, "open('/etc/passwd').read()")

def test_deduplication_and_missing_values():
    df = pd.DataFrame({
        "user_id": [101, 102, 101, 103],
        "val": [10, np.nan, 10, 30]
    })

    # Deduplicate on user_id
    step_dedup = {"op": "deduplicate", "params": {"columns": ["user_id"]}}
    df_dedup = apply_transformation_step(df, step_dedup)
    assert len(df_dedup) == 3

    # Fill missing with mean
    step_fill = {"op": "fill_missing", "params": {"column": "val", "strategy": "mean"}}
    df_filled = apply_transformation_step(df, step_fill)
    assert not df_filled["val"].isna().any()
    assert round(df_filled.loc[1, "val"], 2) == round((10 + 10 + 30) / 3, 2)
