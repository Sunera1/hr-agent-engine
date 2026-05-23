"""Short-term memory repository backed by SQLite."""

from __future__ import annotations

from typing import Any

from app.database import get_connection, utc_now
from app.config import Settings, get_settings


class ShortTermMemoryRepository:
    """Store and retrieve the most recent request interactions."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def add_entry(self, user_id: str, content: str, significance: float, source_request: str | None = None) -> int:
        """Insert a new STM record and prune older entries beyond the configured limit."""

        with get_connection(self._settings) as connection:
            cursor = connection.execute(
                """
                INSERT INTO memory_entries (user_id, memory_type, content, significance, source_request, created_at)
                VALUES (?, 'stm', ?, ?, ?, ?)
                """,
                (user_id, content, significance, source_request, utc_now()),
            )
            inserted_id = int(cursor.lastrowid)
            self._prune(connection, user_id)
            return inserted_id

    def list_entries(self, user_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        """Return recent STM entries, optionally for one user."""

        sql = "SELECT * FROM memory_entries WHERE memory_type = 'stm'"
        params: list[Any] = []
        if user_id:
            sql += " AND user_id = ?"
            params.append(user_id)
        sql += " ORDER BY id DESC"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        with get_connection(self._settings) as connection:
            rows = connection.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def clear(self, user_id: str | None = None) -> int:
        """Delete STM entries, either globally or for one user."""

        with get_connection(self._settings) as connection:
            if user_id:
                cursor = connection.execute("DELETE FROM memory_entries WHERE memory_type = 'stm' AND user_id = ?", (user_id,))
            else:
                cursor = connection.execute("DELETE FROM memory_entries WHERE memory_type = 'stm'")
            return int(cursor.rowcount)

    def _prune(self, connection, user_id: str) -> None:
        """Keep only the most recent STM entries for a user."""

        cursor = connection.execute(
            "SELECT id FROM memory_entries WHERE memory_type = 'stm' AND user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        rows = cursor.fetchall()
        overflow = rows[self._settings.stm_limit :]
        if overflow:
            ids = [row["id"] for row in overflow]
            bind_markers = ",".join("?" for _ in ids)
            connection.execute(f"DELETE FROM memory_entries WHERE id IN ({bind_markers})", ids)
