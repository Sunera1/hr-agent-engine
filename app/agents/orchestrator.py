"""Top-level orchestrator agent used by the API layer."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.exceptions import AgentExecutionError
from app.graph.workflow import RequestWorkflow
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.llm.openai_provider import OpenAICompatibleProvider
from app.memory.memory_service import MemoryService


@dataclass(slots=True)
class OrchestrationResult:
    """Normalized result returned by the orchestrator."""

    request_id: int
    intent: str
    confidence: float
    routed_agent: str
    memory_used: list[dict[str, object]]
    response: str
    status: str
    error_message: str | None = None


class OrchestratorAgent:
    """Coordinate memory retrieval, intent routing, and agent execution."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._memory = MemoryService(self._settings)
        self._llm = self._build_provider()
        self._workflow = RequestWorkflow(settings=self._settings, memory_service=self._memory, llm_provider=self._llm)

    def _build_provider(self) -> LLMProvider:
        if self._settings.mock_llm or not self._settings.openai_api_key:
            return MockLLMProvider()
        return OpenAICompatibleProvider(api_key=self._settings.openai_api_key)

    async def handle_request(self, request_id: int, user_id: str, message: str) -> OrchestrationResult:
        """Execute the workflow with timeout handling and a user-safe fallback."""

        try:
            state = await asyncio.wait_for(
                asyncio.to_thread(self._workflow.run, user_id, message),
                timeout=self._settings.request_timeout_seconds,
            )
            classification = state["classification"]
            return OrchestrationResult(
                request_id=request_id,
                intent=classification.intent,
                confidence=classification.confidence,
                routed_agent=state.get("routed_agent", classification.routed_agent),
                memory_used=state.get("memory_context", []),
                response=state.get("response_text", ""),
                status=state.get("status", "success"),
                error_message=state.get("error_message"),
            )
        except Exception as exc:  # pragma: no cover - orchestration fallback path
            raise AgentExecutionError("The request could not be processed right now.") from exc
