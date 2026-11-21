# REST API Specification: Image Recognition App

All endpoints return standard JSON responses and require Bearer token authentication unless otherwise noted.

## 1. Authentication & Users
- `POST /api/v1/auth/register` — Register a new user account.
- `POST /api/v1/auth/login` — Authenticate and receive JWT access and refresh tokens.
- `GET /api/v1/auth/me` — Retrieve authenticated user profile and quota details.

## 2. Image Management & Sanitization
- `POST /api/v1/images/upload` — Upload single or multiple images (multipart/form-data). Validates formats, strips EXIF, generates thumbnails.
- `GET /api/v1/images` — List uploaded image assets for the current user (paginated).
- `GET /api/v1/images/{id}` — Get image metadata and pre-signed/local access URLs.
- `DELETE /api/v1/images/{id}` — Permanently delete an image, thumbnail, embeddings, and analyses.

## 3. Computer Vision Inference
- `POST /api/v1/inference/classify` — Run image classification on an uploaded asset or raw byte buffer. Returns top-k categories, softmax confidence scores, and latency.
- `POST /api/v1/inference/detect` — Run object detection. Returns bounding boxes (pixel and normalized coordinates), class labels, and per-class counts.
- `POST /api/v1/inference/explain` — Compute Grad-CAM saliency overlay for a classification prediction.
- `POST /api/v1/inference/live-frame` — Lightweight throttled endpoint for live webcam frame recognition. Returns detected objects and round-trip latency.

## 4. History & Analysis Records
- `GET /api/v1/analyses` — List historical inference jobs and results for the current user.
- `GET /api/v1/analyses/{id}` — Retrieve complete analysis payload including bounding boxes and scores.
- `DELETE /api/v1/analyses/{id}` — Remove an analysis record.
- `POST /api/v1/images/similarity-search` — Perform vector similarity search against the user's uploaded library.

## 5. Model Management & Evaluation
- `GET /api/v1/models` — List registered vision models, status (loaded/unloaded), latency benchmarks, and licenses.
- `GET /api/v1/models/{id}/metrics` — Retrieve evaluation metrics (Top-1, Top-5 accuracy, mAP).
- `POST /api/v1/models/train` — Trigger head fine-tuning job on a custom uploaded dataset.
