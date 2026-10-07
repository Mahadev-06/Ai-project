"""API endpoint integration tests."""
import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_check(async_client):
    response = await async_client.get("/api/v1/health/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "models" in data
    assert "corpus" in data


@pytest.mark.asyncio
async def test_create_and_fetch_analysis(async_client):
    # Submit analysis
    submit_payload = {
        "input_text": "Water boils at 100 degrees Celsius at sea level.",
        "evidence_mode": "local"
    }
    create_res = await async_client.post("/api/v1/analyses", json=submit_payload)
    assert create_res.status_code == 202
    created = create_res.json()
    assert "id" in created
    assert "access_token" in created
    job_id = created["id"]
    token = created["access_token"]

    # Retrieve without token should be 403
    unauth_res = await async_client.get(f"/api/v1/analyses/{job_id}")
    assert unauth_res.status_code == 403

    # Retrieve with token
    headers = {"Authorization": f"Bearer {token}"}
    auth_res = await async_client.get(f"/api/v1/analyses/{job_id}", headers=headers)
    assert auth_res.status_code == 200
    job_data = auth_res.json()
    assert job_data["id"] == job_id
    assert job_data["status"] in ["queued", "running", "completed"]


@pytest.mark.asyncio
async def test_reject_unsupported_language(async_client):
    payload = {
        "input_text": "El agua hierve a cien grados Celsius al nivel del mar y la tierra gira alrededor del sol.",
        "evidence_mode": "local"
    }
    res = await async_client.post("/api/v1/analyses", json=payload)
    assert res.status_code == 400
    assert "English only" in res.json()["detail"]


@pytest.mark.asyncio
async def test_reject_empty_input(async_client):
    payload = {
        "input_text": "   ",
        "evidence_mode": "local"
    }
    res = await async_client.post("/api/v1/analyses", json=payload)
    assert res.status_code == 400
