# Dataset Card: Demo Computer Vision Benchmark

## Dataset Details
- **Dataset Name**: Demo Computer Vision Benchmark
- **Dataset Version**: 1.0.0
- **Purpose**: Local integration testing, calibration, and zero-network verification of classification and object detection pipelines.
- **License**: Public Domain / CC0
- **Format**: PNG test image fixtures with hand-annotated ground truth bounding boxes and class labels.

## Data Splits
- **Total Test Images**: 10 fixture images (synthetic geometric compositions, office objects, vehicles, and everyday items).
- **Split Strategy**: Stratified test holdout.
- **Leakage Prevention**: Perceptual hashing (pHash) verified ensuring zero perceptual overlap between training demo split and test holdout.
- **Annotations**: Bounding boxes formatted in both normalized `[ymin, xmin, ymax, xmax]` and pixel coordinates.
