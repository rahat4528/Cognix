import io
import os
import sys
import tempfile
import pytest
import pandas as pd
import numpy as np

# Ensure backend path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from data_processing.ingestion import read_file_to_dataframe, save_dataframe_as_parquet, compute_sha256
from data_processing.profiling import infer_column_type, profile_dataframe

def test_csv_ingestion_and_bom_handling():
    # Test UTF-8 with BOM and semicolon delimiter
    csv_content = "\ufeffid;name;score;active\n1;Alpha;92.5;True\n2;Beta;88.0;False\n".encode("utf-8-sig")
    df, fmt = read_file_to_dataframe(csv_content, "test_data.csv")
    assert fmt == "csv"
    assert len(df) == 2
    assert "score" in df.columns
    assert df["score"].iloc[0] == 92.5

def test_parquet_and_json_ingestion():
    # Parquet
    df_orig = pd.DataFrame({"category": ["A", "B", "C"], "val": [10, 20, 30]})
    buffer = io.BytesIO()
    df_orig.to_parquet(buffer)
    parquet_bytes = buffer.getvalue()

    df_p, fmt_p = read_file_to_dataframe(parquet_bytes, "test.parquet")
    assert fmt_p == "parquet"
    assert len(df_p) == 3

    # JSON records
    json_bytes = df_orig.to_json(orient="records").encode("utf-8")
    df_j, fmt_j = read_file_to_dataframe(json_bytes, "test.json")
    assert fmt_j == "json"
    assert len(df_j) == 3

def test_corrupt_file_handling():
    corrupt_bytes = b"NOT_A_VALID_PARQUET_OR_DATASET_CONTENT_XYZ"
    with pytest.raises(Exception):
        read_file_to_dataframe(corrupt_bytes, "invalid.parquet")

def test_column_type_inference():
    int_series = pd.Series([1, 2, 3, 4])
    float_series = pd.Series([1.5, 2.7, 3.2])
    bool_series = pd.Series([True, False, True])
    date_series = pd.Series(["2025-01-01", "2025-01-02", "2025-01-03"])
    cat_series = pd.Series(["CatA", "CatB", "CatA", "CatA", "CatB"] * 20)

    assert infer_column_type(int_series) == "integer"
    assert infer_column_type(float_series) == "float"
    assert infer_column_type(bool_series) == "boolean"
    assert infer_column_type(date_series) in ["date", "datetime"]
    assert infer_column_type(cat_series) == "categorical"

def test_dataframe_profiling_and_quality_score():
    df = pd.DataFrame({
        "num": [10, 20, np.nan, 40],
        "cat": ["X", "Y", "X", "Y"],
        "id": [1, 2, 3, 4]
    })
    col_profiles, quality_report, score = profile_dataframe(df)
    
    assert len(col_profiles) == 3
    num_col = next(c for c in col_profiles if c["name"] == "num")
    assert num_col["null_count"] == 1
    assert num_col["statistics"]["min"] == 10.0
    assert num_col["statistics"]["max"] == 40.0
    
    # 1 null out of 12 total cells -> completeness is approx 91.6%
    assert quality_report["total_null_cells"] == 1
    assert score > 80.0
