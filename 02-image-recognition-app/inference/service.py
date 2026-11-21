import os
import io
import time
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Query, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from .models.classifier import MobileNetClassifier, IMAGENET_CATEGORIES
from .models.detector import SSDLiteDetector, COCO_CATEGORIES
from .models.explainability import GradCAMExplainer

INTERNAL_SERVICE_KEY = os.getenv("INTERNAL_SERVICE_KEY", "cognix-cv-internal-key-secure-2026")

app = FastAPI(
    title="Cognix Computer Vision Inference Service",
    description="Dedicated microservice for real-time deep learning image classification, object detection, and visual explainability.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model singletons (lazy or startup initialized)
classifier: Optional[MobileNetClassifier] = None
detector: Optional[SSDLiteDetector] = None
explainer: Optional[GradCAMExplainer] = None

def get_classifier() -> MobileNetClassifier:
    global classifier
    if classifier is None:
        classifier = MobileNetClassifier()
    return classifier

def get_detector() -> SSDLiteDetector:
    global detector
    if detector is None:
        detector = SSDLiteDetector()
    return detector

def get_explainer() -> GradCAMExplainer:
    global explainer
    if explainer is None:
        explainer = GradCAMExplainer(get_classifier())
    return explainer

def verify_internal_auth(x_internal_service_key: Optional[str] = Header(None)):
    if INTERNAL_SERVICE_KEY and x_internal_service_key != INTERNAL_SERVICE_KEY:
        # Allow open access if key is empty or matches
        if INTERNAL_SERVICE_KEY != "":
            raise HTTPException(status_code=401, detail="Unauthorized: invalid internal service key")
    return True

@app.on_event("startup")
async def startup_event():
    # Warm up models on startup
    get_classifier()
    get_detector()
    get_explainer()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cognix-cv-inference",
        "version": "1.0.0",
        "device": "cpu",
        "models_loaded": {
            "classifier": classifier is not None,
            "detector": detector is not None,
            "explainer": explainer is not None
        }
    }

@app.get("/models")
def list_models():
    return {
        "models": [
            {
                "id": "mobilenet_v3_small",
                "name": "MobileNetV3-Small",
                "task": "classification",
                "weights": "MobileNet_V3_Small_Weights.DEFAULT",
                "num_classes": len(IMAGENET_CATEGORIES),
                "embedding_dimension": 576,
                "input_resolution": "224x224",
                "supported_formats": ["JPEG", "PNG", "WEBP"]
            },
            {
                "id": "ssdlite320_mobilenet_v3_large",
                "name": "SSDLite320-MobileNetV3-Large",
                "task": "object_detection",
                "weights": "SSDLite320_MobileNet_V3_Large_Weights.DEFAULT",
                "num_classes": len(COCO_CATEGORIES),
                "input_resolution": "320x320",
                "supported_formats": ["JPEG", "PNG", "WEBP"]
            },
            {
                "id": "grad_cam_explainer",
                "name": "MobileNetV3-GradCAM",
                "task": "explainability",
                "target_layer": "features[-1]",
                "disclaimer": "approximate explanation"
            }
        ]
    }

def read_image_from_bytes(file_bytes: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.load()
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Corrupt or invalid image data: {str(e)}")

@app.post("/classify")
async def classify_image(
    file: UploadFile = File(...),
    top_k: int = Query(5, ge=1, le=20),
    uncertainty_threshold: float = Query(0.20, ge=0.0, le=1.0),
    _auth: bool = Depends(verify_internal_auth)
):
    contents = await file.read()
    image = read_image_from_bytes(contents)
    cls_engine = get_classifier()
    result = cls_engine.predict(image, top_k=top_k, uncertainty_threshold=uncertainty_threshold)
    return result

@app.post("/detect")
async def detect_objects(
    file: UploadFile = File(...),
    score_threshold: float = Query(0.30, ge=0.05, le=0.99),
    nms_threshold: float = Query(0.45, ge=0.05, le=0.99),
    _auth: bool = Depends(verify_internal_auth)
):
    contents = await file.read()
    image = read_image_from_bytes(contents)
    det_engine = get_detector()
    result = det_engine.detect(image, score_threshold=score_threshold, nms_threshold=nms_threshold)
    return result

@app.post("/explain")
async def explain_classification(
    file: UploadFile = File(...),
    target_class_id: Optional[int] = Query(None, ge=0, le=1000),
    alpha: float = Query(0.5, ge=0.1, le=0.9),
    _auth: bool = Depends(verify_internal_auth)
):
    contents = await file.read()
    image = read_image_from_bytes(contents)
    cam_engine = get_explainer()
    result = cam_engine.explain(image, target_class_id=target_class_id, alpha=alpha)
    return result

@app.post("/live-frame")
async def live_frame_inference(
    file: UploadFile = File(...),
    score_threshold: float = Query(0.35, ge=0.1, le=0.95),
    _auth: bool = Depends(verify_internal_auth)
):
    """
    Lightweight endpoint for throttled real-time camera frames.
    Returns detected objects and bounding boxes with minimal latency overhead.
    """
    t0 = time.perf_counter()
    contents = await file.read()
    image = read_image_from_bytes(contents)
    det_engine = get_detector()
    res = det_engine.detect(image, score_threshold=score_threshold)
    total_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "detected_objects": res["detected_objects"],
        "total_objects_count": res["total_objects_count"],
        "class_counts": res["class_counts"],
        "inference_latency_ms": res["latency_ms"],
        "round_trip_ms": total_ms
    }
