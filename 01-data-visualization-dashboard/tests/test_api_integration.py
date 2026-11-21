import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from api.main import app
from core.database import init_db

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_auth_and_workspaces_flow():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login with seeded admin
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@cognix.local",
            "password": "AdminPass123!"
        })
        assert login_resp.status_code == 200
        tokens = login_resp.json()
        access_token = tokens["access_token"]
        assert access_token is not None

        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. List workspaces
        ws_resp = await client.get("/api/v1/workspaces", headers=headers)
        assert ws_resp.status_code == 200
        workspaces = ws_resp.json()
        assert len(workspaces) > 0
        ws_id = workspaces[0]["id"]

        # 3. List datasets
        ds_resp = await client.get(f"/api/v1/workspaces/{ws_id}/datasets", headers=headers)
        assert ds_resp.status_code == 200
        datasets = ds_resp.json()
        assert len(datasets) > 0

        # 4. List charts
        ch_resp = await client.get(f"/api/v1/workspaces/{ws_id}/charts", headers=headers)
        assert ch_resp.status_code == 200

        # 5. List dashboards
        dash_resp = await client.get(f"/api/v1/workspaces/{ws_id}/dashboards", headers=headers)
        assert dash_resp.status_code == 200
        dashboards = dash_resp.json()
        assert len(dashboards) > 0

        # 6. Test Optimistic Concurrency Control on dashboard update
        dash = dashboards[0]
        # Valid update with matching version
        update_resp = await client.put(f"/api/v1/dashboards/{dash['id']}", headers=headers, json={
            "title": "Updated Dashboard Title",
            "version": dash["version"]
        })
        assert update_resp.status_code == 200
        updated_dash = update_resp.json()
        assert updated_dash["version"] == dash["version"] + 1

        # Stale update attempt with outdated version must return 409 Conflict
        stale_resp = await client.put(f"/api/v1/dashboards/{dash['id']}", headers=headers, json={
            "title": "Conflicting Update",
            "version": dash["version"]  # Old version
        })
        assert stale_resp.status_code == 409
