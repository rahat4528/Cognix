# Repository Overview

**Cognix** is a multi-project repository containing three independent, production-grade applications in artificial intelligence and machine learning:

1. **Data Visualization Dashboard (`01-data-visualization-dashboard`)**:
   An analytical workspace enabling users to ingest datasets, perform declarative multi-step transformations, construct interactive multi-series charts and grid dashboards, query data using secure sandboxed DuckDB SQL, and track real machine-learning experiment metrics.

2. **Image Recognition App (`02-image-recognition-app`)**:
   A computer vision platform offering classification, multi-object detection with canvas overlays, segmentation, real-time camera inference with bounded latency, vector similarity search, and model fine-tuning.

3. **Recommendation System (`03-recommendation-system`)**:
   A personalization and ranking suite featuring collaborative filtering, content-based matching, sequential models, and hybrid ranking algorithms, supported by real-time re-ranking, offline metric evaluation, and an operational management dashboard.

---

## Organizational Structure

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
│   └── final-delivery-report.md (post Phase 3)
├── 01-data-visualization-dashboard/
├── 02-image-recognition-app/
└── 03-recommendation-system/
```

Each application is self-contained with its own frontend, backend, database migrations, configuration, and automated test suite.
