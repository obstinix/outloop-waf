"""
Rate limiting tests.
"""
import pytest
from fastapi.testclient import TestClient

def test_rate_limiter_blocks_burst(client: TestClient):
    # Burst limit is 20 requests per second.
    # Send 20 requests (which should pass).
    for _ in range(20):
        res = client.get("/api/secure/test")
        assert res.status_code == 200
    
    # 21st request should be blocked with HTTP 429
    res = client.get("/api/secure/test")
    assert res.status_code == 429
    assert res.headers["x-waf-rate-limited"] == "true"
    assert "Retry-After" in res.headers
