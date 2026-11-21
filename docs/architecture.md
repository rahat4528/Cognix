# Repository Architecture

## Architectural Isolation

Cognix adheres to strict application separation. Each project functions as an autonomous system:

```text
+----------------------------------------------------------------------------+
|                                Cognix                                      |
+----------------------------------------------------------------------------+
|                                                                            |
|  [01-data-visualization-dashboard]                                         |
|  Next.js Frontend <--> FastAPI Backend <--> DuckDB / PostgreSQL / Redis   |
|                                                                            |
|  [02-image-recognition-app]                                                |
|  Next.js Frontend <--> FastAPI Main API <--> Inference Service <--> pgvector|
|                                                                            |
|  [03-recommendation-system]                                                |
|  Next.js Frontend <--> FastAPI Gateway <--> Training & Serving Engines     |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Principles:
1. **No Shared Run-time Dependencies**: Applications do not share database schemas, internal RPCs, or in-memory state.
2. **Dedicated Data Stores**:
   - `cognix_dataviz_db` for Data Visualization Dashboard
   - `cognix_image_recognition_db` for Image Recognition App
   - `cognix_recommendation_db` for Recommendation System
3. **Reproducible Storage**: File uploads and model weights are managed securely using object storage and deterministic directory layouts.
4. **Security by Default**: Authentication is token-based with Argon2/Bcrypt password hashing, parameterized database queries, sandboxed execution engines, and role-based access control.
