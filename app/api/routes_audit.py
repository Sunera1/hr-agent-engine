"""Audit retrieval routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.audit.audit_service import AuditService
from app.config import get_settings
from app.schemas import AuditEntry

router = APIRouter(tags=["audit"])


@router.get("/audit", response_model=list[AuditEntry])
def get_audit(limit: int = Query(default=None, ge=1, le=500)) -> list[AuditEntry]:
    """Return the most recent audit entries."""

    service = AuditService(get_settings())
    rows = service.list_entries(limit=limit)
    return [AuditEntry(**row) for row in rows]
