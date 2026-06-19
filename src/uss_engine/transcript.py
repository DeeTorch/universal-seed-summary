"""Transcript normalization for USS Engine v0.2.

This module converts raw chat text or JSON exports into a normalized thread object.
The normalized thread becomes the stable input contract for prompt compilation and
LLM generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TranscriptRole(StrEnum):
    """Supported normalized speaker roles."""

    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"
    developer = "developer"
    unknown = "unknown"


ROLE_ALIASES: dict[str, TranscriptRole] = {
    "system": TranscriptRole.system,
    "developer": TranscriptRole.developer,
    "user": TranscriptRole.user,
    "human": TranscriptRole.user,
    "me": TranscriptRole.user,
    "assistant": TranscriptRole.assistant,
    "ai": TranscriptRole.assistant,
    "chatgpt": TranscriptRole.assistant,
    "model": TranscriptRole.assistant,
    "tool": TranscriptRole.tool,
    "function": TranscriptRole.tool,
}

ROLE_LINE_RE = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?P<role>system|developer|user|human|me|assistant|ai|chatgpt|model|tool|function)\s*[:：-]\s*(?P<content>.*)$",
    re.IGNORECASE,
)

DELIMITER_RE = re.compile(r"^\s*(?:---+|===+|\*\*\*+)\s*$")


class TranscriptMessage(BaseModel):
    """One normalized message in a conversation thread."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:12]}")
    role: TranscriptRole
    content: str
    timestamp: str | None = None
    source_index: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("message content cannot be empty")
        return value.strip()

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_iso_when_present(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("timestamp must be ISO-8601 compatible") from exc
        return value


class NormalizedThread(BaseModel):
    """Canonical transcript format consumed by USS Engine prompt compilation."""

    model_config = ConfigDict(extra="allow")

    thread_id: str = Field(default_factory=lambda: f"thread_{uuid4().hex[:12]}")
    source: str = "unknown"
    created_at: str = Field(default_factory=lambda: _now_utc())
    messages: list[TranscriptMessage]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("messages")
    @classmethod
    def messages_must_not_be_empty(cls, value: list[TranscriptMessage]) -> list[TranscriptMessage]:
        if not value:
            raise ValueError("normalized thread must contain at least one message")
        return value

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_iso(cls, value: str) -> str:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @model_validator(mode="after")
    def assign_source_indices(self) -> "NormalizedThread":
        for index, message in enumerate(self.messages):
            if message.source_index is None:
                message.source_index = index
        return self

    @property
    def exchange_pair_count(self) -> int:
        """Best-effort count of user/assistant exchange pairs."""

        user_count = sum(1 for message in self.messages if message.role == TranscriptRole.user)
        assistant_count = sum(1 for message in self.messages if message.role == TranscriptRole.assistant)
        return min(user_count, assistant_count)

    @property
    def char_count(self) -> int:
        return sum(len(message.content) for message in self.messages)

    def to_prompt_block(self, *, max_chars: int | None = None) -> str:
        """Render a deterministic transcript block for runtime prompt compilation."""

        lines: list[str] = []
        total_chars = 0
        for message in self.messages:
            header = f"[{message.id}] role={message.role.value}"
            if message.timestamp:
                header += f" timestamp={message.timestamp}"
            content = message.content.strip()
            chunk = f"{header}\n{content}"
            if max_chars is not None and total_chars + len(chunk) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 200:
                    lines.append(chunk[:remaining].rstrip() + "\n[TRUNCATED_BY_PROMPT_BUDGET]")
                lines.append("[TRANSCRIPT_TRUNCATED]")
                break
            lines.append(chunk)
            total_chars += len(chunk)
        return "\n\n--- MESSAGE ---\n\n".join(lines)


def normalize_transcript_text(
    text: str,
    *,
    thread_id: str | None = None,
    source: str = "raw_text",
    created_at: str | None = None,
) -> NormalizedThread:
    """Normalize simple role-prefixed chat text.

    Supported examples:

    User: Build the tool.
    Assistant: Here is a plan.

    Lines that do not begin with a role are appended to the current message. If no
    role line is found, the whole text becomes a single user message.
    """

    raw = text.strip()
    if not raw:
        raise ValueError("transcript text cannot be empty")

    messages: list[TranscriptMessage] = []
    current_role: TranscriptRole | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_role, current_lines
        content = "\n".join(current_lines).strip()
        if current_role is not None and content:
            messages.append(
                TranscriptMessage(
                    role=current_role,
                    content=content,
                    source_index=len(messages),
                )
            )
        current_role = None
        current_lines = []

    for line in raw.splitlines():
        if DELIMITER_RE.match(line) and current_role is None:
            continue
        match = ROLE_LINE_RE.match(line)
        if match:
            flush()
            role_text = match.group("role").lower().strip()
            current_role = ROLE_ALIASES.get(role_text, TranscriptRole.unknown)
            first_content = match.group("content")
            current_lines = [first_content] if first_content else []
            continue
        if current_role is None:
            current_role = TranscriptRole.user
        current_lines.append(line)

    flush()

    if not messages:
        messages.append(TranscriptMessage(role=TranscriptRole.user, content=raw, source_index=0))

    return NormalizedThread(
        thread_id=thread_id or f"thread_{uuid4().hex[:12]}",
        source=source,
        created_at=created_at or _now_utc(),
        messages=messages,
    )


def normalize_transcript_json(
    payload: dict[str, Any],
    *,
    thread_id: str | None = None,
    source: str | None = None,
) -> NormalizedThread:
    """Normalize a JSON transcript payload.

    Expected minimal input:

    {
      "thread_id": "example",
      "source": "chatgpt_export",
      "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
      ]
    }

    The normalizer is intentionally permissive with common key aliases, then emits
    a strict NormalizedThread model.
    """

    if not isinstance(payload, dict):
        raise TypeError("JSON transcript payload must be an object")

    raw_messages = payload.get("messages") or payload.get("conversation") or payload.get("items")
    if not isinstance(raw_messages, list) or not raw_messages:
        raise ValueError("JSON transcript must contain a non-empty 'messages' list")

    messages: list[TranscriptMessage] = []
    for index, item in enumerate(raw_messages):
        if not isinstance(item, dict):
            raise ValueError(f"message at index {index} must be an object")

        role_raw = str(item.get("role") or item.get("speaker") or item.get("author") or "unknown")
        role = ROLE_ALIASES.get(role_raw.lower().strip(), TranscriptRole.unknown)
        content = item.get("content") or item.get("text") or item.get("message")
        if isinstance(content, list):
            content = "\n".join(str(part) for part in content)
        if content is None:
            raise ValueError(f"message at index {index} is missing content/text/message")

        message_id = str(item.get("id") or item.get("message_id") or f"msg_{index + 1:04d}")
        metadata = {key: value for key, value in item.items() if key not in {"id", "message_id", "role", "speaker", "author", "content", "text", "message", "timestamp", "created_at"}}
        messages.append(
            TranscriptMessage(
                id=message_id,
                role=role,
                content=str(content),
                timestamp=item.get("timestamp") or item.get("created_at"),
                source_index=index,
                metadata=metadata,
            )
        )

    return NormalizedThread(
        thread_id=thread_id or str(payload.get("thread_id") or payload.get("id") or f"thread_{uuid4().hex[:12]}"),
        source=source or str(payload.get("source") or "json"),
        created_at=str(payload.get("created_at") or _now_utc()),
        messages=messages,
        metadata={key: value for key, value in payload.items() if key not in {"thread_id", "id", "source", "created_at", "messages", "conversation", "items"}},
    )


def load_thread(path: str | Path) -> NormalizedThread:
    """Load and normalize a transcript from .json, .md, or .txt."""

    input_path = Path(path)
    text = input_path.read_text(encoding="utf-8")
    if input_path.suffix.lower() == ".json":
        payload = json.loads(text)
        return normalize_transcript_json(payload, source=payload.get("source") if isinstance(payload, dict) else None)
    return normalize_transcript_text(text, source=input_path.suffix.lower().lstrip(".") or "text")


def save_thread(thread: NormalizedThread, path: str | Path) -> None:
    """Persist a normalized thread as pretty JSON."""

    output_path = Path(path)
    output_path.write_text(
        json.dumps(thread.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
