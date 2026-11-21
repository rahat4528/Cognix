# Requirements Specification: Data Visualization Dashboard

## 1. Executive Summary
The **Data Visualization Dashboard** is an enterprise-grade analytics, data profiling, and visual intelligence application. It transforms raw tabular data (CSV, Parquet, JSON, Excel) into interactive charts, customizable grid dashboards, sandboxed SQL query views, and machine-learning experiment analytics. It does not train ML models; instead, it provides rigorous visualization and scikit-learn calculation of user-imported predictions and training metrics.

---

## 2. Functional Requirements

### 2.1 Authentication & Workspace Management
- **User Accounts**: Registration, authentication (JWT with access and refresh tokens, Argon2 password hashing), profile management.
- **Workspaces**: Hierarchical tenant scoping where datasets, dashboards, and queries belong to a workspace.
- **Role-Based Access Control (RBAC)**:
  - `OWNER`: Full administrative control, workspace settings, member management, deletion.
  - `ADMIN`: Dataset ingestion, member invitations, dashboard publishing, alert management.
  - `EDITOR`: Dataset creation/transformation, chart authoring, dashboard configuration, query authoring.
  - `VIEWER`: Read-only access to datasets, charts, dashboards, and exported reports.
- **Dashboard Permissions**: Private dashboards, workspace-shared dashboards, and token-based public share links with optional password protection and expiration dates.

### 2.2 Dataset Management & Ingestion
- **Supported Formats**: CSV, Parquet, JSON (records or split format), Excel (`.xlsx`), and connected SQL sources.
- **Storage**: Immutable raw file storage in object storage / local volume with version-tagged Parquet files.
- **Profiling & Quality Reports**:
  - Automatic column type inference: `integer`, `float`, `boolean`, `date`, `datetime`, `string`, `categorical`.
  - Missing-value count and percentage per column.
  - Duplicate row detection (across all columns and specified primary key subsets).
  - Descriptive statistics: min, max, mean, stddev, median, 25th/75th percentiles, cardinality.
  - Quality score computation based on completeness, uniqueness, and format validity.
- **Dataset Versioning**: Every ingestion and transformation step generates a distinct `DatasetVersion`, ensuring non-destructive operations.

### 2.3 Data Transformation Engine
- **Declarative Operations**:
  - Filter: Boolean expressions on column values.
  - Select / Drop Columns: Attribute subsetting.
  - Sort: Multi-column ascending/descending.
  - Type Conversion: Safe casting between types.
  - Date Parsing: Parsing custom timestamp strings with timezone handling.
  - Missing Value Handling: Drop, fill with scalar, mean, median, or mode.
  - Deduplication: Distinct row filtering by column keys.
  - Group By & Aggregation: Sum, Mean, Min, Max, Count, Standard Deviation.
  - Derived Columns: Safe mathematical expression evaluation (no arbitrary code execution / no `eval`).

### 2.4 Visualizations & Chart Builder
- **Supported Chart Types**:
  - Bar (standard, stacked, grouped)
  - Line & Area (multi-series, smoothed, cumulative)
  - Pie & Donut
  - Scatter (with automatic sampling for large volumes)
  - Histogram (configurable bin width, Freedman-Diaconis rule)
  - Box Plot (five-number summary: min, Q1, median, Q3, max, outliers)
  - Heatmap (2D binned frequency or aggregated metrics)
  - Time Series (with daily, weekly, monthly resampling)
  - Geographic Map (region code choropleth mapping)
- **Aggregation & Compilation**: All chart statistics are calculated server-side by DuckDB over columnar data.

### 2.5 Grid Dashboard Builder
- **Interactive Grid**: Dynamic multi-column layout with drag, resize, and reorder.
- **Global & Date Filters**: Scoped dashboard filters that dynamically filter charts tied to matching dataset columns.
- **Export Formats**: PDF export, CSV export of aggregated chart data, and JSON dashboard configuration templates.
- **Collaboration**: Optimistic concurrency control using version timestamps to prevent silent overwrite conflicts.

### 2.6 Sandboxed SQL Workspace
- **Execution Engine**: DuckDB over registered in-memory / Parquet views of authorized dataset versions.
- **Security Sandbox**:
  - External file and network access strictly disabled.
  - PRAGMA, INSTALL, LOAD, COPY, ATTACH, and filesystem functions blocked.
  - AST-based parser verification restricting queries to single read-only `SELECT` or `WITH` queries.
  - Execution timeout and row limits enforced.
- **Saved Queries & History**: Query versioning, execution logs with runtime and row counts.

### 2.7 Machine Learning Analytics
- **Import Formats**: CSV and JSON containing run identifiers, metric names, steps/epochs, and values.
- **Experiment Tracking**: Training/validation loss curves, accuracy curves, and cross-run comparisons.
- **Evaluation Metrics**:
  - When true labels and predicted probabilities/classes are imported, the system computes:
    - Confusion Matrix
    - Precision, Recall, and F1-score
    - ROC Curves and Area Under the Curve (AUC)
    - Precision-Recall (PR) Curves
  - All calculated via Scikit-learn on verified data, distinctly labeled as computed from imported data.

---

## 3. Non-Functional Requirements
- **Performance**: Chart queries on datasets up to 500,000 rows respond within 500ms using DuckDB columnar caching.
- **Security**: OWASP Top 10 compliance, input validation with Pydantic, CSRF protection, and SSRF prevention.
- **Reproducibility**: Complete traceability from raw upload to dataset version, transformation steps, and chart output.
