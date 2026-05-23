"""Scheduling agent for interview and calendar requests."""

from __future__ import annotations

from app.llm.base import LLMProvider


class SchedulingAgent:
    """Handle meeting and scheduling requests."""

    name = "scheduling_agent"

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider

    def run(self, message: str, memory_context: list[dict[str, str]]) -> str:
        """Return a scheduling response using contextual memory."""

        if "force failure" in message.lower():
            raise RuntimeError("Requested scheduling failure for fallback verification.")

        memory_summary = "; ".join(item["content"] for item in memory_context[:2]) if memory_context else "no prior memory"
        prompt = (
            "You are a scheduling assistant for an HR platform. "
            f"Use this context: {memory_summary}. "
            f"Respond to: {message}"
        )
        response = self._llm.generate(prompt)
        return (
            "Scheduling request handled. "
            f"Context used: {memory_summary}. "
            f"Draft response: {response.text}"
        )
