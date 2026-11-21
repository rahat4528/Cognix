# Model Card: MobileNetV3-Small (Vision Classification & Feature Extraction)

## Model Details
- **Model Name**: MobileNetV3-Small
- **Model Version**: 1.0.0
- **Model Architecture**: Convolutional Neural Network with squeeze-and-excitation blocks and hard-swish non-linearities.
- **Source**: PyTorch / Torchvision model registry
- **License**: BSD 3-Clause License (Permissive open source)
- **Primary Tasks**: Image Classification (1,000 classes) and visual embedding feature extraction (576-dimensional penultimate vectors).

## Training Data & Lineage
- **Dataset**: ImageNet (ILSVRC 2012)
- **License of Dataset**: Academic / Research Open Access
- **Preprocessing Pipeline**:
  - Input resolution: 224 x 224 pixels
  - Normalization: Mean `[0.485, 0.456, 0.406]`, Std `[0.229, 0.224, 0.225]`
  - Interpolation: Bilinear with center cropping

## Evaluation Metrics (Benchmark)
- **Top-1 Accuracy**: 67.7%
- **Top-5 Accuracy**: 87.4%
- **Inference Latency (CPU)**: 12 - 25 ms per single 224x224 image
- **Parameter Count**: ~2.5 Million parameters

## Limitations & Biases
- Pretrained weights were trained on ImageNet and may perform sub-optimally on specialized domains (e.g. medical microscopy, specialized satellite imagery) without fine-tuning.
- Outputs represent softmax model probabilities and must not be treated as absolute facts.
- Scores below 0.20 are flagged as "Uncertain" in the Cognix workbench UI.
- Not permitted for biometric human identification or surveillance.
