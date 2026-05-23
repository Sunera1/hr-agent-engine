"""LangGraph workflow for request orchestration."""

from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.classifier import ClassificationResult, IntentClassifier
from app.agents.clarification_agent import ClarificationAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.leave_agent import LeaveAgent
from app.agents.scheduling_agent import SchedulingAgent
from app.config import Settings, get_settings
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockLLMProvider
from app.memory.memory_service import MemoryService


class WorkflowState(TypedDict, total=False):
    user_id: str
    message: str
    memory_context: list[dict[str, object]]
    classification: ClassificationResult
    routed_agent: str
    response_text: str
    significance: float
    request_id: int
    status: str
    error_message: str


class RequestWorkflow:
    """Build and run the LangGraph orchestration flow."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        memory_service: MemoryService | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._memory_service = memory_service or MemoryService(self._settings)
        self._llm = llm_provider or MockLLMProvider()
        self._classifier = IntentClassifier()
        self._scheduling_agent = SchedulingAgent(self._llm)
        self._leave_agent = LeaveAgent(self._llm)
        self._compliance_agent = ComplianceAgent(self._llm)
        self._clarification_agent = ClarificationAgent(self._llm)
        self._graph = self._build_graph()

    def run(self, user_id: str, message: str) -> WorkflowState:
        """Execute the workflow for a single request."""

        initial_state: WorkflowState = {
            "user_id": user_id,
            "message": message,
            "status": "success",
        }
        return self._graph.invoke(initial_state)

    def _build_graph(self):
        workflow = StateGraph(WorkflowState)
        workflow.add_node("retrieve_memory", self._retrieve_memory)
        workflow.add_node("classify", self._classify)
        workflow.add_node("route_agent", self._route_agent)
        workflow.add_node("save_memory", self._save_memory)

        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "classify")
        workflow.add_edge("classify", "route_agent")
        workflow.add_edge("route_agent", "save_memory")
        workflow.add_edge("save_memory", END)
        return workflow.compile()

    def _retrieve_memory(self, state: WorkflowState) -> WorkflowState:
        memory_context = self._memory_service.retrieve_context(state["user_id"], state["message"])
        return {**state, "memory_context": memory_context}

    def _classify(self, state: WorkflowState) -> WorkflowState:
        classification = self._classifier.classify(state["message"])
        if classification.confidence < self._settings.low_confidence_threshold:
            classification = ClassificationResult(
                intent="clarification",
                confidence=classification.confidence,
                routed_agent="clarification_agent",
            )
        return {**state, "classification": classification, "routed_agent": classification.routed_agent}

    def _route_agent(self, state: WorkflowState) -> WorkflowState:
        classification = state["classification"]
        memory_context = state.get("memory_context", [])
        try:
            if classification.intent == "scheduling":
                response_text = self._scheduling_agent.run(state["message"], memory_context)
            elif classification.intent == "leave":
                response_text = self._leave_agent.run(state["message"], memory_context)
            elif classification.intent == "compliance":
                response_text = self._compliance_agent.run(state["message"], memory_context)
            else:
                response_text = self._clarification_agent.run(state["message"], memory_context)
            return {**state, "response_text": response_text}
        except Exception as exc:  # pragma: no cover - handled by orchestrator and tests
            return {
                **state,
                "status": "error",
                "error_message": str(exc),
                "response_text": "I could not complete that request right now. Please try again in a moment.",
            }

    def _save_memory(self, state: WorkflowState) -> WorkflowState:
        classification = state.get("classification")
        if not classification:
            return state
        significance = self._memory_service.compute_significance(state["message"], classification.intent, classification.confidence)
        memory_context = self._memory_service.store_request_summary(
            state["user_id"],
            state["message"],
            state.get("response_text", ""),
            significance,
        )
        return {**state, "memory_context": memory_context, "significance": significance}
