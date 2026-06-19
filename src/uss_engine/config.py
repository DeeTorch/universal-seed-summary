"""Environment and provider configuration helpers for USS Engine v1.1.

This module intentionally avoids third-party dotenv dependencies. It supports a
small, safe subset of `.env` files for local development while keeping secrets
out of source code and generated reports.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ProviderSecretKind(StrEnum):
    """Known provider secret families."""

    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"
    grok = "grok"
    xai = "xai"
    ollama = "ollama"


PROVIDER_ENV_KEYS: dict[str, tuple[str, ...]] = {
    "openai": ("OPENAI_API_KEY",),
    "anthropic": ("ANTHROPIC_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "grok": ("XAI_API_KEY",),
    "xai": ("XAI_API_KEY",),
    "ollama": ("OLLAMA_API_KEY",),
}


@dataclass(frozen=True, slots=True)
class ProviderSecretStatus:
    """Safe provider secret status for CLI display.

    Never stores or prints the actual key.
    """

    provider: str
    configured: bool
    env_key: str | None = None
    source: str | None = None


@dataclass(frozen=True, slots=True)
class EnvLoadResult:
    """Result of loading a dotenv-style file."""

    path: str
    loaded_keys: tuple[str, ...]
    skipped_keys: tuple[str, ...]


def load_env_file(path: str | Path = ".env", *, override: bool = False) -> EnvLoadResult:
    """Load simple KEY=VALUE lines into `os.environ`.

    Supported:
    - blank lines and comments
    - KEY=VALUE
    - optional single or double quotes around values
    Unsupported shell syntax is ignored rather than executed.
    """

    env_path = Path(path)
    if not env_path.exists():
        return EnvLoadResult(path=str(env_path), loaded_keys=(), skipped_keys=())

    loaded: list[str] = []
    skipped: list[str] = []
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            skipped.append(line)
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not _valid_env_key(key):
            skipped.append(key)
            continue
        if key in os.environ and not override:
            skipped.append(key)
            continue
        os.environ[key] = value
        loaded.append(key)
    return EnvLoadResult(path=str(env_path), loaded_keys=tuple(loaded), skipped_keys=tuple(skipped))


def provider_secret_status(provider: str) -> ProviderSecretStatus:
    """Return whether the provider has a usable secret in the environment."""

    key = provider.strip().lower()
    env_names = PROVIDER_ENV_KEYS.get(key, ())
    if key == "ollama" and os.environ.get("OLLAMA_BASE_URL"):
        # Local Ollama usually needs no API key. A base URL counts as configured.
        return ProviderSecretStatus(provider=key, configured=True, env_key="OLLAMA_BASE_URL", source="env")
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value and value.strip():
            return ProviderSecretStatus(provider=key, configured=True, env_key=env_name, source="env")
    if key == "ollama":
        # Default local server path can still be tried without a key.
        return ProviderSecretStatus(provider=key, configured=True, env_key=None, source="default_local")
    return ProviderSecretStatus(provider=key, configured=False, env_key=env_names[0] if env_names else None, source=None)


def all_provider_secret_statuses() -> list[ProviderSecretStatus]:
    """Return status for all supported external provider families."""

    return [provider_secret_status(name) for name in ("openai", "anthropic", "gemini", "grok", "ollama")]


def _valid_env_key(key: str) -> bool:
    if not key:
        return False
    return all(ch.isalnum() or ch == "_" for ch in key) and not key[0].isdigit()
