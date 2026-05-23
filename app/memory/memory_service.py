"""High-level memory service for retrieval, injection, and persistence."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.memory.ltm import LongTermMemoryRepository
from app.memory.stm import ShortTermMemoryRepository
from app.utils.text import overlap_score


class MemoryService:
    """Coordinate STM and LTM retrieval for request handling."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._stm = ShortTermMemoryRepository(self._settings)
        self._ltm = LongTermMemoryRepository(self._settings)

    def retrieve_context(self, user_id: str, message: str) -> list[dict[str, object]]:
        """Return the most relevant memory entries for a request."""

        recent_memory = self._stm.list_entries(user_id=user_id, limit=self._settings.stm_limit)
        significant_memory = self._ltm.list_entries(user_id=user_id, limit=self._settings.stm_limit)
        combined = recent_memory + significant_memory
        ranked = sorted(combined, key=lambda row: self._memory_relevance(message, row), reverse=True)
        return ranked[: self._settings.stm_limit]

    def store_request_summary(self, user_id: str, message: str, response_text: str, significance: float) -> list[dict[str, object]]:
        """Store the request in STM and, when significant, also in LTM.

        Significance combines direct signal from the classifier and simple content cues.
        High-impact items such as policy, compliance, leave approvals, or repeat workflows
        are promoted to long-term memory so future requests can reuse the context.
        """

        summary = f"Request: {message} | Response: {response_text}"
        self._stm.add_entry(user_id, summary, significance, source_request=message)
        if significance >= self._settings.ltm_significance_threshold:
            self._ltm.add_entry(user_id, summary, significance, source_request=message)
        return self.retrieve_context(user_id, message)

    def get_memory(self, user_id: str | None = None) -> dict[str, list[dict[str, object]]]:
        """Return all visible memory for API responses."""

        return {
            "stm": self._stm.list_entries(user_id=user_id, limit=self._settings.stm_limit),
            "ltm": self._ltm.list_entries(user_id=user_id, limit=self._settings.stm_limit),
        }

    def clear_memory(self, user_id: str | None = None) -> dict[str, int]:
        """Delete memory records for one user or globally."""

        return {
            "stm_deleted": self._stm.clear(user_id=user_id),
            "ltm_deleted": self._ltm.clear(user_id=user_id),
        }

    def compute_significance(self, message: str, intent: str, confidence: float) -> float:
        """Compute a bounded significance score for a request.

        The score intentionally stays simple and explainable for the prototype:
        intent-specific work matters more than casual chatter, higher classifier
        confidence increases trust, and repeated or policy-heavy language nudges
        items into long-term memory.
        """

        base = 0.35
        intent_bonus = {
            "scheduling": 0.12,
            "leave": 0.18,
            "compliance": 0.3,
            "clarification": 0.05,
        }.get(intent, 0.0)
        keyword_bonus = 0.15 if any(term in message.lower() for term in ["policy", "approved", "urgent", "repeat", "tomorrow", "deadline"]) else 0.0
        score = base + intent_bonus + (confidence * 0.3) + keyword_bonus
        return round(min(1.0, score), 2)

    def _memory_relevance(self, message: str, memory_row: dict[str, object]) -> float:
        source_text = str(memory_row.get("source_request") or memory_row.get("content") or "")
        return overlap_score(message, source_text) + float(memory_row.get("significance", 0.0)) * 0.1
