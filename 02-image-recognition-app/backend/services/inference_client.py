import os
import io
from typing import Dict, Any, Optional
import httpx
from PIL import Image
from ..core.config import settings

# Attempt in-process fallback if separate microservice is unreachable
_in_process_classifier = None
_in_process_detector = None
_in_process_explainer = None


def _get_in_process_models():
    global _in_process_classifier, _in_process_detector, _in_process_explainer
    if _in_process_classifier is None:
        import sys
        # Add parent directory to sys.path to locate inference package
        app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if app_root not in sys.path:
            sys.path.insert(0, app_root)
        from inference.models.classifier import MobileNetClassifier
        from inference.models.detector import SSDLiteDetector
        from inference.models.explainability import GradCAMExplainer

        _in_process_classifier = MobileNetClassifier()
        _in_process_detector = SSDLiteDetector()
        _in_process_explainer = GradCAMExplainer(_in_process_classifier)
    return _in_process_classifier, _in_process_detector, _in_process_explainer


class InferenceClient:
    def __init__(self):
        self.base_url = settings.INFERENCE_SERVICE_URL
        self.headers = {"X-Internal-Service-Key": settings.INTERNAL_SERVICE_KEY}

    async def classify_image(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
        top_k: int = 5,
        uncertainty_threshold: float = 0.20
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (filename, image_bytes, "image/jpeg")}
                params = {"top_k": top_k, "uncertainty_threshold": uncertainty_threshold}
                resp = await client.post(
                    f"{self.base_url}/classify",
                    headers=self.headers,
                    files=files,
                    params=params
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass  # Fallback to direct in-process inference

        cls_engine, _, _ = _get_in_process_models()
        pil_img = Image.open(io.BytesIO(image_bytes))
        return cls_engine.predict(pil_img, top_k=top_k, uncertainty_threshold=uncertainty_threshold)

    async def detect_objects(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
        score_threshold: float = 0.30,
        nms_threshold: float = 0.45
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (filename, image_bytes, "image/jpeg")}
                params = {"score_threshold": score_threshold, "nms_threshold": nms_threshold}
                resp = await client.post(
                    f"{self.base_url}/detect",
                    headers=self.headers,
                    files=files,
                    params=params
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass  # Fallback to direct in-process inference

        _, det_engine, _ = _get_in_process_models()
        pil_img = Image.open(io.BytesIO(image_bytes))
        return det_engine.detect(pil_img, score_threshold=score_threshold, nms_threshold=nms_threshold)

    async def explain_classification(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
        target_class_id: Optional[int] = None,
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (filename, image_bytes, "image/jpeg")}
                params = {"alpha": alpha}
                if target_class_id is not None:
                    params["target_class_id"] = target_class_id
                resp = await client.post(
                    f"{self.base_url}/explain",
                    headers=self.headers,
                    files=files,
                    params=params
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass  # Fallback to direct in-process inference

        _, _, cam_engine = _get_in_process_models()
        pil_img = Image.open(io.BytesIO(image_bytes))
        return cam_engine.explain(pil_img, target_class_id=target_class_id, alpha=alpha)

    async def live_frame(self, image_bytes: bytes, score_threshold: float = 0.35) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}
                params = {"score_threshold": score_threshold}
                resp = await client.post(
                    f"{self.base_url}/live-frame",
                    headers=self.headers,
                    files=files,
                    params=params
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass

        _, det_engine, _ = _get_in_process_models()
        import time
        t0 = time.perf_counter()
        pil_img = Image.open(io.BytesIO(image_bytes))
        res = det_engine.detect(pil_img, score_threshold=score_threshold)
        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        return {
            "detected_objects": res["detected_objects"],
            "total_objects_count": res["total_objects_count"],
            "class_counts": res["class_counts"],
            "inference_latency_ms": res["latency_ms"],
            "round_trip_ms": total_ms
        }


inference_client = InferenceClient()
