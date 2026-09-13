"""Test suite for ARCANA AI Brain foundation endpoints."""

import pytest


@pytest.mark.anyio
async def test_root_endpoint(async_client):
    """Test that root endpoint returns specified project identity."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "project": "ARCANA AI Engine",
        "status": "online",
        "version": "0.1.0",
    }


@pytest.mark.anyio
async def test_health_check_endpoint(async_client):
    """Test that health check endpoint returns 200 and healthy status."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "ARCANA AI Engine"
    assert data["version"] == "0.1.0"
    assert "environment" in data


@pytest.mark.anyio
async def test_cors_preflight(async_client):
    """Test CORS headers on preflight OPTIONS request."""
    response = await async_client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
