"""Google Gemini generateContent adapter for USS Engine."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from ._http import post_json
from .base import ChatMessage, ClientConfig

DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


@dataclass(slots=True)
class GeminiClient:
    """Minimal Gemini generateContent client.

    The adapter converts USS runtime chat messages into Gemini `contents` parts.
    System prompt content is folded into the first user content block so the
    engine can use the same LLMClient contract as other providers.
    """

    config: ClientConfig

    @classmethod
    def from_env(
        cls,
        *,
        model: str = "gemini-3.5-flash",
        base_url: str | None = None,
        timeout_seconds: int = 120,
        **extra_payload: Any,
    ) -> "GeminiClient":
        return cls(
            ClientConfig(
                model=model,
                api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
                base_url=base_url or os.environ.get("GEMINI_BASE_URL") or DEFAULT_GEMINI_BASE_URL,
                timeout_seconds=timeout_seconds,
                extra_payload=extra_payload or None,
            )
        )

    def complete(self, messages: list[ChatMessage]) -> str:
        api_key = self.config.api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is required for GeminiClient")

        payload: dict[str, Any] = {
            "contents": _messages_to_gemini_contents(messages),
            "generationConfig": {"temperature": 0},
            **(self.config.extra_payload or {}),
        }
        base_url = (self.config.base_url or DEFAULT_GEMINI_BASE_URL).rstrip("/")
        query = urlencode({"key": api_key})
        data = post_json(
            url=f"{base_url}/models/{self.config.model}:generateContent?{query}",
            payload=payload,
            headers={**(self.config.extra_headers or {})},
            timeout_seconds=self.config.timeout_seconds,
        )
        try:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Gemini response shape: {data}") from exc
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Gemini response did not contain non-empty text content")
        return text


def _messages_to_gemini_contents(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    system_parts: list[str] = []
    contents: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if role == "system":
            system_parts.append(content)
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": content}]})

    if system_parts:
        system_text = "\n\n".join(system_parts)
        if contents and contents[0]["role"] == "user":
            contents[0]["parts"].insert(
                0,
                {"text": f"SYSTEM INSTRUCTIONS:\n{system_text}\n\nUSER TASK:"},
            )
        else:
            contents.insert(
                0,
                {"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_text}"}]},
            )
    return contents or [{"role": "user", "parts": [{"text": "Generate a USS artifact."}]}]
