"""Custom exceptions and user-safe error handling."""

from __future__ import annotations


class HRAgentError(Exception):
    """Base exception for user-facing errors."""


class AgentExecutionError(HRAgentError):
    """Raised when a routed agent cannot complete its work."""


class ClassificationError(HRAgentError):
    """Raised when intent classification fails unexpectedly."""


class MemoryError(HRAgentError):
    """Raised when memory storage or retrieval fails."""

