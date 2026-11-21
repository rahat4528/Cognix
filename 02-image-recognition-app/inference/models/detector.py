import time
from typing import List, Dict, Any, Tuple
import torch
import torchvision.models.detection as detection
from torchvision.models.detection import SSDLite320_MobileNet_V3_Large_Weights
from torchvision.transforms import functional as F
from PIL import Image
import numpy as np

# Standard COCO 80 categories mapping
COCO_CATEGORIES = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT.meta["categories"]

class SSDLiteDetector:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.weights = SSDLite320_MobileNet_V3_Large_Weights.DEFAULT
        self.model = detection.ssdlite320_mobilenet_v3_large(weights=self.weights)
        self.model.to(self.device)
        self.model.eval()

    def detect(
        self,
        image: Image.Image,
        score_threshold: float = 0.30,
        nms_threshold: float = 0.45
    ) -> Dict[str, Any]:
        """
        Executes genuine object detection using SSDLite on an image.
        Returns bounding boxes in both absolute pixel and normalized [0, 1] coordinates.
        """
        start_time = time.perf_counter()
        orig_w, orig_h = image.size

        # Preprocess
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        tensor_img = F.to_tensor(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor_img)[0]

        boxes = outputs["boxes"].cpu().numpy()
        scores = outputs["scores"].cpu().numpy()
        labels = outputs["labels"].cpu().numpy()

        detected_objects: List[Dict[str, Any]] = []
        class_counts: Dict[str, int] = {}

        for box, score, label_id in zip(boxes, scores, labels):
            if score < score_threshold:
                continue

            x1, y1, x2, y2 = box
            # Clip coordinates to original image bounds
            x1 = max(0.0, min(float(x1), float(orig_w)))
            y1 = max(0.0, min(float(y1), float(orig_h)))
            x2 = max(0.0, min(float(x2), float(orig_w)))
            y2 = max(0.0, min(float(y2), float(orig_h)))

            # Normalized coordinates [0.0 - 1.0]
            norm_x1 = round(x1 / orig_w, 4) if orig_w > 0 else 0.0
            norm_y1 = round(y1 / orig_h, 4) if orig_h > 0 else 0.0
            norm_x2 = round(x2 / orig_w, 4) if orig_w > 0 else 0.0
            norm_y2 = round(y2 / orig_h, 4) if orig_h > 0 else 0.0

            class_name = COCO_CATEGORIES[int(label_id)] if int(label_id) < len(COCO_CATEGORIES) else f"Class_{label_id}"

            detected_objects.append({
                "label": class_name,
                "class_id": int(label_id),
                "score": round(float(score), 4),
                "bbox_pixels": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "bbox_normalized": [norm_x1, norm_y1, norm_x2, norm_y2],
                "width": round(x2 - x1, 1),
                "height": round(y2 - y1, 1)
            })

            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "model_name": "SSDLite320-MobileNetV3-Large",
            "model_version": "1.0.0",
            "image_width": orig_w,
            "image_height": orig_h,
            "detected_objects": detected_objects,
            "total_objects_count": len(detected_objects),
            "class_counts": class_counts,
            "latency_ms": duration_ms
        }
