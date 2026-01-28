"""
Pytest test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from api.index import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def api_base_url():
    """Base URL for API endpoints."""
    return "/api"
