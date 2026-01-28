"""
Gravity Endpoint Tests

Tests for gravity state endpoint behavior under various conditions.
"""

import pytest
from fastapi.testclient import TestClient


class TestGravityEndpoint:
    """Test suite for gravity endpoint."""
    
    def test_gravity_returns_enabled_by_default(self, client: TestClient):
        """Verify gravity is enabled under normal conditions."""
        response = client.get("/api/gravity")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
        assert data["gravity_constant"] == 9.80665
        assert data["unit"] == "m/s²"
    
    def test_gravity_includes_timestamp(self, client: TestClient):
        """Verify response includes timestamp."""
        response = client.get("/api/gravity")
        data = response.json()
        
        assert "timestamp" in data
    
    def test_gravity_constants_endpoint(self, client: TestClient):
        """Verify gravity constants reference endpoint."""
        response = client.get("/api/gravity/constants")
        
        assert response.status_code == 200
        data = response.json()
        assert "earth" in data
        assert "moon" in data
        assert "mars" in data
        assert data["earth"]["surface_gravity"] == 9.80665
    
    def test_gravity_header_present(self, client: TestClient):
        """Verify X-Gravity-State header is set."""
        response = client.get("/api/gravity")
        
        assert "x-gravity-state" in response.headers
        assert response.headers["x-gravity-state"] == "enabled"
    
    def test_gravity_with_invalid_code(self, client: TestClient):
        """Verify gravity remains enabled with incorrect code."""
        response = client.get("/api/gravity?code=12345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
    
    def test_gravity_header_only_not_sufficient(self, client: TestClient):
        """Verify header alone does not change gravity state."""
        response = client.get(
            "/api/gravity",
            headers={"X-Antigravity": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
    
    def test_gravity_code_only_not_sufficient(self, client: TestClient):
        """Verify code alone does not change gravity state."""
        # Using a code value for testing
        response = client.get("/api/gravity?code=1807")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"


class TestGravityValidation:
    """Test suite for gravity state validation logic."""
    
    def test_complete_activation_sequence(self, client: TestClient):
        """
        Verify gravity state changes when all conditions are met.
        
        This test documents the expected behavior when specific
        request parameters are provided together.
        """
        response = client.get(
            "/api/gravity?code=1807",
            headers={"X-Antigravity": "true"}
        )
        
        # When both conditions are met, special behavior activates
        assert response.status_code == 418  # I'm a teapot
        data = response.json()
        assert data["status"] == "disabled 🚀"
        assert data["gravity_constant"] == 0.0
        assert "message" in data
    
    def test_activation_with_cli_user_agent(self, client: TestClient):
        """Verify activation works with CLI user agents."""
        response = client.get(
            "/api/gravity?code=1807",
            headers={
                "X-Antigravity": "true",
                "User-Agent": "python-requests/2.28.0"
            }
        )
        
        assert response.status_code == 418
        data = response.json()
        assert data["_meta"]["context"] == "cli"
    
    def test_activation_with_browser_user_agent(self, client: TestClient):
        """Verify activation works with browser user agents."""
        response = client.get(
            "/api/gravity?code=1807",
            headers={
                "X-Antigravity": "true",
                "User-Agent": "Mozilla/5.0"
            }
        )
        
        assert response.status_code == 418
        data = response.json()
        assert data["_meta"]["context"] == "browser"
    
    def test_activation_response_headers(self, client: TestClient):
        """Verify special headers are set on activation."""
        response = client.get(
            "/api/gravity?code=1807",
            headers={"X-Antigravity": "true"}
        )
        
        assert response.headers["x-gravity-state"] == "disabled"
        assert response.headers["x-flight-status"] == "cleared-for-takeoff"
    
    def test_header_case_insensitivity(self, client: TestClient):
        """Verify header matching is case-insensitive for value."""
        response = client.get(
            "/api/gravity?code=1807",
            headers={"X-Antigravity": "TRUE"}
        )
        
        assert response.status_code == 418
    
    def test_wrong_code_format_remains_normal(self, client: TestClient):
        """Verify non-numeric code doesn't cause errors."""
        response = client.get(
            "/api/gravity?code=notanumber",
            headers={"X-Antigravity": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
