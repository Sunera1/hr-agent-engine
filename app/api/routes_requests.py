"""Request processing route."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.audit.audit_service import AuditService
from app.config import get_settings
from app.exceptions import AgentExecutionError
from app.agents.orchestrator import OrchestratorAgent
from app.schemas import RequestCreate, RequestResponse

router = APIRouter(tags=["requests"])


@router.post("/request", response_model=RequestResponse)
async def process_request(payload: RequestCreate) -> RequestResponse:
    """Handle a natural language request and return a structured response."""

    settings = get_settings()
    audit_service = AuditService(settings)
    orchestrator = OrchestratorAgent(settings)

    request_id = audit_service.append_entry(
        user_id=payload.user_id,
        request_text=payload.message,
        classified_intent="pending",
        confidence=0.0,
        routed_agent="orchestrator",
        memory_used=[],
        response_text="Processing request.",
        status="started",
    )

    try:
        result = await orchestrator.handle_request(request_id, payload.user_id, payload.message)
        audit_service.append_entry(
            user_id=payload.user_id,
            request_text=payload.message,
            classified_intent=result.intent,
            confidence=result.confidence,
            routed_agent=result.routed_agent,
            memory_used=result.memory_used,
            response_text=result.response,
            status=result.status,
            error_message=result.error_message,
        )
        return RequestResponse(**asdict(result))
    except AgentExecutionError:
        error_message = "I could not complete that request right now. Please try again shortly."
        audit_service.append_entry(
            user_id=payload.user_id,
            request_text=payload.message,
            classified_intent="error",
            confidence=0.0,
            routed_agent="orchestrator",
            memory_used=[],
            response_text=error_message,
            status="error",
            error_message=error_message,
        )
        raise HTTPException(status_code=500, detail=error_message)
    except Exception:
        error_message = "The request could not be processed. Please try again later."
        audit_service.append_entry(
            user_id=payload.user_id,
            request_text=payload.message,
            classified_intent="error",
            confidence=0.0,
            routed_agent="orchestrator",
            memory_used=[],
            response_text=error_message,
            status="error",
            error_message=error_message,
        )
        raise HTTPException(status_code=500, detail=error_message)
