import re
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
import duckdb

FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b", r"\bCREATE\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bPRAGMA\b", r"\bATTACH\b", r"\bDETACH\b",
    r"\bCOPY\b", r"\bINSTALL\b", r"\bLOAD\b", r"\bEXPORT\b", r"\bIMPORT\b",
    r"\bSET\b", r"\bCALL\b", r"\bEXECUTE\b", r"\bVACUUM\b", r"\bCHECKPOINT\b"
]

FORBIDDEN_FUNCTIONS = [
    r"\bread_parquet\b", r"\bread_csv\b", r"\bread_json\b", r"\bread_csv_auto\b",
    r"\bscan_parquet\b", r"\bscan_csv\b", r"\bparquet_scan\b", r"\bglob\b",
    r"\bread_text\b", r"\bwrite_parquet\b", r"\bwrite_csv\b"
]

class SQLSandboxSecurityError(Exception):
    pass

def validate_sql_security(sql_text: str):
    """
    Strictly validates that the query is a single read-only SELECT or WITH statement.
    Rejects DDL, DML, PRAGMA, COPY, ATTACH, multi-statements, and filesystem scan functions.
    """
    clean_sql = sql_text.strip()
    if not clean_sql:
        raise SQLSandboxSecurityError("Query text cannot be empty.")

    # Remove trailing semicolons
    clean_sql = re.sub(r";+\s*$", "", clean_sql)

    # Check for multiple statements
    # Simple check for semicolon outside quotes
    in_single_quote = False
    in_double_quote = False
    for ch in clean_sql:
        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif ch == ';' and not in_single_quote and not in_double_quote:
            raise SQLSandboxSecurityError("Multiple SQL statements are strictly forbidden.")

    # Must start with SELECT or WITH
    upper_query = clean_sql.upper()
    if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
        raise SQLSandboxSecurityError("Only read-only SELECT or WITH statements are allowed.")

    # Check forbidden keywords
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, clean_sql, re.IGNORECASE):
            matched = re.search(pattern, clean_sql, re.IGNORECASE).group()
            raise SQLSandboxSecurityError(f"Forbidden keyword '{matched}' detected in query.")

    # Check forbidden filesystem / external scan functions
    for pattern in FORBIDDEN_FUNCTIONS:
        if re.search(pattern, clean_sql, re.IGNORECASE):
            matched = re.search(pattern, clean_sql, re.IGNORECASE).group()
            raise SQLSandboxSecurityError(f"Direct file reading function '{matched}' is disabled.")

def create_sandboxed_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Creates a memory-bounded, locked-down DuckDB in-memory instance."""
    conn = duckdb.connect(":memory:")
    # Lock down external and filesystem access
    conn.execute("SET enable_external_access = false;")
    conn.execute("SET max_memory = '512MB';")
    return conn

def execute_sandboxed_query(
    conn: duckdb.DuckDBPyConnection,
    sql_text: str,
    timeout_seconds: int = 15,
    max_rows: int = 10000
) -> Tuple[List[str], List[Dict[str, Any]], float]:
    """
    Executes a validated query in DuckDB within a timeout and row limit.
    Returns (column_names, rows_as_dicts, duration_ms).
    """
    validate_sql_security(sql_text)
    
    start_time = time.perf_counter()
    
    # We wrap execution with an interrupt timer to enforce hard timeout
    timer = None
    try:
        if timeout_seconds > 0:
            timer = threading.Timer(timeout_seconds, conn.interrupt)
            timer.start()

        # Wrap query to enforce hard max_rows limit if not already limited
        wrapped_query = f"SELECT * FROM ({sql_text}) AS _cognix_subq LIMIT {max_rows}"
        res = conn.execute(wrapped_query)
        df = res.df()
    finally:
        if timer:
            timer.cancel()

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    columns = list(df.columns)
    
    # Clean NaN / inf to None for JSON serialization
    clean_df = df.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
    rows = clean_df.to_dict(orient="records")

    return columns, rows, duration_ms
