"""Append-only audit service for request traceability."""

from __future__ import annotations

import json
from typing import Any

from app.config import Settings, get_settings
from app.database import get_connection, utc_now


class AuditService:
    """Persist and retrieve audit entries without update or delete actions."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def append_entry(
        self,
        *,
        user_id: str,
        request_text: str,
        classified_intent: str,
        confidence: float,
        routed_agent: str,
        memory_used: list[dict[str, Any]],
        response_text: str,
        status: str,
        error_message: str | None = None,
    ) -> int:
        """Append a single audit entry and return its database id."""

        with get_connection(self._settings) as connection:
            cursor = connection.execute(
                """
                INSERT INTO audit_log (
                    timestamp, user_id, request_text, classified_intent, confidence,
                    routed_agent, memory_used, response_text, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    user_id,
                    request_text,
                    classified_intent,
                    confidence,
                    routed_agent,
                    json.dumps(memory_used, ensure_ascii=False),
                    response_text,
                    status,
                    error_message,
                ),
            )
            return int(cursor.lastrowid)

    def list_entries(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Return the most recent audit entries."""

        sql = "SELECT * FROM audit_log ORDER BY id DESC"
        params: list[Any] = []
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        with get_connection(self._settings) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
