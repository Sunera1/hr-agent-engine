"""Pydantic request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RequestCreate(BaseModel):
    """Incoming natural-language request."""

    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class MemoryItem(BaseModel):
    """Single memory entry returned by the API."""

    id: int
    user_id: str
    memory_type: str
    content: str
    significance: float
    created_at: datetime


class RequestResponse(BaseModel):
    """Structured response for processed requests."""

    request_id: int
    intent: str
    confidence: float
    routed_agent: str
    memory_used: list[dict[str, Any]]
    response: str
    status: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    app_name: str
    database: str


class AuditEntry(BaseModel):
    """Audit log entry."""

    id: int
    timestamp: datetime
    user_id: str
    request_text: str
    classified_intent: str
    confidence: float
    routed_agent: str
    memory_used: str
    response_text: str
    status: str
    error_message: str | None = None


class MemoryReadResponse(BaseModel):
    """Combined STM and LTM response."""

    user_id: str | None
    stm: list[MemoryItem]
    ltm: list[MemoryItem]


class MemoryDeleteResponse(BaseModel):
    """Response for memory deletion."""

    status: str
    user_id: str | None = None

