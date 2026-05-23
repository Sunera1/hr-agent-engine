"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes_audit import router as audit_router
from app.api.routes_health import router as health_router
from app.api.routes_memory import router as memory_router
from app.api.routes_requests import router as requests_router
from app.config import get_settings
from app.database import initialize_database


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""

    settings = get_settings()
    initialize_database(settings)
    application = FastAPI(title=settings.app_name, version="0.1.0")

    @application.exception_handler(Exception)
    async def global_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "An internal error occurred. Please try again later."})

    application.include_router(health_router)
    application.include_router(requests_router)
    application.include_router(audit_router)
    application.include_router(memory_router)
    return application


app = create_app()
