"""LLM client contracts for USS Engine.

The engine core depends only on this small interface. Provider-specific modules
may use network APIs, local runtimes, or internal gateways, but they must return
one candidate USS Markdown artifact per `complete()` call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


ChatMessage = dict[str, str]


@runtime_checkable
class LLMClient(Protocol):
    """Minimal client contract required by USS Engine generation."""

    def complete(self, messages: list[ChatMessage]) -> str:
        """Return a USS Markdown artifact candidate."""


@dataclass(slots=True)
class StaticLLMClient:
    """Deterministic test/demo client that returns predefined outputs.

    This lives in `clients.base` so provider adapters and the generator can share
    the same contract without importing from orchestration code.
    """

    outputs: list[str]

    def complete(self, messages: list[ChatMessage]) -> str:  # noqa: ARG002
        if not self.outputs:
            raise RuntimeError("StaticLLMClient has no outputs remaining")
        return self.outputs.pop(0)


@dataclass(slots=True)
class ClientConfig:
    """Common provider client settings."""

    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 120
    extra_headers: dict[str, str] | None = None
    extra_payload: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.model or not self.model.strip():
            raise ValueError("model is required")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be positive")
