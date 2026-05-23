"""API tests for the HR Agent Engine prototype."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_request_endpoint_leave() -> None:
    response = client.post("/request", json={"user_id": "user_001", "message": "I need to apply for sick leave tomorrow"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["intent"] == "leave"


def test_memory_endpoints() -> None:
    client.post("/request", json={"user_id": "user_002", "message": "Please schedule a 1:1 next week"})
    response = client.get("/memory", params={"user_id": "user_002"})
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "user_002"
    assert "stm" in body
    delete_response = client.delete("/memory", params={"user_id": "user_002"})
    assert delete_response.status_code == 200


def test_audit_endpoint() -> None:
    response = client.get("/audit", params={"limit": 5})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
