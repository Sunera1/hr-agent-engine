"""SQLite persistence helpers for memory and audit storage."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.config import Settings, get_settings


def _resolve_sqlite_path(database_url: str) -> Path:
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this prototype.")
    raw_path = database_url.replace("sqlite:///", "", 1)
    return Path(raw_path).expanduser().resolve()


def get_database_path(settings: Settings | None = None) -> Path:
    """Return the absolute filesystem path for the configured SQLite database."""

    resolved_settings = settings or get_settings()
    return _resolve_sqlite_path(resolved_settings.database_url)


def initialize_database(settings: Settings | None = None) -> None:
    """Create all required tables if they do not already exist."""

    resolved_settings = settings or get_settings()
    database_path = get_database_path(resolved_settings)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_type TEXT NOT NULL CHECK(memory_type IN ('stm', 'ltm')),
                content TEXT NOT NULL,
                significance REAL NOT NULL,
                source_request TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                request_text TEXT NOT NULL,
                classified_intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                routed_agent TEXT NOT NULL,
                memory_used TEXT NOT NULL,
                response_text TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT
            )
            """
        )
        connection.commit()


@contextmanager
def get_connection(settings: Settings | None = None) -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with row access by column name."""

    resolved_settings = settings or get_settings()
    database_path = get_database_path(resolved_settings)
    connection = sqlite3.connect(database_path, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()
