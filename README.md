# Cognix

**Cognix** is an enterprise-grade suite of three independent, standalone, production-quality artificial intelligence and machine learning applications. Each project is architected with its own dedicated frontend, backend, database, test suite, and operational environment, operating completely independently without cross-dependencies or shared single points of failure.

---

## The Applications

| Application | Project Folder | Frontend | Backend Gateway | Primary Models & Technologies | Test Suite |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **Data Visualization Dashboard** | [`01-data-visualization-dashboard`](./01-data-visualization-dashboard) | Port 3000 | Port 8000 | DuckDB, Apache ECharts, Scikit-learn Linear Regression | **22/22 (100%)** |
| **Image Recognition App** | [`02-image-recognition-app`](./02-image-recognition-app) | Port 3001 | Port 8000 (Inference: 8001) | PyTorch, MobileNetV3-Small, SSDLite320, Grad-CAM | **17/17 (100%)** |
| **Recommendation System** | [`03-recommendation-system`](./03-recommendation-system) | Port 3002 | Port 8002 | Truncated SVD, TF-IDF Cosine, First-Order Markov, Hybrid Ensemble | **16/16 (100%)** |

---

### 1. [01-data-visualization-dashboard](./01-data-visualization-dashboard) — Data Visualization Dashboard
A modern analytics and business intelligence workspace for exploring structured data and machine-learning experiment metrics.
- **Key Features**: Multi-format dataset ingestion (CSV, Parquet, JSON, XLSX), schema detection, data profiling, transformation pipelines with immutable versioning, custom chart compiler, interactive grid dashboards with global date/dimension filters, secure sandboxed SQL analytics (DuckDB), and real linear regression forecasting and anomaly detection.
- **Core Stack**: Next.js 14, React 18, TypeScript, Tailwind CSS, Monaco Editor, Apache ECharts, FastAPI, DuckDB, Pandas, SQLAlchemy.
- **Documentation**: [`01-data-visualization-dashboard/docs/completion-report.md`](./01-data-visualization-dashboard/docs/completion-report.md)

### 2. [02-image-recognition-app](./02-image-recognition-app) — Image Recognition App
A computer vision workbench for real-time and batch image intelligence.
- **Key Features**: High-throughput image classification, multi-object detection with interactive HTML5 canvas bounding-box inspection and class filtering, Grad-CAM visual explainability overlays with scientific disclosure notices, live camera feed processing with frame throttling and latency metrics, image similarity search via 576-dim normalized vector embeddings, and privacy-safeguarded cascading deletion.
- **Core Stack**: Next.js 14, React 18, TypeScript, HTML5 Canvas, FastAPI, PyTorch, Torchvision, OpenCV, Pillow.
- **Documentation**: [`02-image-recognition-app/docs/completion-report.md`](./02-image-recognition-app/docs/completion-report.md)

### 3. [03-recommendation-system](./03-recommendation-system) — Recommendation System
An end-to-end personalization and content discovery engine with real-time serving and operational controls.
- **Key Features**: Multi-model recommendation algorithms (Collaborative Truncated SVD, Content-Based TF-IDF, Sequential First-Order Markov Chains, and Dynamic Hybrid Ensemble Ranker), real-time re-ranking from live event streams, cold-start onboarding workflows, live A/B testing framework, and an offline evaluation suite with strict chronological train/val/test splits (NDCG@10, Recall@10, MAP@10, Coverage).
- **Core Stack**: Next.js 14, React 18, TypeScript, Tailwind CSS, FastAPI, Scikit-learn, SciPy, Pandas, SQLAlchemy.
- **Documentation**: [`03-recommendation-system/docs/completion-report.md`](./03-recommendation-system/docs/completion-report.md)

---

## Architectural Principles

1. **Strict Application Independence**: Each application contains its own decoupled frontend, API services, database instances (`cognix_dataviz_db`, `cognix_image_recognition_db`, `cognix_recommendation_db`), worker queues, and configuration files. No application requires another to run.
2. **Authentic AI & Scientific Integrity**: All analytical metrics, model evaluations, predictions, and recommendations are computed via verified algorithms and reproducible pipelines. Hardcoded inferences, mocked recommendations, or invented metrics are strictly forbidden.
3. **Reproducibility & Lineage**: Model architectures, random seeds, hyperparameter settings, dataset versions, and evaluation metrics are captured in version-controlled documentation cards and evaluation artifacts.
4. **Defense in Depth**: Robust authentication, role-based authorization, query sandboxing, upload sanitization, EXIF stripping, 25MP decompression bomb limits, rate limiting, and comprehensive audit trails protect user data and compute resources.

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
│   ├── project-index.md
│   └── final-delivery-report.md
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
│   ├── frontend/
│   ├── backend/
│   ├── database/
│   ├── inference/
│   ├── tests/
│   ├── docs/
│   ├── docker-compose.yml
│   └── README.md
└── 03-recommendation-system/
    ├── frontend/
    ├── backend/
    ├── database/
    ├── recommendation_engine/
    ├── data_processing/
    ├── model_training/
    ├── model_evaluation/
    ├── tests/
    ├── docs/
    ├── docker-compose.yml
    └── README.md
```

---

## Global Setup & Requirements

- **Runtime Environments**: Python 3.11+ / 3.13+, Node.js 20+, Docker & Docker Compose.
- **Quick Start**: Refer to each application directory for detailed setup, database migration, and test execution instructions.
- **Repository Documentation**: Detailed architectural specifications, technology decisions, and delivery logs are cataloged in [`docs/`](./docs) and [`docs/final-delivery-report.md`](./docs/final-delivery-report.md).
