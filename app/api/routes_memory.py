"""Memory inspection and cleanup routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import get_settings
from app.memory.memory_service import MemoryService
from app.schemas import MemoryDeleteResponse, MemoryReadResponse

router = APIRouter(tags=["memory"])


@router.get("/memory", response_model=MemoryReadResponse)
def read_memory(user_id: str | None = Query(default=None)) -> MemoryReadResponse:
    """Return STM and LTM memory, optionally scoped to a user."""

    service = MemoryService(get_settings())
    memory = service.get_memory(user_id=user_id)
    return MemoryReadResponse(user_id=user_id, stm=memory["stm"], ltm=memory["ltm"])


@router.delete("/memory", response_model=MemoryDeleteResponse)
def delete_memory(user_id: str | None = Query(default=None)) -> MemoryDeleteResponse:
    """Clear memory, optionally scoped to a user."""

    service = MemoryService(get_settings())
    service.clear_memory(user_id=user_id)
    return MemoryDeleteResponse(status="deleted", user_id=user_id)
