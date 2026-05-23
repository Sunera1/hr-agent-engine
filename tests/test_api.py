"""API tests for the HR Agent Engine prototype."""

from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient
import pytest

from app.audit.audit_service import AuditService
from app.config import get_settings
from app.database import get_connection
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
    client.post("/request", json={"user_id": "audit_user", "message": "What is the compliance training policy?"})
    response = client.get("/audit", params={"limit": 5})
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body
    required_fields = {
        "id",
        "timestamp",
        "user_id",
        "request_text",
        "classified_intent",
        "confidence",
        "routed_agent",
        "memory_used",
        "response_text",
        "status",
        "error_message",
    }
    assert required_fields.issubset(body[0].keys())


def test_uncertain_request_routes_to_clarification() -> None:
    response = client.post("/request", json={"user_id": "user_003", "message": "Can you help me with this?"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "clarification"
    assert body["routed_agent"] == "clarification_agent"


def test_fallback_response_hides_stack_trace() -> None:
    response = client.post("/request", json={"user_id": "user_004", "message": "Please schedule a meeting and force failure"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"
    assert "Traceback" not in body["response"]


def test_audit_log_is_append_only() -> None:
    settings = get_settings()
    audit_id = AuditService(settings).append_entry(
        user_id="append_only_user",
        request_text="Check audit append only",
        classified_intent="clarification",
        confidence=0.0,
        routed_agent="clarification_agent",
        memory_used=[],
        response_text="Audit check.",
        status="success",
    )

    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(settings) as connection:
            connection.execute("UPDATE audit_log SET status = ? WHERE id = ?", ("edited", audit_id))

    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(settings) as connection:
            connection.execute("DELETE FROM audit_log WHERE id = ?", (audit_id,))
