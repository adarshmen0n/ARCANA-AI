"""Pytest configuration and shared fixtures for ARCANA AI Brain test suite."""

import os
import sys
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

# Ensure ai-engine root directory is in sys.path
ai_engine_root = Path(__file__).resolve().parent.parent
if str(ai_engine_root) not in sys.path:
    sys.path.insert(0, str(ai_engine_root))

from app.main import app


@pytest.fixture
async def async_client():
    """Async HTTP test client fixture for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
