# Architecture: Image Recognition App

## System Topology & Microservice Isolation

```text
+-----------------------------------------------------------------------------------------+
|                                  Next.js Frontend                                       |
|  Upload Workspace | Classification Viewer | Canvas Detection | Live Camera | Fine-Tuning |
+-----------------------------------------------------------------------------------------+
                                              |  HTTPS / WebSocket
                                              v
+-----------------------------------------------------------------------------------------+
|                                 FastAPI Main Web API                                    |
|   Auth & Security | Upload Sanitizer | Metadata DB | Storage Broker | Job Dispatcher    |
+-----------------------------------------------------------------------------------------+
         |                       |                                    |
         v                       v                                    v
+------------------+    +-------------------+               +-----------------------------+
|    PostgreSQL    |    |   Redis Broker    |               |  Isolated Inference Service |
| (Metadata, Vector|    |  (Task Queues &   |<=============>| (PyTorch Engine, MobileNet, |
|   Embeddings)    |    |  Stream Buffers)  |               |  SSDLite, Zero DB Access)   |
+------------------+    +-------------------+               +-----------------------------+
         |
         v
+------------------+
|  Object Storage  |
| (Sanitized Assets|
|  & Thumbnails)   |
+------------------+
```

---

## Security & Isolation Boundaries

1. **Separation of Concerns**: The inference engine operates as an independent service in `inference/`. It does not possess database credentials or direct end-user tokens; it receives sanitized image byte buffers, executes neural network forward passes, and returns structured prediction dictionaries.
2. **Safe Model Serialization**: All model weights are loaded strictly with PyTorch `weights_only=True` or via safe TorchScript/safetensors formats. Checksums are verified before loading.
3. **EXIF Stripping**: Original uploaded images are re-encoded via Pillow, stripping sensitive EXIF metadata (GPS location coordinates, camera serial numbers, device telemetry).
4. **Isolated Similarity Search**: Vector embeddings for similarity search are queried strictly within the authenticated user's image assets (`WHERE user_id = :current_user_id`).
