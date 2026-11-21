# Technology Stack

Cognix leverages modern, industry-standard technologies across all three applications.

## Common Architecture Components

### Frontend
- **Framework**: Next.js 14+ (App Router), React 18+, TypeScript (Strict mode enabled)
- **Styling & Components**: Tailwind CSS, Radix UI primitives, Lucide React icons
- **Data Visualization & Editors**: Apache ECharts, Recharts, HTML5 Canvas, Monaco Editor

### Backend & Core Compute
- **Language**: Python 3.11+ / 3.13+
- **API Framework**: FastAPI, Pydantic v2
- **Database ORM & Migrations**: SQLAlchemy 2.0, Alembic
- **Asynchronous Task Workers**: Celery with Redis broker
- **Data Processing & ML**:
  - Columnar and tabular compute: DuckDB, Pandas, NumPy
  - Computer vision and deep learning: PyTorch, Torchvision, OpenCV, Pillow
  - Machine learning and recommendation algorithms: Scikit-learn, SciPy, pgvector
- **Testing & Quality Assurance**: Pytest, Pytest-Asyncio, HTTPX, Ruff, Mypy
