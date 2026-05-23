"""Deterministic mock LLM provider used by default."""

from __future__ import annotations

from app.llm.base import LLMResponse


class MockLLMProvider:
    """Return short, predictable responses without external API calls."""

    def generate(self, prompt: str) -> LLMResponse:
        """Create a mock response that reflects the requested action."""

        summary = prompt.strip().splitlines()[0][:160] if prompt.strip() else "No prompt provided"
        return LLMResponse(text=f"Mock response: {summary}")
