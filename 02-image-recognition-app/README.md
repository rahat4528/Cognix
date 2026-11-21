# Image Recognition App

**Image Recognition App** is a computer-vision workbench and model serving platform. It provides high-throughput classification, multi-object detection with interactive HTML5 Canvas bounding-box inspection and per-class visibility toggles, live webcam frame streaming with persistent visual indicators, vector similarity search, and explainability via Grad-CAM saliency overlays.

---

## Key Features

- **Genuine Neural Network Inference**: Classification via MobileNetV3-Small (1,000 ImageNet classes) and object detection via SSDLite320-MobileNetV3-Large (80 COCO categories). Zero mocked or synthetic outputs.
- **Microservice Isolation**: The computer vision inference engine runs as a completely decoupled microservice in `inference/` with no database access or end-user credential exposure.
- **Upload Sanitization & Privacy**: Enforces Pillow image decode verification, decompression bomb limits (max 25 MP), automatic EXIF orientation normalization, and stripping of GPS location telemetry.
- **Interactive Canvas Overlays**: Bounding boxes returned in original pixel coordinates and normalized ranges, rendered on HTML5 Canvas with per-class toggles, confidence score tooltips, and COCO/JSON/CSV exports.
- **Live Camera Stream**: Explicit permission prompt, persistent red "CAMERA ACTIVE" indicator, frame throttling (max 5 FPS), live round-trip latency metrics, and zero frame persistence unless a snapshot is explicitly taken.
- **Vector Similarity Search**: High-dimensional penultimate feature embeddings queried strictly against the user's private library of uploaded assets.
- **Explainability**: Integrated Grad-CAM feature attribution heatmaps labeled "approximate explanation".

---

## Architecture & Technology Stack

| Layer | Technologies | Justification |
|---|---|---|
| **Frontend** | Next.js 14, React 18, TypeScript, HTML5 Canvas, Tailwind CSS, Lucide Icons | Responsive image manipulation, sub-millisecond canvas bounding box rendering. |
| **Main Web API** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 | Async upload handling, user authentication, asset management, cascading deletion. |
| **Inference Service** | Python 3.11+, PyTorch, Torchvision, Pillow, OpenCV | High-speed forward-pass execution, safe `weights_only=True` model loading. |
| **Database & Vectors** | PostgreSQL with pgvector (or SQLite vector cosine fallback for zero-config dev) | ACID metadata storage, high-dimensional vector similarity indexing. |
| **Caching & Queues** | Redis | Streaming buffer and frame rate throttling. |

---

## Directory Structure

```text
02-image-recognition-app/
├── backend/                  # Main Web API
│   ├── api/                  # FastAPI routers (auth, images, inference proxy, history)
│   ├── core/                 # Config, security, database sessions
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic v2 schemas
│   ├── preprocessing/        # Pillow decode, EXIF strip, decompression bomb defense
│   ├── Dockerfile
│   └── requirements.txt
├── inference/                # Isolated Inference Microservice
│   ├── models/               # PyTorch MobileNetV3, SSDLite, Grad-CAM, Embeddings
│   ├── service.py            # Authenticated internal inference API
│   ├── Dockerfile
│   └── requirements.txt
├── database/                 # Migrations and seed scripts
│   ├── alembic/
│   └── seed.py
├── frontend/                 # Next.js CV Workbench
│   ├── src/
│   │   ├── app/              # Next.js App Router (upload, detection, camera, history)
│   │   ├── components/       # Canvas overlays, top-k bars, camera controls
│   │   └── lib/              # API clients, types
│   ├── package.json
│   └── Dockerfile
├── docs/                     # Specifications, architecture, API, and model cards
│   ├── requirements.md
│   ├── architecture.md
│   ├── api.md
│   └── models/
├── tests/                    # Unit, integration, model determinism, and privacy tests
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Local Setup & Quick Start

### 1. Environment Configuration
```bash
cp .env.example .env
```

### 2. Run Database & Demo Data Seed
The app supports instant zero-config development using SQLite, or PostgreSQL via `DATABASE_URL`:
```bash
cd database
python -m seed
```
Default accounts seeded:
- Admin: `admin@cognix.local` / `AdminPass123!`
- Researcher: `researcher@cognix.local` / `ResearcherPass123!`

### 3. Launch Services
- **Start the Inference Microservice**:
  ```bash
  cd inference
  python -m uvicorn service:app --port 8001
  ```
- **Start the Main Web API**:
  ```bash
  cd ../backend
  python -m uvicorn api.main:app --port 8002
  ```
- **Start the Frontend**:
  ```bash
  cd ../frontend
  npm install
  npm run dev
  ```
Open `http://localhost:3000` to access the CV workbench.

---

## Running the Automated Test Suite

Execute all image preprocessing, classification determinism, detection scaling, Grad-CAM, similarity search, and privacy tests:
```bash
python -m pytest tests/ -v
```

---

## Responsible AI & Safety Disclosures

- **No Biometrics**: Cognix strictly prohibits facial recognition, biometric profiling, or human surveillance algorithms.
- **Model Probabilities**: Classification scores represent model softmax outputs and are not calibrated real-world probabilities. Scores below 0.20 are flagged as "Uncertain".
