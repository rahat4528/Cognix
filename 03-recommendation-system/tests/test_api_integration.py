import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app


@pytest.mark.asyncio
async def test_api_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cognix-recommendation-backend"


@pytest.mark.asyncio
async def test_api_catalog_and_categories():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/items/")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0

        cat_resp = await client.get("/api/v1/items/categories")
        assert cat_resp.status_code == 200
        categories = cat_resp.json()
        assert "Audio" in categories or "Computing" in categories


@pytest.mark.asyncio
async def test_api_recommendations_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Personalized hybrid recs
        rec_resp = await client.get("/api/v1/recommendations/personalized?top_k=5")
        assert rec_resp.status_code == 200
        recs = rec_resp.json()
        assert len(recs) > 0
        assert "item" in recs[0]
        assert "score" in recs[0]

        # Cold start quiz submission
        quiz_resp = await client.post("/api/v1/recommendations/onboard-quiz", json={
            "selected_categories": ["Audio", "Photography"],
            "price_tier": "premium",
            "tech_affinity": "high"
        })
        assert quiz_resp.status_code == 200
        assert quiz_resp.json()["status"] == "success"

        # A/B experiments summary
        ab_resp = await client.get("/api/v1/experiments/")
        assert ab_resp.status_code == 200
        assert "variants" in ab_resp.json()

        # Offline benchmarks
        bench_resp = await client.get("/api/v1/evaluation/benchmarks")
        assert bench_resp.status_code == 200
        assert "benchmarks" in bench_resp.json()
