"""Long-term memory repository backed by SQLite."""

from __future__ import annotations

from typing import Any

from app.database import get_connection, utc_now
from app.config import Settings, get_settings


class LongTermMemoryRepository:
    """Store and retrieve significant long-term memory entries."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def add_entry(self, user_id: str, content: str, significance: float, source_request: str | None = None) -> int:
        """Insert a new LTM record."""

        with get_connection(self._settings) as connection:
            cursor = connection.execute(
                """
                INSERT INTO memory_entries (user_id, memory_type, content, significance, source_request, created_at)
                VALUES (?, 'ltm', ?, ?, ?, ?)
                """,
                (user_id, content, significance, source_request, utc_now()),
            )
            return int(cursor.lastrowid)

    def list_entries(self, user_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        """Return long-term memory entries, optionally scoped to a user."""

        sql = "SELECT * FROM memory_entries WHERE memory_type = 'ltm'"
        params: list[Any] = []
        if user_id:
            sql += " AND user_id = ?"
            params.append(user_id)
        sql += " ORDER BY significance DESC, id DESC"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        with get_connection(self._settings) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def clear(self, user_id: str | None = None) -> int:
        """Delete LTM entries, either globally or for one user."""

        with get_connection(self._settings) as connection:
            if user_id:
                cursor = connection.execute("DELETE FROM memory_entries WHERE memory_type = 'ltm' AND user_id = ?", (user_id,))
            else:
                cursor = connection.execute("DELETE FROM memory_entries WHERE memory_type = 'ltm'")
            return int(cursor.rowcount)
