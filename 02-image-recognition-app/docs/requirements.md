# Requirements Specification: Image Recognition App

## 1. Executive Summary
The **Image Recognition App** is a production-quality computer vision workbench and model serving system. It provides high-throughput image classification, multi-object detection with interactive HTML5 Canvas bounding box inspection and per-class toggles, live camera feed processing with latency metrics and frame throttling, image similarity search, and custom dataset management with transfer learning.

In accordance with scientific and responsible AI standards:
- All predictions, scores, and bounding boxes are computed directly from genuine machine-learning models (PyTorch/Torchvision).
- Zero mocked inference, zero synthetic outputs disguised as model predictions.
- No biometric identification, facial recognition, or unauthorized surveillance features.

---

## 2. Functional Requirements

### 2.1 User Management & Privacy
- **Account Management**: Registration, JWT authentication, user profile management.
- **Tenant & Asset Isolation**: Users access exclusively their own uploaded assets, inference history, and custom datasets.
- **Asset Purge & Cascading Deletion**: Deleting history permanently removes original images, generated thumbnails, vector embeddings, and database analysis records.

### 2.2 Upload & Image Sanitization
- **Supported Formats**: JPEG, JPG, PNG, WebP.
- **Upload Types**: Single and multiple batch file uploads.
- **Sanitization & Decompression Bomb Defense**:
  - Image decoding verification via Pillow (`Image.open`, `verify`).
  - Strict pixel-count limit (max 25 megapixels) to prevent memory exhaustion and zip/decompression bombs.
  - Automatic EXIF orientation normalization followed by metadata stripping (eliminating GPS and device telemetry leaks).
  - High-quality thumbnail generation (e.g. 256x256) for rapid gallery browsing.

### 2.3 Image Classification
- **Model Architecture**: Permissively licensed MobileNetV3 / ResNet backbone.
- **Inference Pipeline**: Deterministic RGB conversion, resize, center-crop, normalization via standard ImageNet statistics.
- **Outputs**: Top-k categories with calibrated softmax scores, latency telemetry, model version metadata, and low-confidence "uncertain" state trigger below threshold (default 0.20).
- **Explainability**: Integrated Grad-CAM heatmaps labeled "approximate explanation" indicating salient image regions.

### 2.4 Object Detection
- **Model Architecture**: SSDLite / Faster R-CNN with MobileNet backbone.
- **Outputs**:
  - Bounding boxes returned in original image pixel coordinates `[x1, y1, x2, y2]` and normalized `[0, 1]` ranges.
  - Confidence scores, class labels, and per-class object counts.
  - Configurable Non-Maximum Suppression (NMS) and confidence score thresholds.
- **Export Formats**: Downloadable detection results in JSON, CSV, and standard COCO format.
- **UI Inspection**: Interactive Canvas overlay with per-class visibility toggles, box hover tooltips, and zoom.

### 2.5 Live Camera Recognition
- **Permission & Safety**: Activated only upon explicit user consent and click; displays a persistent, unmistakable visual "Camera Active" indicator.
- **Frame Throttling & Latency**: Frames captured from WebRTC video feed at a throttled rate (max 5 FPS), processed in memory with single-in-flight queue and drop-late policy.
- **Zero Default Retention**: Live camera frames are never stored or persisted unless the user explicitly clicks "Save Snapshot".
- **Auto-Stop**: Stream automatically disconnects when navigating away or switching tabs.

### 2.6 Vector Similarity Search
- **Feature Extraction**: 1000-dimensional or 512-dimensional penultimate layer embeddings extracted from the vision backbone.
- **Search**: Fast nearest-neighbor cosine similarity search restricted strictly to the user's private library of images.

### 2.7 Datasets & Fine-Tuning
- **Dataset Ingestion**: Support for folder-per-class archives and simple bounding box annotations.
- **Leakage Prevention**: Stratified splitting (Train / Val / Test) with fixed seeds and perceptual hashing (pHash) to detect duplicate/near-duplicate images across splits.
- **Fine-Tuning**: Head transfer learning pipeline logging training loss, validation accuracy, and saving weights with SHA-256 checksums.

---

## 3. Service Architecture
- **Web API**: FastAPI handling authentication, upload validation, asset storage, and job dispatching.
- **Isolated Inference Microservice**: A standalone package (`inference/`) running the PyTorch vision models with zero database credentials and no external network access, communicating via internal authenticated requests.
