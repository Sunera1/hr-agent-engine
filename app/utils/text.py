"""Text utilities used by the classifier and memory layers."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable


def normalize_text(text: str) -> str:
    """Normalize text for matching and tokenization."""

    return re.sub(r"\s+", " ", text.strip().lower())


def tokenize(text: str) -> list[str]:
    """Tokenize a string into lowercase word tokens."""

    return re.findall(r"[a-z0-9']+", normalize_text(text))


def keyword_score(text: str, keywords: Iterable[str]) -> float:
    """Return a simple overlap score between text tokens and keywords."""

    text_tokens = Counter(tokenize(text))
    keyword_tokens = [normalize_text(keyword) for keyword in keywords]
    if not keyword_tokens:
        return 0.0
    matches = sum(1 for keyword in keyword_tokens if text_tokens[keyword] > 0)
    return matches / len(keyword_tokens)


def overlap_score(text: str, candidate: str) -> float:
    """Estimate token overlap between two short text fragments."""

    text_tokens = set(tokenize(text))
    candidate_tokens = set(tokenize(candidate))
    if not text_tokens or not candidate_tokens:
        return 0.0
    return len(text_tokens & candidate_tokens) / len(text_tokens | candidate_tokens)
