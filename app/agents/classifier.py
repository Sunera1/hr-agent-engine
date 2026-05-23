"""Deterministic intent classifier with confidence scoring."""

from __future__ import annotations

from dataclasses import dataclass

from app.utils.text import keyword_score, normalize_text


@dataclass(slots=True)
class ClassificationResult:
    """Intent classification output."""

    intent: str
    confidence: float
    routed_agent: str


class IntentClassifier:
    """Classify user requests into supported HR automation intents."""

    INTENT_KEYWORDS = {
        "scheduling": [
            "schedule",
            "meeting",
            "calendar",
            "interview",
            "book",
            "reschedule",
            "availability",
            "slot",
        ],
        "leave": ["leave", "vacation", "sick", "pto", "time off", "absence", "absent"],
        "compliance": [
            "policy",
            "compliance",
            "audit",
            "training",
            "code of conduct",
            "data retention",
            "nda",
        ],
    }

    def classify(self, message: str) -> ClassificationResult:
        """Return a best-effort intent with a deterministic confidence score."""

        normalized_message = normalize_text(message)
        if not normalized_message:
            return ClassificationResult(intent="clarification", confidence=1.0, routed_agent="clarification_agent")

        scores = {
            intent: keyword_score(normalized_message, keywords)
            for intent, keywords in self.INTENT_KEYWORDS.items()
        }
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        if best_score == 0:
            return ClassificationResult(intent="clarification", confidence=0.42, routed_agent="clarification_agent")

        if best_score < 0.5 and "how do i" in normalized_message:
            return ClassificationResult(intent="clarification", confidence=0.55, routed_agent="clarification_agent")

        routed_agent = f"{best_intent}_agent"
        confidence = round(min(0.95, 0.55 + best_score * 0.45), 2)
        return ClassificationResult(intent=best_intent, confidence=confidence, routed_agent=routed_agent)
