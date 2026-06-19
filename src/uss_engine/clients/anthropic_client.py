"""Anthropic Messages API adapter for USS Engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from ._http import post_json
from .base import ChatMessage, ClientConfig

DEFAULT_ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"


@dataclass(slots=True)
class AnthropicClient:
    """Minimal Anthropic Messages API client."""

    config: ClientConfig
    max_tokens: int = 4096

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "claude-sonnet-4-5",
        base_url: str | None = None,
        timeout_seconds: int = 120,
        max_tokens: int = 4096,
        **extra_payload: Any,
    ) -> "AnthropicClient":
        return cls(
            ClientConfig(
                model=model,
                api_key=os.environ.get("ANTHROPIC_API_KEY"),
                base_url=base_url or os.environ.get("ANTHROPIC_BASE_URL") or DEFAULT_ANTHROPIC_BASE_URL,
                timeout_seconds=timeout_seconds,
                extra_payload=extra_payload or None,
            ),
            max_tokens=max_tokens,
        )

    def complete(self, messages: list[ChatMessage]) -> str:
        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for AnthropicClient")

        system_parts: list[str] = []
        anthropic_messages: list[ChatMessage] = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                system_parts.append(content)
            elif role in {"user", "assistant"}:
                anthropic_messages.append({"role": role, "content": content})
            else:
                anthropic_messages.append({"role": "user", "content": f"[{role}]\n{content}"})

        payload: dict[str, Any] = {
            "model": self.config.model,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "messages": anthropic_messages,
            **(self.config.extra_payload or {}),
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)

        base_url = (self.config.base_url or DEFAULT_ANTHROPIC_BASE_URL).rstrip("/")
        headers = {
            "x-api-key": api_key,
            "anthropic-version": DEFAULT_ANTHROPIC_VERSION,
            **(self.config.extra_headers or {}),
        }
        data = post_json(
            url=f"{base_url}/messages",
            payload=payload,
            headers=headers,
            timeout_seconds=self.config.timeout_seconds,
        )
        try:
            blocks = data["content"]
            text = "".join(block.get("text", "") for block in blocks if block.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Anthropic response shape: {data}") from exc
        if not text.strip():
            raise RuntimeError("Anthropic response did not contain non-empty text content")
        return text
