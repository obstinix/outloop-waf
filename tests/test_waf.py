"""
WAF Security Tests

Tests for Web Application Firewall blocking and detection capabilities.
"""

import pytest
from fastapi.testclient import TestClient


class TestWAFBlocking:
    """Test suite for WAF threat detection and blocking."""
    
    def test_clean_request_passes(self, client: TestClient):
        """Verify legitimate requests pass through WAF."""
        response = client.get("/api/secure/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["waf_enabled"] is True
    
    def test_sql_injection_blocked(self, client: TestClient):
        """Verify SQL injection attempts are blocked."""
        malicious_payload = "'; DROP TABLE users; --"
        response = client.get(f"/api/secure/test?payload={malicious_payload}")
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"] == "Forbidden"
        assert "request_id" in data
    
    def test_union_select_blocked(self, client: TestClient):
        """Verify UNION SELECT injection is blocked."""
        response = client.get("/api/secure/test?payload=1 UNION SELECT * FROM users")
        
        assert response.status_code == 403
    
    def test_xss_script_tag_blocked(self, client: TestClient):
        """Verify XSS script tag injection is blocked."""
        response = client.get("/api/secure/test?payload=<script>alert(1)</script>")
        
        assert response.status_code == 403
    
    def test_xss_event_handler_blocked(self, client: TestClient):
        """Verify XSS event handler injection is blocked."""
        response = client.get("/api/secure/test?payload=<img onerror=alert(1)>")
        
        assert response.status_code == 403
    
    def test_path_traversal_blocked(self, client: TestClient):
        """Verify path traversal attempts are blocked."""
        response = client.get("/api/secure/test?payload=../../etc/passwd")
        
        assert response.status_code == 403
    
    def test_command_injection_blocked(self, client: TestClient):
        """Verify command injection attempts are blocked."""
        response = client.get("/api/secure/test?payload=; cat /etc/passwd")
        
        assert response.status_code == 403
    
    def test_waf_headers_present(self, client: TestClient):
        """Verify WAF adds protection headers to responses."""
        response = client.get("/api/secure/info")
        
        assert "x-waf-protected" in response.headers
        assert response.headers["x-waf-protected"] == "true"
        assert "x-waf-request-id" in response.headers
    
    def test_blocked_response_includes_request_id(self, client: TestClient):
        """Verify blocked responses include request ID for tracking."""
        response = client.get("/api/secure/test?payload=<script>")
        
        assert response.status_code == 403
        data = response.json()
        assert "request_id" in data
        assert data["request_id"].startswith("REQ-")


class TestWAFRules:
    """Test suite for specific WAF rule patterns."""
    
    @pytest.mark.parametrize("payload", [
        "SELECT * FROM users",
        "INSERT INTO logs VALUES",
        "UPDATE users SET password",
        "DELETE FROM sessions",
        "DROP TABLE users",
    ])
    def test_sql_keywords_blocked(self, client: TestClient, payload: str):
        """Verify various SQL keyword combinations are blocked."""
        response = client.get(f"/api/secure/test?payload={payload}")
        assert response.status_code == 403
    
    @pytest.mark.parametrize("payload", [
        "<iframe src='evil.com'>",
        "<object data='evil'>",
        "<embed src='evil'>",
        "javascript:alert(1)",
    ])
    def test_xss_variants_blocked(self, client: TestClient, payload: str):
        """Verify various XSS patterns are blocked."""
        response = client.get(f"/api/secure/test?payload={payload}")
        assert response.status_code == 403
    
    def test_encoded_attack_blocked(self, client: TestClient):
        """Verify URL-encoded attacks are detected and blocked."""
        # URL-encoded path traversal
        response = client.get("/api/secure/test?payload=%2e%2e%2f%2e%2e%2fetc%2fpasswd")
        assert response.status_code == 403
    
    def test_normal_text_passes(self, client: TestClient):
        """Verify normal text content passes through."""
        response = client.get("/api/secure/test?payload=Hello World")
        assert response.status_code == 200
    
    def test_json_post_with_clean_data(self, client: TestClient):
        """Verify clean POST data passes through WAF."""
        response = client.post(
            "/api/secure/process",
            json={"data": "This is legitimate data", "metadata": {"source": "test"}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["waf_verified"] is True
