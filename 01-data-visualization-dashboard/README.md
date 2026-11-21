# Data Visualization Dashboard

**Data Visualization Dashboard** is an enterprise-grade analytics workspace and data visualization suite. It empowers data teams to ingest, explore, transform, and visualize structured datasets, execute secure analytical SQL queries in an isolated DuckDB sandbox, and track real machine-learning experiment metrics and evaluation curves.

---

## Key Features

- **Multi-Format Ingestion**: Ingest CSV, Parquet, JSON, and Excel (`.xlsx`) datasets with automatic delimiter, BOM, and character encoding detection.
- **Automated Profiling & Quality Scoring**: Automatic column data type inference, null statistics, duplicate detection, cardinality metrics, and comprehensive data health reports.
- **Immutable Transformation Engine**: Declarative multi-step data pipelines (filtering, column selection, casting, date parsing, missing value imputation, deduplication, aggregation, and derived columns via a secure AST math evaluator). Every transform produces a new `DatasetVersion` leaving raw data pristine.
- **Server-Side Chart Computation**: High-performance DuckDB query compilation for Bar, Line, Area, Pie, Donut, Scatter (with density sampling), Histogram (Freedman-Diaconis binning), Box Plot (five-number summary), Heatmap, Time-Series resampling, and Geographic choropleths.
- **Dynamic Grid Dashboards**: Drag-and-drop grid layouts, scoped global and date range filters, optimistic concurrency versioning, and revocable public share links.
- **Sandboxed SQL Studio**: High-speed analytical queries executed in a tightly restricted DuckDB instance (zero filesystem/network access, single-statement SELECT validation, timeout and row limits).
- **ML Experiment Analytics**: Track training/validation loss and accuracy curves across runs. Compute confusion matrices, Precision, Recall, F1, ROC, and PR curves directly from imported predictions via Scikit-learn.

---

## Architecture & Technology Stack

| Layer | Technologies | Justification |
|---|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Monaco Editor, Apache ECharts | Strict typing, responsive reactive grids, modular charting, code editor ergonomics. |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2 | High-throughput async HTTP, automatic OpenAPI documentation, schema validation. |
| **Analytical Engine** | DuckDB, Pandas, NumPy, PyArrow | In-memory columnar processing, zero-copy Parquet queries, rapid aggregations. |
| **ML Metrics Engine** | Scikit-learn | Verified statistical and classification evaluation metrics calculation. |
| **Database & ORM** | PostgreSQL (or SQLite for zero-config dev), SQLAlchemy 2.0, Alembic | ACID transactions, relational integrity, seamless schema migrations. |
| **Caching & Workers** | Redis, Celery | Async background processing for heavy exports and query result caching. |
| **Storage** | MinIO / Local File Storage Adapter | Immutable object storage with SHA-256 validation. |

---

## Directory Structure

```text
01-data-visualization-dashboard/
├── backend/
│   ├── api/                  # FastAPI REST routes (auth, datasets, charts, dashboards, sql, ml)
│   ├── core/                 # Config, security, database sessions, auth middleware
│   ├── data_processing/      # Ingestion, profiling, transformation engine, AST evaluator
│   ├── visualization/        # Chart query compiler, binning, box plot stats, caching
│   ├── sql_sandbox/          # DuckDB sandbox, query AST validator, timeout limits
│   ├── ml_analytics/         # Scikit-learn evaluation metrics, loss/acc curves
│   ├── models/               # SQLAlchemy 2.0 database models
│   ├── schemas/              # Pydantic v2 schemas
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   ├── alembic/              # Database migration scripts
│   ├── alembic.ini
│   └── seed.py               # Deterministic seed script with demo datasets and users
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # UI widgets, chart renderers, grid layouts, SQL editor
│   │   └── lib/              # API clients, chart options builders, utilities
│   ├── package.json
│   └── Dockerfile
├── docs/                     # Specifications, architecture, API, and completion report
├── tests/                    # Comprehensive unit, integration, security, and ML tests
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Local Setup & Quick Start

### 1. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Initialize Database & Seed Demo Data
The application defaults to local SQLite for instant zero-setup development, or PostgreSQL via `DATABASE_URL`:
```bash
python -m database.seed
```
Default accounts seeded:
- Admin: `admin@cognix.local` / `AdminPass123!`
- Analyst: `analyst@cognix.local` / `AnalystPass123!`

### 4. Run the Backend API
```bash
uvicorn api.main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

### 5. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Running the Automated Test Suite

Run all backend, analytical, security, and ML calculation tests:
```bash
pytest tests/ -v
```

---

## Security & Limitations

### Sandboxed SQL Security
DuckDB query execution is sandboxed with:
1. `enable_external_access = false` (no remote network or local file I/O).
2. AST validation strictly enforcing single-statement `SELECT` / `WITH` read-only queries. Multiple statements, `PRAGMA`, `ATTACH`, `INSTALL`, and DDL/DML are rejected before evaluation.
3. Execution timeout (default 15s) and maximum row limit (default 10,000 rows).

### Known Limitations
- Excel (`.xlsx`) files are limited to 20MB because Excel formats cannot be efficiently streamed.
- PDF dashboard export requires Chromium or ReportLab installed in the server environment.
