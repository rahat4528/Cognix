# Architecture: Data Visualization Dashboard

## System Overview

The **Data Visualization Dashboard** is designed around a decoupled, service-oriented architecture:

```text
+-----------------------------------------------------------------------------------+
|                                Next.js Frontend                                   |
|   Dataset Explorer | Chart Builder | Grid Dashboards | SQL Studio | ML Analytics  |
+-----------------------------------------------------------------------------------+
                                         |  HTTPS / REST / WebSocket
                                         v
+-----------------------------------------------------------------------------------+
|                                FastAPI Backend                                    |
|   Auth & RBAC | Ingestion Router | Transformation Router | Chart Engine | SQL Sandbox|
+-----------------------------------------------------------------------------------+
       |                    |                       |                    |
       v                    v                       v                    v
+--------------+   +-------------------+   +------------------+   +-----------------+
|  PostgreSQL  |   |    DuckDB Core    |   |   Redis Cache    |   | Object Storage  |
| (Metadata &  |   | (Columnar Queries |   | (Query Caching & |   |  (Immutable Raw |
|  App State)  |   |  & ML Transforms) |   | Task Brokerage)  |   | & Parquet Files)|
+--------------+   +-------------------+   +------------------+   +-----------------+
                            ^                       ^
                            |                       |
               +-------------------------------------------+
               |               Celery Worker               |
               | (File Parsing, Quality Reports, Exports)  |
               +-------------------------------------------+
```

---

## 1. Data Ingestion & Storage Pipeline
1. **Raw Storage**: Raw uploaded files (`.csv`, `.parquet`, `.json`, `.xlsx`) are stored immutably in object storage (or local storage adapter) with SHA-256 integrity hashes.
2. **Standardization**: Ingestion jobs convert all tabular data to standardized Parquet files partitioned or indexed for DuckDB.
3. **Metadata Indexing**: Schema metadata (columns, data types, null rates, cardinality) is extracted and stored in `dataset_columns` and `dataset_versions` in PostgreSQL.

---

## 2. In-Memory & Columnar Query Engine
- **DuckDB**: Embedded analytical engine providing zero-copy reading of Parquet datasets.
- **Query Sandboxing**:
  - DuckDB is configured with `enable_external_access = false`.
  - Allowed operations: Pure read-only analytical queries against authorized dataset version tables registered as temporary in-memory views.
- **Query Cache**: Query results are cached in Redis using a composite key: `hash(dataset_version_id, query_ast_or_spec)`.

---

## 3. Database Schema (PostgreSQL)

### Core Models
- `User`: User accounts with Argon2 password hashes.
- `Workspace`: Tenant boundaries for team collaboration.
- `WorkspaceMember`: Associates users with workspaces under roles (`OWNER`, `ADMIN`, `EDITOR`, `VIEWER`).
- `Dataset`: Top-level dataset metadata entity.
- `DatasetVersion`: Versioned snapshots of datasets pointing to Parquet storage paths.
- `DatasetColumn`: Schema metadata (name, inferred_type, null_count, sample_values).
- `DataTransformation`: JSON-encoded sequence of transformation steps generating derived versions.
- `Chart`: Visualization definitions including type, encodings (X, Y, Series), filters, and styling.
- `Dashboard`: Composite layout entity containing multiple charts in a grid arrangement.
- `DashboardChart`: Mapping between dashboards and charts with layout coordinates (`x`, `y`, `w`, `h`).
- `SavedQuery`: SQL queries stored by users.
- `QueryExecution`: Execution history and performance telemetry.
- `MLExperiment`: Metadata container for ML experiments.
- `ModelMetric`: Epoch/step metric records (loss, accuracy, custom values).
- `MLPrediction`: Evaluation arrays (true labels, predicted scores) for confusion matrices and ROC curves.
- `DataAlert`: Threshold-based alerts monitoring dataset aggregations.
- `AuditLog`: System audit logging for security compliance.
