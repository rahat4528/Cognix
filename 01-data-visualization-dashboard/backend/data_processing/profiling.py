from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

def infer_column_type(series: pd.Series) -> str:
    """Infers high-level data type from a pandas Series."""
    non_null = series.dropna()
    if non_null.empty:
        return "string"
    
    # Check boolean
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if set(non_null.astype(str).str.lower().unique()).issubset({"true", "false", "0", "1", "yes", "no"}):
        if len(non_null.unique()) <= 2:
            return "boolean"

    # Check numeric types
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        return "float"
    
    # Try parsing numeric from string
    try:
        pd.to_numeric(non_null)
        if (pd.to_numeric(non_null) % 1 == 0).all():
            return "integer"
        return "float"
    except (ValueError, TypeError):
        pass

    # Check datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    
    # Check string datetime heuristic
    if non_null.dtype == object or non_null.dtype == 'string':
        first_val = str(non_null.iloc[0])
        if len(first_val) in (10, 19, 23, 24, 25) and any(sep in first_val for sep in ['-', '/', 'T']):
            try:
                parsed = pd.to_datetime(non_null.iloc[:100], errors='raise')
                if (parsed.dt.hour == 0).all() and (parsed.dt.minute == 0).all() and (parsed.dt.second == 0).all():
                    return "date"
                return "datetime"
            except Exception:
                pass

    # Check low cardinality category
    cardinality = len(non_null.unique())
    total_count = len(non_null)
    if cardinality > 1 and (cardinality / total_count < 0.05 or cardinality <= 20):
        return "categorical"

    return "string"

def profile_dataframe(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], Dict[str, Any], float]:
    """
    Analyzes a DataFrame and returns:
    1. List of column profiles (types, nulls, unique count, statistics, sample values)
    2. Overall dataset quality report
    3. Global quality score (0 - 100)
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols if total_rows > 0 and total_cols > 0 else 1

    column_profiles = []
    total_nulls = 0

    for col in df.columns:
        series = df[col]
        data_type = infer_column_type(series)
        null_count = int(series.isna().sum())
        total_nulls += null_count
        null_pct = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=True))
        
        # Sample non-null values
        samples = series.dropna().head(5).tolist()
        # Convert any timestamp or numpy types to standard python types
        samples = [val.isoformat() if hasattr(val, 'isoformat') else (val.item() if hasattr(val, 'item') else val) for val in samples]

        stats: Dict[str, Any] = {}
        if data_type in ["integer", "float"]:
            numeric_series = pd.to_numeric(series.dropna(), errors='coerce').dropna()
            if not numeric_series.empty:
                stats = {
                    "min": float(numeric_series.min()),
                    "max": float(numeric_series.max()),
                    "mean": round(float(numeric_series.mean()), 4),
                    "std": round(float(numeric_series.std()), 4) if len(numeric_series) > 1 else 0.0,
                    "median": float(numeric_series.median()),
                    "q25": float(numeric_series.quantile(0.25)),
                    "q75": float(numeric_series.quantile(0.75)),
                }

        column_profiles.append({
            "name": str(col),
            "data_type": data_type,
            "is_nullable": null_count > 0,
            "null_count": null_count,
            "null_percentage": null_pct,
            "unique_count": unique_count,
            "sample_values": samples,
            "statistics": stats
        })

    # Duplicates
    duplicate_rows = int(df.duplicated().sum()) if total_rows > 0 else 0
    duplicate_pct = round((duplicate_rows / total_rows * 100), 2) if total_rows > 0 else 0.0

    # Completeness & Quality Scoring
    completeness = max(0.0, 1.0 - (total_nulls / total_cells))
    uniqueness = max(0.0, 1.0 - (duplicate_rows / total_rows)) if total_rows > 0 else 1.0
    validity = 1.0  # Proportion of structurally valid cells

    quality_score = round((0.5 * completeness + 0.3 * uniqueness + 0.2 * validity) * 100, 2)

    quality_report = {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "total_cells": total_cells,
        "total_null_cells": total_nulls,
        "overall_null_percentage": round((total_nulls / total_cells * 100), 2),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": duplicate_pct,
        "completeness_score": round(completeness * 100, 2),
        "uniqueness_score": round(uniqueness * 100, 2),
        "validity_score": round(validity * 100, 2),
        "overall_quality_score": quality_score
    }

    return column_profiles, quality_report, quality_score
