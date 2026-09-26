"""Unit tests for AI Engine foundation and health endpoints."""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure ai-engine-adarsh is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.errors import ResourceNotFoundException

client = TestClient(app)


def test_root_endpoint():
    """Verify that the root endpoint returns project metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ARCANA-AI Brain"
    assert data["status"] == "operational"
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


def test_health_liveness_endpoint():
    """Verify that the /health endpoint reports healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ARCANA-AI Brain"
    assert "timestamp" in data


def test_health_readiness_endpoint():
    """Verify that the /health/ready endpoint reports readiness of components."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "components" in data
    assert data["components"]["schemas"] == "ready"


def test_api_v1_health():
    """Verify that /api/v1/health is routed correctly."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_structured_error_handling():
    """Verify that ArcanaException returns a structured error envelope matching Section 49."""
    # Temporarily mount a test route that raises ArcanaException
    @app.get("/test-error-endpoint")
    async def error_route():
        raise ResourceNotFoundException(resource_type="Document", resource_id="doc-xyz-123")

    response = client.get("/test-error-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "doc-xyz-123" in data["error"]["message"]
    assert "request_id" in data["error"]
