"""Small JSON-over-HTTP helper functions for USS Engine provider clients."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SENSITIVE_QUERY_KEYS = {
    "key",
    "api_key",
    "apikey",
    "access_token",
    "token",
    "password",
}


def redact_secrets(value: str) -> str:
    """Best-effort redaction for URLs, query params, and common API key shapes."""
    redacted = value

    redacted = re.sub(
        r"(?i)(key|api_key|apikey|access_token|token|password)=([^&\s\"']+)",
        r"\1=<REDACTED>",
        redacted,
    )
    redacted = re.sub(
        r"(?i)(bearer\s+)[A-Za-z0-9._\-+/=]+",
        r"\1<REDACTED>",
        redacted,
    )
    redacted = re.sub(
        r"AIza[0-9A-Za-z_\-]{20,}",
        "<REDACTED_GOOGLE_API_KEY>",
        redacted,
    )
    redacted = re.sub(
        r"sk-[A-Za-z0-9_\-]{20,}",
        "<REDACTED_API_KEY>",
        redacted,
    )

    return redacted


def redact_url(url: str) -> str:
    """Redact sensitive query values from a URL before including it in errors."""
    try:
        parts = urlsplit(url)
        query_pairs = parse_qsl(parts.query, keep_blank_values=True)
        safe_pairs = [
            (key, "<REDACTED>" if key.lower() in SENSITIVE_QUERY_KEYS else value)
            for key, value in query_pairs
        ]
        safe_query = urlencode(safe_pairs)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, safe_query, parts.fragment))
    except Exception:
        return redact_secrets(url)


def post_json(
    *,
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    """POST JSON and return parsed JSON, raising sanitized RuntimeError on failure."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        safe_url = redact_url(url)
        safe_detail = redact_secrets(detail)
        raise RuntimeError(f"HTTP {exc.code} from {safe_url}: {safe_detail}") from exc
    except urllib.error.URLError as exc:
        safe_url = redact_url(url)
        reason = redact_secrets(str(exc.reason))
        raise RuntimeError(f"Request failed for {safe_url}: {reason}") from exc

    if not raw.strip():
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        safe_raw = redact_secrets(raw)
        raise RuntimeError(f"Provider returned invalid JSON: {safe_raw}") from exc
