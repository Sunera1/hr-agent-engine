"""LLM provider abstraction used by the prototype agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class LLMResponse:
    """Simple structured output from an LLM provider."""

    text: str


class LLMProvider(Protocol):
    """Interface for all LLM providers."""

    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response for the supplied prompt."""
