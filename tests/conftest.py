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
async def async_client():
    """Create an asynchronous HTTP client for integration testing with a custom User-Agent."""
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"User-Agent": "WAF-Test-Client"}
    ) as ac:
        yield ac


@pytest.fixture
def api_base_url():
    """Base URL for API endpoints."""
    return "/api"


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state in WAFEngine and RateLimiter before each test."""
    from api.waf.engine import waf_engine
    from api.waf.rate_limiter import rate_limiter

    waf_engine._local_blocked_ips = set()
    waf_engine._local_request_counter = 0
    waf_engine._local_blocked_counter = 0
    waf_engine._event_queue.clear()
    waf_engine._event_listeners.clear()

    rate_limiter._windows.clear()

