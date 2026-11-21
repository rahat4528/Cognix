import os
import hashlib
import io
import csv
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def compute_sha256(file_bytes: bytes) -> str:
    """Computes SHA-256 hash of bytes."""
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

def detect_csv_dialect(sample_text: str) -> Tuple[str, str]:
    """Detects delimiter and header presence in CSV text."""
    delimiters = [',', ';', '\t', '|']
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample_text, delimiters=delimiters)
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ','
    return delimiter

def read_file_to_dataframe(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """
    Parses uploaded file bytes (CSV, Parquet, JSON, Excel) into a pandas DataFrame.
    Returns (DataFrame, detected_format).
    """
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.csv', '.txt']:
        # Check encoding and BOM
        encoding = 'utf-8-sig' if file_bytes.startswith(b'\xef\xbb\xbf') else 'utf-8'
        try:
            sample_text = file_bytes[:8192].decode(encoding)
        except UnicodeDecodeError:
            encoding = 'latin1'
            sample_text = file_bytes[:8192].decode('latin1', errors='replace')
        
        delimiter = detect_csv_dialect(sample_text)
        buffer = io.BytesIO(file_bytes)
        df = pd.read_csv(buffer, encoding=encoding, sep=delimiter, low_memory=False)
        return df, 'csv'

    elif ext in ['.parquet', '.pq']:
        buffer = io.BytesIO(file_bytes)
        df = pd.read_parquet(buffer)
        return df, 'parquet'

    elif ext in ['.json']:
        buffer = io.BytesIO(file_bytes)
        try:
            # Try records orientation first
            df = pd.read_json(buffer, orient='records')
        except Exception:
            buffer.seek(0)
            df = pd.read_json(buffer)
        return df, 'json'

    elif ext in ['.xlsx', '.xls']:
        buffer = io.BytesIO(file_bytes)
        df = pd.read_excel(buffer)
        return df, 'xlsx'

    else:
        # Default fallback: try CSV sniffer
        try:
            buffer = io.BytesIO(file_bytes)
            df = pd.read_csv(buffer, low_memory=False)
            return df, 'csv'
        except Exception as e:
            raise ValueError(f"Unsupported file format for '{filename}'. Allowed: CSV, Parquet, JSON, XLSX. Error: {e}")

def save_dataframe_as_parquet(df: pd.DataFrame, storage_dir: str, version_id: str) -> Tuple[str, int]:
    """
    Saves a DataFrame as a standardized Parquet file.
    Returns (absolute_file_path, file_size_bytes).
    """
    os.makedirs(storage_dir, exist_ok=True)
    parquet_path = os.path.join(storage_dir, f"{version_id}.parquet")
    
    # Sanitize column names for parquet compatibility
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().replace(" ", "_") for c in df_clean.columns]
    
    table = pa.Table.from_pandas(df_clean)
    pq.write_table(table, parquet_path, compression='SNAPPY')
    
    file_size = os.path.getsize(parquet_path)
    return parquet_path, file_size
