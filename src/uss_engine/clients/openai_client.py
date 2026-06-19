"""OpenAI Chat Completions adapter for USS Engine.

This adapter intentionally uses only the Python standard library so USS Engine's
core package stays dependency-light. It can be replaced by the official SDK in
application code without changing the `LLMClient` contract.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from ._http import post_json
from .base import ChatMessage, ClientConfig

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


@dataclass(slots=True)
class OpenAIClient:
    """Minimal OpenAI-compatible chat-completions client."""

    config: ClientConfig

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "gpt-4.1-mini",
        base_url: str | None = None,
        timeout_seconds: int = 120,
        **extra_payload: Any,
    ) -> "OpenAIClient":
        return cls(
            ClientConfig(
                model=model,
                api_key=os.environ.get("OPENAI_API_KEY"),
                base_url=base_url or os.environ.get("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE_URL,
                timeout_seconds=timeout_seconds,
                extra_payload=extra_payload or None,
            )
        )

    def complete(self, messages: list[ChatMessage]) -> str:
        api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIClient")

        base_url = (self.config.base_url or DEFAULT_OPENAI_BASE_URL).rstrip("/")
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0,
            **(self.config.extra_payload or {}),
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            **(self.config.extra_headers or {}),
        }
        data = post_json(
            url=f"{base_url}/chat/completions",
            payload=payload,
            headers=headers,
            timeout_seconds=self.config.timeout_seconds,
        )
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected OpenAI response shape: {data}") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenAI response did not contain non-empty message content")
        return content
