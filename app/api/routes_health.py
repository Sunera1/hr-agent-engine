"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.database import get_database_path
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a simple service health response."""

    settings = get_settings()
    database_path = get_database_path(settings)
    database_status = "connected" if database_path.exists() else "not initialized"
    return HealthResponse(status="ok", app_name=settings.app_name, database=database_status)
