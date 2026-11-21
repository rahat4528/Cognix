import io
import time
from typing import List, Dict, Any, Tuple
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.models import MobileNet_V3_Small_Weights
from PIL import Image
import numpy as np

# Load standard ImageNet category labels
IMAGENET_CATEGORIES = MobileNet_V3_Small_Weights.DEFAULT.meta["categories"]

class MobileNetClassifier:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        # Load MobileNetV3-Small with default pretrained weights safely
        self.weights = MobileNet_V3_Small_Weights.DEFAULT
        self.model = models.mobilenet_v3_small(weights=self.weights)
        self.model.to(self.device)
        self.model.eval()

        # Build standard inference transform pipeline
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def predict(
        self,
        image: Image.Image,
        top_k: int = 5,
        uncertainty_threshold: float = 0.20
    ) -> Dict[str, Any]:
        """
        Executes genuine classification inference.
        Returns top-k categories, softmax probabilities, and embedding vector.
        """
        start_time = time.perf_counter()
        
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            # Forward pass through feature extractor
            features = self.model.features(input_tensor)
            pooled = self.model.avgpool(features)
            flattened = torch.flatten(pooled, 1)
            
            # Extract normalized visual embedding
            norm_embedding = torch.nn.functional.normalize(flattened, p=2, dim=1)
            embedding_list = norm_embedding.squeeze(0).cpu().numpy().tolist()

            # Forward pass through classification head
            logits = self.model.classifier(flattened)
            probabilities = torch.nn.functional.softmax(logits, dim=1).squeeze(0)

        # Get top-k predictions
        top_scores, top_indices = torch.topk(probabilities, k=min(top_k, len(IMAGENET_CATEGORIES)))
        
        predictions = []
        for score, idx in zip(top_scores.cpu().numpy(), top_indices.cpu().numpy()):
            predictions.append({
                "class_id": int(idx),
                "label": IMAGENET_CATEGORIES[int(idx)],
                "score": round(float(score), 4)
            })

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        top_score = predictions[0]["score"] if predictions else 0.0
        is_uncertain = top_score < uncertainty_threshold

        return {
            "model_name": "MobileNetV3-Small",
            "model_version": "1.0.0",
            "top_predictions": predictions,
            "top_label": predictions[0]["label"] if predictions else "Unknown",
            "top_score": top_score,
            "is_uncertain": is_uncertain,
            "embedding": embedding_list,
            "latency_ms": duration_ms
        }
