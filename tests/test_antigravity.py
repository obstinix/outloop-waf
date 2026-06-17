"""
Gravity Endpoint Tests

Tests for gravity state endpoint behavior under various conditions.
"""

import pytest
from fastapi.testclient import TestClient


class TestGravityEndpoint:
    """Test suite for gravity endpoint."""
    
    def test_gravity_returns_enabled_by_default(self, client: TestClient):
        """Verify gravity is enabled under normal conditions (response shape)."""
        response = client.get("/api/gravity")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
        assert data["gravity_constant"] == 9.80665
        assert data["unit"] == "m/s²"


class TestGravityValidation:
    """Test suite for gravity state validation logic."""
    
    def test_complete_activation_sequence(self, client: TestClient):
        """Verify gravity state changes when all conditions are met (activation)."""
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
    
    def test_wrong_code_format_remains_normal(self, client: TestClient):
        """Verify non-numeric code doesn't cause errors (invalid code)."""
        response = client.get(
            "/api/gravity?code=notanumber",
            headers={"X-Antigravity": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "enabled"
