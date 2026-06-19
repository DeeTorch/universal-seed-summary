"""xAI Grok adapter for USS Engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from ._http import post_json
from .base import ChatMessage, ClientConfig

DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"


@dataclass(slots=True)
class GrokClient:
    """Minimal xAI Grok chat-completions client.

    The xAI API exposes OpenAI-compatible routes. This adapter uses the chat
    completions route because USS Engine's internal client contract is message based.
    """

    config: ClientConfig

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "grok-4.3",
        base_url: str | None = None,
        timeout_seconds: int = 120,
        **extra_payload: Any,
    ) -> "GrokClient":
        return cls(
            ClientConfig(
                model=model,
                api_key=os.environ.get("XAI_API_KEY"),
                base_url=base_url or os.environ.get("XAI_BASE_URL") or DEFAULT_XAI_BASE_URL,
                timeout_seconds=timeout_seconds,
                extra_payload=extra_payload or None,
            )
        )

    def complete(self, messages: list[ChatMessage]) -> str:
        api_key = self.config.api_key or os.environ.get("XAI_API_KEY")
        if not api_key:
            raise RuntimeError("XAI_API_KEY is required for GrokClient")

        base_url = (self.config.base_url or DEFAULT_XAI_BASE_URL).rstrip("/")
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
            raise RuntimeError(f"Unexpected Grok/xAI response shape: {data}") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Grok/xAI response did not contain non-empty message content")
        return content
