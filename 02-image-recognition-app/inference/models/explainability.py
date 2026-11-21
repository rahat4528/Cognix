import io
import base64
import time
from typing import Dict, Any, Optional
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import numpy as np
from PIL import Image
import cv2

from .classifier import MobileNetClassifier, IMAGENET_CATEGORIES


class GradCAMExplainer:
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping) implementation
    for MobileNetV3 visual explanation.
    Provides approximate visual explanations for neural network predictions.
    """
    def __init__(self, classifier: MobileNetClassifier):
        self.classifier = classifier
        self.device = classifier.device
        self.model = classifier.model
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        # Target the final convolutional block in MobileNetV3 features
        target_layer = self.model.features[-1]

        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def explain(
        self,
        image: Image.Image,
        target_class_id: Optional[int] = None,
        alpha: float = 0.5
    ) -> Dict[str, Any]:
        """
        Computes Grad-CAM heatmap and overlays it on the original image.
        Returns base64 encoded heatmap overlay and attribution details.
        """
        start_time = time.perf_counter()

        if image.mode != "RGB":
            image = image.convert("RGB")

        orig_w, orig_h = image.size
        input_tensor = self.classifier.preprocess(image).unsqueeze(0).to(self.device)
        input_tensor.requires_grad_(True)

        # Forward pass
        self.model.eval()
        features = self.model.features(input_tensor)
        pooled = self.model.avgpool(features)
        flattened = torch.flatten(pooled, 1)
        logits = self.model.classifier(flattened)
        probabilities = F.softmax(logits, dim=1).squeeze(0)

        # Determine target class
        if target_class_id is None:
            target_class_id = int(torch.argmax(probabilities).item())

        score = probabilities[target_class_id].item()
        target_label = IMAGENET_CATEGORIES[target_class_id] if target_class_id < len(IMAGENET_CATEGORIES) else f"Class_{target_class_id}"

        # Backward pass for the target class
        self.model.zero_grad()
        loss = logits[0, target_class_id]
        loss.backward()

        # Compute Grad-CAM weights: global average pooling of gradients
        gradients = self.gradients.detach()
        activations = self.activations.detach()

        pooled_gradients = torch.mean(gradients, dim=[2, 3], keepdim=True)
        cam = torch.sum(pooled_gradients * activations, dim=1).squeeze(0)
        cam = F.relu(cam)

        # Normalize CAM to [0, 1]
        cam_np = cam.cpu().numpy()
        cam_min, cam_max = cam_np.min(), cam_np.max()
        if cam_max - cam_min > 1e-7:
            cam_np = (cam_np - cam_min) / (cam_max - cam_min)
        else:
            cam_np = np.zeros_like(cam_np)

        # Resize heatmap to original image dimensions
        heatmap_resized = cv2.resize(cam_np, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
        heatmap_uint8 = np.uint8(255 * heatmap_resized)

        # Apply colormap (COLORMAP_JET)
        colormap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        colormap_rgb = cv2.cvtColor(colormap, cv2.COLOR_BGR2RGB)

        # Blend with original image
        orig_np = np.array(image)
        overlay = cv2.addWeighted(orig_np, 1 - alpha, colormap_rgb, alpha, 0)

        # Encode to JPEG base64
        overlay_pil = Image.fromarray(overlay)
        buffer = io.BytesIO()
        overlay_pil.save(buffer, format="JPEG", quality=85)
        base64_heatmap = base64.b64encode(buffer.getvalue()).decode("utf-8")

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "model_name": "MobileNetV3-Small-GradCAM",
            "target_class_id": target_class_id,
            "target_label": target_label,
            "confidence": round(float(score), 4),
            "heatmap_base64": f"data:image/jpeg;base64,{base64_heatmap}",
            "disclaimer": "approximate explanation: visual attribution highlights regions contributing most strongly to the classification score and should be interpreted as diagnostic assistance, not definitive causality.",
            "latency_ms": duration_ms
        }
