"""Compliance and policy agent."""

from __future__ import annotations

from app.llm.base import LLMProvider


class ComplianceAgent:
    """Handle compliance policy and audit requests."""

    name = "compliance_agent"

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def run(self, message: str, memory_context: list[dict[str, str]]) -> str:
        """Return a compliance-oriented response using memory context."""

        memory_summary = "; ".join(item["content"] for item in memory_context[:2]) if memory_context else "no prior memory"
        prompt = (
            "You are a compliance assistant for an HR platform. "
            f"Use this context: {memory_summary}. "
            f"Respond to: {message}"
        )
        response = self._llm.generate(prompt)
        return (
            "Compliance request handled. "
            f"Context used: {memory_summary}. "
            f"Draft response: {response.text}"
        )
