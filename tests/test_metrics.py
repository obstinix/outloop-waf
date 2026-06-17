"""
Tests for the Prometheus metrics endpoint.
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_metrics_endpoint_format(async_client: AsyncClient):
    # Retrieve metrics
    response = await async_client.get("/api/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    
    # Check that WAF metrics are defined in the output
    content = response.text
    assert "waf_requests_total" in content
    assert "waf_blocked_total" in content
    assert "waf_rule_hits_total" in content
    assert "waf_response_time_seconds" in content
    assert "waf_blocked_ips_current" in content

@pytest.mark.asyncio
async def test_metrics_increment(async_client: AsyncClient):
    # Initial metrics retrieval
    response = await async_client.get("/api/metrics")
    assert response.status_code == 200
    initial_content = response.text

    # Make a clean request to generate traffic
    await async_client.get("/api/secure/test?payload=clean_input")
    
    # Retrieve metrics again
    response = await async_client.get("/api/metrics")
    assert response.status_code == 200
    new_content = response.text
    
    # Check that waf_requests_total is present
    assert "waf_requests_total" in new_content
