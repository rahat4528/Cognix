import os
import sys
import pytest
import duckdb
import pandas as pd
import numpy as np

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from visualization.chart_compiler import ChartCompiler

@pytest.fixture
def test_duckdb():
    conn = duckdb.connect(":memory:")
    # Seed known test dataset
    df = pd.DataFrame({
        "region": ["North", "North", "South", "South", "East"],
        "sales": [100.0, 200.0, 150.0, 250.0, 300.0],
        "score": [10, 25, 40, 55, 70]
    })
    conn.register("sales_data", df)
    yield conn, df
    conn.close()

def test_bar_chart_aggregation(test_duckdb):
    conn, df = test_duckdb
    compiler = ChartCompiler(conn)

    result = compiler.execute_chart_query(
        table_name="sales_data",
        chart_type="BAR",
        config={"x_axis": "region", "y_axis": "sales", "aggregation": "sum"},
        allowed_columns=["region", "sales", "score"]
    )

    data = result["data"]
    # Reference pandas calculation
    pandas_agg = df.groupby("region")["sales"].sum().to_dict()
    
    for row in data:
        reg = row["x"]
        val = row["val"]
        assert val == pandas_agg[reg]

def test_box_plot_five_number_summary(test_duckdb):
    conn, df = test_duckdb
    compiler = ChartCompiler(conn)

    result = compiler.execute_chart_query(
        table_name="sales_data",
        chart_type="BOX_PLOT",
        config={"y_axis": "sales"},
        allowed_columns=["region", "sales", "score"]
    )

    summary = result["data"][0]
    assert summary["min_val"] == 100.0
    assert summary["max_val"] == 300.0
    assert summary["median"] == 200.0
    assert summary["q1"] == 150.0
    assert summary["q3"] == 250.0

def test_histogram_binning(test_duckdb):
    conn, df = test_duckdb
    compiler = ChartCompiler(conn)

    result = compiler.execute_chart_query(
        table_name="sales_data",
        chart_type="HISTOGRAM",
        config={"x_axis": "score", "bins": 3},
        allowed_columns=["region", "sales", "score"]
    )

    hist_data = result["data"]
    assert len(hist_data["bins"]) == 3
    # Total counts must sum to 5 rows
    assert sum(hist_data["counts"]) == 5

def test_column_allowlist_enforcement(test_duckdb):
    conn, df = test_duckdb
    compiler = ChartCompiler(conn)

    # Attempting to query an unauthorized or malicious column identifier must fail
    with pytest.raises(ValueError):
        compiler.execute_chart_query(
            table_name="sales_data",
            chart_type="BAR",
            config={"x_axis": "unauthorized_secret_col", "y_axis": "sales"},
            allowed_columns=["region", "sales"]
        )
