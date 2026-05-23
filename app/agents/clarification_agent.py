"""Clarification agent for low-confidence or ambiguous requests."""

from __future__ import annotations

from app.llm.base import LLMProvider


class ClarificationAgent:
    """Ask the user for more detail when routing confidence is low."""

    name = "clarification_agent"

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def run(self, message: str, memory_context: list[dict[str, str]]) -> str:
        """Return a polite clarification request."""

        memory_summary = "; ".join(item["content"] for item in memory_context[:1]) if memory_context else "no prior memory"
        prompt = (
            "You are a clarification assistant. Ask one short follow-up question. "
            f"Use this context: {memory_summary}. "
            f"Respond to: {message}"
        )
        response = self._llm.generate(prompt)
        return (
            "I need a little more detail to route this correctly. "
            f"Context used: {memory_summary}. "
            f"Suggested follow-up: {response.text}"
        )
