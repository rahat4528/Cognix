from fastapi import APIRouter
from ...services.inference_client import inference_client

router = APIRouter(prefix="/models", tags=["Model Registry"])


@router.get("/")
async def list_models():
    """
    Returns registered computer vision model architectures, capabilities, and parameters.
    """
    return {
        "models": [
            {
                "id": "mobilenet_v3_small",
                "name": "MobileNetV3-Small",
                "task": "Image Classification & Embeddings",
                "framework": "PyTorch / torchvision",
                "parameters_millions": 2.54,
                "embedding_dimension": 576,
                "input_resolution": "224x224",
                "supported_formats": ["JPEG", "PNG", "WEBP"],
                "license": "BSD-3-Clause",
                "purpose": "Efficient edge-optimized visual feature extraction and 1,000-class classification."
            },
            {
                "id": "ssdlite320_mobilenet_v3_large",
                "name": "SSDLite320-MobileNetV3-Large",
                "task": "Object Detection & Localization",
                "framework": "PyTorch / torchvision",
                "parameters_millions": 3.44,
                "input_resolution": "320x320",
                "num_classes": 80,
                "dataset": "MS COCO 2017",
                "license": "BSD-3-Clause",
                "purpose": "Real-time single-shot multi-box localization with bounding box coordinates."
            },
            {
                "id": "mobilenet_v3_gradcam",
                "name": "MobileNetV3-Small-GradCAM",
                "task": "Visual Explainability",
                "framework": "PyTorch",
                "target_layer": "features[-1]",
                "disclaimer": "approximate explanation",
                "purpose": "Gradient-weighted Class Activation Mapping highlighting diagnostic saliency regions."
            }
        ]
    }
