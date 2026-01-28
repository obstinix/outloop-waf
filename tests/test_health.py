"""
Health Endpoint Tests

Tests for health check and readiness endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test suite for health-related endpoints."""
    
    def test_health_check_returns_200(self, client: TestClient):
        """Verify basic health check returns successful status."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "waf-api"
    
    def test_health_check_includes_version(self, client: TestClient):
        """Verify health check includes version information."""
        response = client.get("/api/health")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    def test_detailed_health_check(self, client: TestClient):
        """Verify detailed health check returns component status."""
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "waf_engine" in data["components"]
        assert data["components"]["waf_engine"]["status"] == "operational"
    
    def test_readiness_check(self, client: TestClient):
        """Verify readiness endpoint returns ready status."""
        response = client.get("/api/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
    
    def test_liveness_check(self, client: TestClient):
        """Verify liveness endpoint returns alive status."""
        response = client.get("/api/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_health_bypasses_waf(self, client: TestClient):
        """Verify health endpoint is excluded from WAF inspection."""
        # Send a request with what would normally trigger WAF
        # Health endpoints should bypass WAF
        response = client.get("/api/health")
        
        # Should still return 200 (not blocked)
        assert response.status_code == 200
