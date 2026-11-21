# Model Card: SSDLite with MobileNetV3-Large (Object Detection)

## Model Details
- **Model Name**: SSDLite320-MobileNetV3-Large
- **Model Version**: 1.0.0
- **Architecture**: Single Shot MultiBox Detector with lightweight depthwise separable convolutions (SSDLite).
- **Source**: PyTorch / Torchvision model registry
- **License**: BSD 3-Clause License (Permissive open source)
- **Primary Task**: Multi-object detection with bounding box coordinates and class categorization across 80 common object classes.

## Training Data & Lineage
- **Dataset**: COCO (Common Objects in Context)
- **License of Dataset**: Creative Commons Attribution 4.0
- **Preprocessing Pipeline**:
  - Image scaling to 320 x 320 pixels
  - Mean subtraction and normalization

## Evaluation Metrics (Benchmark)
- **mAP (0.5:0.95)**: 21.3%
- **mAP (0.50)**: 34.3%
- **Inference Latency (CPU)**: 30 - 65 ms per frame
- **NMS Threshold**: 0.45 default
- **Confidence Cutoff**: 0.30 default

## Limitations
- Bounding box accuracy degrades for heavily occluded or sub-pixel miniature objects.
- Real-time video processing requires throttling (max 5 FPS on CPU) to maintain interactive responsiveness without memory buffering.
