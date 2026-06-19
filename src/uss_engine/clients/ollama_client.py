"""Ollama local/cloud chat adapter for USS Engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from ._http import post_json
from .base import ChatMessage, ClientConfig

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


@dataclass(slots=True)
class OllamaClient:
    """Minimal Ollama /api/chat client with stream disabled."""

    config: ClientConfig

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "llama3.2",
        base_url: str | None = None,
        timeout_seconds: int = 120,
        **extra_payload: Any,
    ) -> "OllamaClient":
        return cls(
            ClientConfig(
                model=model,
                api_key=os.environ.get("OLLAMA_API_KEY"),
                base_url=base_url or os.environ.get("OLLAMA_BASE_URL") or DEFAULT_OLLAMA_BASE_URL,
                timeout_seconds=timeout_seconds,
                extra_payload=extra_payload or None,
            )
        )

    def complete(self, messages: list[ChatMessage]) -> str:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            **(self.config.extra_payload or {}),
        }
        headers: dict[str, str] = {**(self.config.extra_headers or {})}
        api_key = self.config.api_key or os.environ.get("OLLAMA_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        base_url = (self.config.base_url or DEFAULT_OLLAMA_BASE_URL).rstrip("/")
        data = post_json(
            url=f"{base_url}/api/chat",
            payload=payload,
            headers=headers,
            timeout_seconds=self.config.timeout_seconds,
        )
        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Ollama response shape: {data}") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("Ollama response did not contain non-empty message content")
        return content
