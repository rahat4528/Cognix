import io
import pytest
from httpx import AsyncClient, ASGITransport
from PIL import Image

from backend.api.main import app


@pytest.mark.asyncio
async def test_api_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cognix-cv-backend"


@pytest.mark.asyncio
async def test_api_models_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/models/")
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) >= 2
        model_ids = [m["id"] for m in data["models"]]
        assert "mobilenet_v3_small" in model_ids
        assert "ssdlite320_mobilenet_v3_large" in model_ids


@pytest.mark.asyncio
async def test_image_upload_and_classify():
    # Create test JPEG
    img = Image.new("RGB", (224, 224), color=(30, 80, 160))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Upload
        files = {"file": ("api_test.jpg", buf, "image/jpeg")}
        upload_resp = await client.post("/api/v1/images/upload", files=files)
        assert upload_resp.status_code == 200
        asset_data = upload_resp.json()
        assert "id" in asset_data
        image_id = asset_data["id"]

        # Classify
        cls_resp = await client.post(f"/api/v1/inference/classify/{image_id}?top_k=3")
        assert cls_resp.status_code == 200
        cls_data = cls_resp.json()
        assert cls_data["image_id"] == image_id
        assert "top_label" in cls_data
        assert len(cls_data["predictions"]) == 3
        assert "embedding" in cls_data
        assert len(cls_data["embedding"]) == 576

        # Detect
        det_resp = await client.post(f"/api/v1/inference/detect/{image_id}?score_threshold=0.20")
        assert det_resp.status_code == 200
        det_data = det_resp.json()
        assert det_data["image_id"] == image_id
        assert "total_objects" in det_data
        assert "detections" in det_data

        # Explainability
        exp_resp = await client.post(f"/api/v1/inference/explain/{image_id}")
        assert exp_resp.status_code == 200
        exp_data = exp_resp.json()
        assert "heatmap_data_url" in exp_data
        assert "approximate explanation" in exp_data["disclaimer"]

        # Delete
        del_resp = await client.delete(f"/api/v1/images/{image_id}")
        assert del_resp.status_code == 200
