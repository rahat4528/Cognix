# Machine Learning Engineering Guide

## Scientific Integrity and AI Standards

Cognix enforces strict quality and integrity benchmarks across all machine learning components:

### 1. Genuine Computation
- All metrics, evaluation curves, predictions, and recommendations are computed directly from real mathematical models and data inputs.
- No synthetic or mocked outputs are disguised as genuine inference.

### 2. Model Cards & Documentation
Every model deployed within Cognix includes a dedicated model card detailing:
- Model architecture and version
- Intended usage and known limitations
- Training and evaluation configurations
- Verified benchmark results and hardware footprints

### 3. Data Lineage and Leakage Prevention
- Ingestion pipelines enforce schema validation and immutability.
- Training and evaluation splits are strictly partitioned by time or stratified random assignments with pinned seeds.
- Preprocessing transformers and scalers are fitted exclusively on training sets.

### 4. Safe Artifact Management
- Model artifacts and weights use secure serialization formats (safetensors, ONNX, TorchScript, or npz).
- Checksums (SHA-256) are validated upon artifact loading to ensure tamper-proof pipelines.
