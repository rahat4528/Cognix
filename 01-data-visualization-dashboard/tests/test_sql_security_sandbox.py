import os
import sys
import pytest
import duckdb
import pandas as pd

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from sql_sandbox.engine import (
    validate_sql_security, create_sandboxed_duckdb_connection,
    execute_sandboxed_query, SQLSandboxSecurityError
)

def test_valid_select_query():
    conn = create_sandboxed_duckdb_connection()
    df = pd.DataFrame({"id": [1, 2, 3], "val": [10, 20, 30]})
    conn.register("my_data", df)

    cols, rows, dur = execute_sandboxed_query(conn, "SELECT id, val FROM my_data WHERE val > 15")
    assert len(rows) == 2
    assert cols == ["id", "val"]
    conn.close()

def test_block_ddl_and_dml():
    # Attempting DROP TABLE
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("DROP TABLE users;")

    # Attempting INSERT
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("INSERT INTO users VALUES (1, 'hacker');")

    # Attempting UPDATE
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("UPDATE users SET admin = true;")

def test_block_filesystem_and_external_functions():
    # Attempting read_parquet or parquet_scan directly
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("SELECT * FROM read_parquet('/etc/passwd')")

    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("SELECT * FROM glob('../*')")

def test_block_multiple_statements():
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("SELECT 1; SELECT 2;")

def test_block_pragma_and_attach():
    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("PRAGMA version;")

    with pytest.raises(SQLSandboxSecurityError):
        validate_sql_security("ATTACH 'evil.db' AS evil;")
