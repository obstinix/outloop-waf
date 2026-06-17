"""
Admin API tests.
"""
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def setup_admin_key(monkeypatch):
    monkeypatch.setenv("WAF_ADMIN_KEY", "test_admin_key")

def test_admin_auth_required(client: TestClient):
    # Missing key
    res = client.get("/api/admin/stats")
    assert res.status_code == 422  # missing header validation error
    
    # Invalid key
    res = client.get("/api/admin/stats", headers={"X-Admin-Key": "wrong"})
    assert res.status_code == 401
    
    # Valid key
    res = client.get("/api/admin/stats", headers={"X-Admin-Key": "test_admin_key"})
    assert res.status_code == 200

def test_admin_blocklist_flow(client: TestClient):
    headers = {"X-Admin-Key": "test_admin_key"}
    
    # Block IP
    res = client.post("/api/admin/blocklist", json={"ip": "1.2.3.4", "reason": "malicious"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["blocked"] == "1.2.3.4"
    
    # Check blocklist
    res = client.get("/api/admin/blocklist", headers=headers)
    assert res.status_code == 200
    assert "1.2.3.4" in res.json()["blocked_ips"]
    
    # Unblock IP
    res = client.delete("/api/admin/blocklist/1.2.3.4", headers=headers)
    assert res.status_code == 200
    assert res.json()["unblocked"] == "1.2.3.4"
    assert res.json()["was_present"] is True

def test_admin_rules(client: TestClient):
    headers = {"X-Admin-Key": "test_admin_key"}
    res = client.get("/api/admin/rules", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "rules" in data
    assert data["count"] > 0
