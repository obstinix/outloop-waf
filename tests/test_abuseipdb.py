"""
AbuseIPDB Threat Intelligence Integration Tests
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from httpx import Response

from api.core.abuseipdb import abuse_ipdb_client, AbuseIPDBClient
import api.core.abuseipdb as abuseipdb_module


@pytest.fixture(autouse=True)
def clean_abuseipdb_cache():
    """Clear AbuseIPDB client cache before each test."""
    abuse_ipdb_client._memory_cache.clear()
    yield


@pytest.mark.asyncio
async def test_abuseipdb_disabled_when_key_missing():
    """Verify AbuseIPDB client returns None if API key is not configured."""
    with patch.object(abuseipdb_module, "ABUSEIPDB_API_KEY", None):
        score = await abuse_ipdb_client.get_abuse_score("1.2.3.4")
        assert score is None


@pytest.mark.asyncio
async def test_abuseipdb_fetches_and_caches_score():
    """Verify AbuseIPDB client queries the endpoint and caches the result."""
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "ipAddress": "1.2.3.4",
            "abuseConfidenceScore": 92
        }
    }

    with patch.object(abuseipdb_module, "ABUSEIPDB_API_KEY", "mock-key"):
        # Mock httpx AsyncClient.get
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            # First query should call API
            score = await abuse_ipdb_client.get_abuse_score("1.2.3.4")
            assert score == 92
            assert mock_get.call_count == 1

            # Second query should hit cache (call_count remains 1)
            score_cached = await abuse_ipdb_client.get_abuse_score("1.2.3.4")
            assert score_cached == 92
            assert mock_get.call_count == 1


@pytest.mark.asyncio
async def test_abuseipdb_fails_gracefully():
    """Verify client handles API errors gracefully and fails open (returns None)."""
    with patch.object(abuseipdb_module, "ABUSEIPDB_API_KEY", "mock-key"):
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            # Simulate connection error
            mock_get.side_effect = Exception("Connection Timeout")

            score = await abuse_ipdb_client.get_abuse_score("1.2.3.4")
            assert score is None


def test_pre_waf_blocking_by_abuseipdb(client: TestClient):
    """Verify WAFMiddleware intercepts and blocks requests with high abuse score pre-WAF."""
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(
        spec=Response,
        status_code=200,
        json=MagicMock(return_value={
            "data": {
                "ipAddress": "8.8.8.8",
                "abuseConfidenceScore": 95
            }
        })
    )

    with patch.object(abuseipdb_module, "ABUSEIPDB_API_KEY", "mock-key"):
        with patch("httpx.AsyncClient.get", mock_get):
            # Send normal request that should be blocked by AbuseIPDB before WAF inspection
            response = client.get("/api/secure/test?payload=safe_input")
            
            assert response.status_code == 403
            assert response.json()["error"] == "Forbidden"
            assert "blocked by Security threat intelligence" in response.json()["message"]
            assert "X-WAF-Block" in response.headers
            assert response.headers["X-WAF-Block"] == "true"
            assert "REQ-" in response.headers["X-WAF-Request-ID"]
            assert "-ABUSE" in response.headers["X-WAF-Request-ID"]


def test_pre_waf_allows_below_threshold(client: TestClient):
    """Verify requests with low abuse scores pass pre-WAF checks."""
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(
        spec=Response,
        status_code=200,
        json=MagicMock(return_value={
            "data": {
                "ipAddress": "8.8.8.8",
                "abuseConfidenceScore": 40
            }
        })
    )

    with patch.object(abuseipdb_module, "ABUSEIPDB_API_KEY", "mock-key"):
        with patch("httpx.AsyncClient.get", mock_get):
            response = client.get("/api/secure/test?payload=safe_input")
            # Should bypass pre-WAF check and return 200 OK
            assert response.status_code == 200
