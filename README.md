# Cognix

**Cognix** is a suite of three independent, standalone, production-quality artificial intelligence and machine learning applications. Each project is architected with its own dedicated frontend, backend, database, test suite, and operational environment, operating completely independently without cross-dependencies or shared single points of failure.

---

## The Applications

### 1. [01-data-visualization-dashboard](./01-data-visualization-dashboard) — Data Visualization Dashboard
A modern analytics and business intelligence workspace for exploring structured data and machine-learning experiment metrics.
- **Key Features**: Multi-format dataset ingestion (CSV, Parquet, JSON, XLSX), schema detection, data profiling, transformation pipelines with immutable versioning, custom chart builder (ECharts/Plotly), interactive grid dashboards with global date/dimension filters, secure sandboxed SQL analytics (DuckDB), and machine learning experiment tracking (loss/accuracy curves, confusion matrices, ROC/PR curves).
- **Core Stack**: Next.js, React, TypeScript, Tailwind CSS, Monaco Editor, Apache ECharts, FastAPI, DuckDB, Pandas, SQLAlchemy, Redis, Celery.

### 2. [02-image-recognition-app](./02-image-recognition-app) — Image Recognition App
A computer vision workbench for real-time and batch image intelligence.
- **Key Features**: High-throughput image classification, multi-object detection with interactive canvas bounding-box inspection and class filtering, semantic/instance segmentation masks, live camera feed processing with frame throttling and latency metrics, image similarity search via vector embeddings, and custom dataset management with fine-tuning pipelines.
- **Core Stack**: Next.js, React, TypeScript, HTML5 Canvas, FastAPI, PyTorch, Torchvision, OpenCV, Pillow, PostgreSQL with pgvector, Redis, Celery.

### 3. [03-recommendation-system](./03-recommendation-system) — Recommendation System
An end-to-end personalization and content discovery engine with real-time serving and operational controls.
- **Key Features**: Multi-model recommendation algorithms (collaborative filtering, matrix factorization, content-based TF-IDF, sequential models, and hybrid weighted ranking), real-time re-ranking from live event streams, cold-start onboarding workflows, transparent recommendation explanations, A/B testing framework, and an administrative operations console with offline metric evaluations.
- **Core Stack**: Next.js, React, TypeScript, Recharts, FastAPI, Scikit-learn, Implicit, PyTorch, PostgreSQL with pgvector, Redis, Celery, MLflow.

---

## Architectural Principles

1. **Strict Application Independence**: Each application contains its own decoupled frontend, API services, database instances (`cognix_dataviz_db`, `cognix_image_recognition_db`, `cognix_recommendation_db`), worker queues, and configuration files. No application requires another to run.
2. **Authentic AI & Scientific Integrity**: All analytical metrics, model evaluations, predictions, and recommendations are computed via verified algorithms and reproducible pipelines. Hardcoded inferences, mocked recommendations, or invented metrics are strictly forbidden.
3. **Reproducibility & Lineage**: Model architectures, random seeds, hyperparameter settings, dataset versions, and evaluation metrics are captured in version-controlled documentation cards and evaluation artifacts.
4. **Defense in Depth**: Robust authentication, role-based authorization, query sandboxing, upload sanitization, short-lived signed URLs, rate limiting, and comprehensive audit trails protect user data and compute resources.

---

## Directory Structure

```text
Cognix/
├── README.md
├── LICENSE
├── .gitignore
├── PROGRESS.md
├── docs/
│   ├── repository-overview.md
│   ├── architecture.md
│   ├── technology-stack.md
│   ├── development-guide.md
│   ├── ml-engineering-guide.md
│   └── project-index.md
├── 01-data-visualization-dashboard/
│   ├── frontend/
│   ├── backend/
│   ├── database/
│   ├── data-processing/
│   ├── visualization/
│   ├── tests/
│   ├── docs/
│   ├── docker-compose.yml
│   └── README.md
├── 02-image-recognition-app/
├── 03-recommendation-system/
```

---

## Global Setup & Requirements

- **Runtime Environments**: Python 3.11+ / 3.13+, Node.js 20+, Docker & Docker Compose.
- **Quick Start**: Refer to each application directory for detailed setup, database migration, and test execution instructions.
- **Documentation**: Detailed design guides, technology decisions, and machine-learning engineering standards are cataloged in [`docs/`](./docs).
