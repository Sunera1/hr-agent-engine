"""Optional OpenAI-compatible provider for environments with an API key."""

from __future__ import annotations

import json

import httpx

from app.llm.base import LLMResponse


class OpenAICompatibleProvider:
    """Minimal OpenAI-compatible provider using the chat completions endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout_seconds: int = 10,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> LLMResponse:
        """Call an OpenAI-compatible chat completion endpoint."""

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": "You are a concise HR automation assistant."},
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(f"{self._base_url}/chat/completions", headers=headers, content=json.dumps(payload))
            response.raise_for_status()
            body = response.json()
        text = body["choices"][0]["message"]["content"]
        return LLMResponse(text=text)
