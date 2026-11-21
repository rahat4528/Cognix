import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import duckdb
import numpy as np
import pandas as pd

ALLOWED_AGGREGATIONS = {"sum", "avg", "mean", "min", "max", "count", "median", "stddev"}
ALLOWED_TIME_INTERVALS = {"day", "week", "month", "quarter", "year"}

class ChartCompiler:
    def __init__(self, db_conn: duckdb.DuckDBPyConnection):
        self.conn = db_conn

    def _sanitize_ident(self, ident: str, allowed_columns: List[str]) -> str:
        """Ensures column identifier exists in the allowed schema and escapes it."""
        if ident not in allowed_columns:
            raise ValueError(f"Column '{ident}' is not in authorized dataset schema.")
        escaped = ident.replace('"', '""')
        return f'"{escaped}"'

    def _build_where_clause(self, filters: Optional[List[Dict[str, Any]]], allowed_columns: List[str]) -> Tuple[str, List[Any]]:
        """Builds a parameterized WHERE clause from filter definitions."""
        if not filters:
            return "", []
        
        clauses = []
        params = []
        for f in filters:
            col = f.get("column")
            op = f.get("operator", "==")
            val = f.get("value")
            
            if not col or col not in allowed_columns:
                continue
            
            sanitized_col = self._sanitize_ident(col, allowed_columns)
            
            if op == "==":
                clauses.append(f"{sanitized_col} = ?")
                params.append(val)
            elif op == "!=":
                clauses.append(f"{sanitized_col} != ?")
                params.append(val)
            elif op == ">":
                clauses.append(f"{sanitized_col} > ?")
                params.append(val)
            elif op == ">=":
                clauses.append(f"{sanitized_col} >= ?")
                params.append(val)
            elif op == "<":
                clauses.append(f"{sanitized_col} < ?")
                params.append(val)
            elif op == "<=":
                clauses.append(f"{sanitized_col} <= ?")
                params.append(val)
            elif op == "in" and isinstance(val, list):
                placeholders = ", ".join(["?"] * len(val))
                clauses.append(f"{sanitized_col} IN ({placeholders})")
                params.extend(val)
            elif op == "between" and isinstance(val, list) and len(val) == 2:
                clauses.append(f"{sanitized_col} BETWEEN ? AND ?")
                params.extend(val)
            elif op == "is_null":
                clauses.append(f"{sanitized_col} IS NULL")
            elif op == "not_null":
                clauses.append(f"{sanitized_col} IS NOT NULL")
        
        if clauses:
            return "WHERE " + " AND ".join(clauses), params
        return "", []

    def execute_chart_query(
        self,
        table_name: str,
        chart_type: str,
        config: Dict[str, Any],
        allowed_columns: List[str],
        global_filters: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compiles and executes an analytical query in DuckDB based on chart configuration.
        """
        start_time = time.perf_counter()
        chart_type = chart_type.upper()
        
        # Merge local and global filters
        combined_filters = (config.get("filters") or []) + (global_filters or [])
        where_sql, params = self._build_where_clause(combined_filters, allowed_columns)

        x_col = config.get("x_axis")
        y_col = config.get("y_axis")
        series_col = config.get("series")
        agg_raw = (config.get("aggregation") or "sum").lower()
        agg_fn = "avg" if agg_raw in ["mean", "avg"] else ("sum" if agg_raw not in ALLOWED_AGGREGATIONS else agg_raw)
        limit = min(int(config.get("limit") or 1000), 10000)

        sampled = False
        data_result: Any = {}

        if chart_type in ["BAR", "LINE", "AREA", "PIE", "DONUT", "MAP"]:
            if not x_col or x_col not in allowed_columns:
                raise ValueError("Valid X-axis column is required.")
            san_x = self._sanitize_ident(x_col, allowed_columns)

            if y_col and y_col in allowed_columns:
                san_y = self._sanitize_ident(y_col, allowed_columns)
                val_expr = f"{agg_fn.upper()}({san_y})"
            else:
                val_expr = "COUNT(*)"

            if series_col and series_col in allowed_columns:
                san_series = self._sanitize_ident(series_col, allowed_columns)
                query = f"""
                    SELECT {san_x} as x, {san_series} as series, {val_expr} as val
                    FROM {table_name}
                    {where_sql}
                    GROUP BY {san_x}, {san_series}
                    ORDER BY val DESC
                    LIMIT {limit}
                """
            else:
                query = f"""
                    SELECT {san_x} as x, {val_expr} as val
                    FROM {table_name}
                    {where_sql}
                    GROUP BY {san_x}
                    ORDER BY val DESC
                    LIMIT {limit}
                """

            res_df = self.conn.execute(query, params).df()
            data_result = res_df.to_dict(orient="records")

        elif chart_type == "TIME_SERIES":
            if not x_col or x_col not in allowed_columns:
                raise ValueError("Timestamp or Date column is required on X-axis.")
            san_x = self._sanitize_ident(x_col, allowed_columns)
            
            interval = config.get("time_interval", "day").lower()
            if interval not in ALLOWED_TIME_INTERVALS:
                interval = "day"
            
            if y_col and y_col in allowed_columns:
                san_y = self._sanitize_ident(y_col, allowed_columns)
                val_expr = f"{agg_fn.upper()}({san_y})"
            else:
                val_expr = "COUNT(*)"

            query = f"""
                SELECT date_trunc('{interval}', {san_x}) as timestamp, {val_expr} as val
                FROM {table_name}
                {where_sql}
                GROUP BY 1
                ORDER BY 1 ASC
                LIMIT {limit}
            """
            res_df = self.conn.execute(query, params).df()
            # Convert timestamps to ISO string
            if "timestamp" in res_df.columns:
                res_df["timestamp"] = res_df["timestamp"].astype(str)
            data_result = res_df.to_dict(orient="records")

        elif chart_type == "SCATTER":
            if not x_col or not y_col or x_col not in allowed_columns or y_col not in allowed_columns:
                raise ValueError("Both X-axis and Y-axis numeric columns are required for Scatter.")
            san_x = self._sanitize_ident(x_col, allowed_columns)
            san_y = self._sanitize_ident(y_col, allowed_columns)

            count_query = f"SELECT COUNT(*) FROM {table_name} {where_sql}"
            total_count = self.conn.execute(count_query, params).fetchone()[0]

            if total_count > 2000:
                sampled = True
                query = f"""
                    SELECT {san_x} as x, {san_y} as y
                    FROM {table_name} USING SAMPLE 2000
                    {where_sql}
                """
            else:
                query = f"""
                    SELECT {san_x} as x, {san_y} as y
                    FROM {table_name}
                    {where_sql}
                    LIMIT {limit}
                """
            res_df = self.conn.execute(query, params).df()
            data_result = res_df.to_dict(orient="records")

        elif chart_type == "HISTOGRAM":
            if not x_col or x_col not in allowed_columns:
                raise ValueError("Numeric column is required for Histogram.")
            san_x = self._sanitize_ident(x_col, allowed_columns)

            stats_query = f"SELECT MIN({san_x}), MAX({san_x}), COUNT({san_x}) FROM {table_name} {where_sql}"
            min_val, max_val, cnt = self.conn.execute(stats_query, params).fetchone()

            if cnt == 0 or min_val is None or max_val is None or min_val == max_val:
                data_result = {"bins": [], "counts": []}
            else:
                # Freedman-Diaconis or 20 bins default
                num_bins = int(config.get("bins") or 20)
                bin_width = (max_val - min_val) / num_bins
                
                query = f"""
                    SELECT 
                        FLOOR(({san_x} - {min_val}) / {bin_width}) as bin_idx,
                        COUNT(*) as count
                    FROM {table_name}
                    {where_sql}
                    GROUP BY bin_idx
                    ORDER BY bin_idx ASC
                """
                bin_df = self.conn.execute(query, params).df()
                
                bins = []
                counts = [0] * num_bins
                for i in range(num_bins):
                    low = min_val + i * bin_width
                    high = low + bin_width
                    bins.append({"bin_index": i, "x0": round(low, 4), "x1": round(high, 4)})
                
                for _, row in bin_df.iterrows():
                    idx = int(row["bin_idx"])
                    if 0 <= idx < num_bins:
                        counts[idx] = int(row["count"])
                    elif idx == num_bins: # edge case for max_val
                        counts[-1] += int(row["count"])

                data_result = {"bins": bins, "counts": counts}

        elif chart_type == "BOX_PLOT":
            if not y_col or y_col not in allowed_columns:
                raise ValueError("Numeric Y-axis column is required for Box Plot.")
            san_y = self._sanitize_ident(y_col, allowed_columns)

            group_clause = ""
            select_group = ""
            if x_col and x_col in allowed_columns:
                san_x = self._sanitize_ident(x_col, allowed_columns)
                select_group = f"{san_x} as group_name,"
                group_clause = f"GROUP BY {san_x}"

            query = f"""
                SELECT 
                    {select_group}
                    MIN({san_y}) as min_val,
                    quantile_cont({san_y}, 0.25) as q1,
                    quantile_cont({san_y}, 0.50) as median,
                    quantile_cont({san_y}, 0.75) as q3,
                    MAX({san_y}) as max_val,
                    COUNT({san_y}) as count
                FROM {table_name}
                {where_sql}
                {group_clause}
            """
            box_df = self.conn.execute(query, params).df()
            data_result = box_df.to_dict(orient="records")

        elif chart_type == "HEATMAP":
            if not x_col or not y_col or x_col not in allowed_columns or y_col not in allowed_columns:
                raise ValueError("Both X and Y category columns are required for Heatmap.")
            san_x = self._sanitize_ident(x_col, allowed_columns)
            san_y = self._sanitize_ident(y_col, allowed_columns)

            val_col = config.get("series")
            if val_col and val_col in allowed_columns:
                san_val = self._sanitize_ident(val_col, allowed_columns)
                val_expr = f"{agg_fn.upper()}({san_val})"
            else:
                val_expr = "COUNT(*)"

            query = f"""
                SELECT {san_x} as x, {san_y} as y, {val_expr} as val
                FROM {table_name}
                {where_sql}
                GROUP BY {san_x}, {san_y}
                LIMIT {limit}
            """
            heat_df = self.conn.execute(query, params).df()
            data_result = heat_df.to_dict(orient="records")

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "chart_type": chart_type,
            "data": data_result,
            "metadata": {
                "execution_time_ms": duration_ms,
                "cached": False,
                "sampled": sampled,
                "record_count": len(data_result) if isinstance(data_result, list) else 1
            }
        }
