"""Redaction layer for USS Engine v0.3.

USS summaries are designed to become durable continuity artifacts. This module
removes or masks common secrets before prompt compilation so sensitive values do
not get sent to LLM providers or preserved in generated summaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Pattern

from pydantic import BaseModel, Field

from .transcript import NormalizedThread, TranscriptMessage


class RedactionCategory(StrEnum):
    email = "email"
    phone = "phone"
    openai_api_key = "openai_api_key"
    anthropic_api_key = "anthropic_api_key"
    github_token = "github_token"
    aws_access_key = "aws_access_key"
    bearer_token = "bearer_token"
    url_credentials = "url_credentials"
    private_key_block = "private_key_block"
    generic_secret_assignment = "generic_secret_assignment"


class RedactionMode(StrEnum):
    mask = "mask"
    placeholder = "placeholder"


@dataclass(frozen=True, slots=True)
class RedactionRule:
    category: RedactionCategory
    pattern: Pattern[str]
    replacement: str
    description: str


class RedactionHit(BaseModel):
    category: RedactionCategory
    message_id: str
    role: str
    source_index: int | None = None
    start: int
    end: int
    placeholder: str


class RedactionReport(BaseModel):
    redacted: bool
    hit_count: int = 0
    hits: list[RedactionHit] = Field(default_factory=list)
    categories: dict[str, int] = Field(default_factory=dict)

    @classmethod
    def from_hits(cls, hits: list[RedactionHit]) -> "RedactionReport":
        categories: dict[str, int] = {}
        for hit in hits:
            categories[hit.category.value] = categories.get(hit.category.value, 0) + 1
        return cls(redacted=bool(hits), hit_count=len(hits), hits=hits, categories=categories)


class RedactionResult(BaseModel):
    thread: NormalizedThread
    report: RedactionReport


@dataclass(slots=True)
class RedactionConfig:
    enabled: bool = True
    mode: RedactionMode = RedactionMode.placeholder
    redact_emails: bool = True
    redact_phone_numbers: bool = True
    redact_secret_assignments: bool = True
    custom_rules: list[RedactionRule] | None = None


DEFAULT_RULES: list[RedactionRule] = [
    RedactionRule(
        category=RedactionCategory.private_key_block,
        pattern=re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.MULTILINE,
        ),
        replacement="[REDACTED_PRIVATE_KEY_BLOCK]",
        description="PEM private key block",
    ),
    RedactionRule(
        category=RedactionCategory.openai_api_key,
        pattern=re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
        replacement="[REDACTED_OPENAI_API_KEY]",
        description="OpenAI-style API key",
    ),
    RedactionRule(
        category=RedactionCategory.anthropic_api_key,
        pattern=re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
        replacement="[REDACTED_ANTHROPIC_API_KEY]",
        description="Anthropic-style API key",
    ),
    RedactionRule(
        category=RedactionCategory.github_token,
        pattern=re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
        replacement="[REDACTED_GITHUB_TOKEN]",
        description="GitHub token",
    ),
    RedactionRule(
        category=RedactionCategory.aws_access_key,
        pattern=re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
        replacement="[REDACTED_AWS_ACCESS_KEY]",
        description="AWS access key ID",
    ),
    RedactionRule(
        category=RedactionCategory.bearer_token,
        pattern=re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
        replacement="Bearer [REDACTED_BEARER_TOKEN]",
        description="Bearer token",
    ),
    RedactionRule(
        category=RedactionCategory.url_credentials,
        pattern=re.compile(r"\b([a-z][a-z0-9+.-]*://)([^\s/@:]+):([^\s/@]+)@", re.IGNORECASE),
        replacement=r"\1[REDACTED_USER]:[REDACTED_PASSWORD]@",
        description="URL embedded username/password",
    ),
    RedactionRule(
        category=RedactionCategory.email,
        pattern=re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        replacement="[REDACTED_EMAIL]",
        description="Email address",
    ),
    RedactionRule(
        category=RedactionCategory.phone,
        pattern=re.compile(r"(?<!\w)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\w)"),
        replacement="[REDACTED_PHONE]",
        description="US phone number",
    ),
    RedactionRule(
        category=RedactionCategory.generic_secret_assignment,
        pattern=re.compile(
            r"(?i)\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*([\"']?)[^\s\"']{12,}\2"
        ),
        replacement=r"\1=[REDACTED_SECRET]",
        description="Generic secret assignment",
    ),
]


def redact_thread(thread: NormalizedThread, config: RedactionConfig | None = None) -> RedactionResult:
    """Return a redacted copy of a normalized thread plus a redaction report."""

    cfg = config or RedactionConfig()
    if not cfg.enabled:
        return RedactionResult(thread=thread, report=RedactionReport.from_hits([]))

    rules = _select_rules(cfg)
    all_hits: list[RedactionHit] = []
    redacted_messages: list[TranscriptMessage] = []

    for message in thread.messages:
        redacted_content, hits = redact_text(
            message.content,
            message_id=message.id,
            role=message.role.value,
            source_index=message.source_index,
            rules=rules,
        )
        all_hits.extend(hits)
        redacted_messages.append(
            message.model_copy(
                update={
                    "content": redacted_content,
                    "metadata": {
                        **message.metadata,
                        "redacted": bool(hits),
                        "redaction_hit_count": len(hits),
                    },
                },
                deep=True,
            )
        )

    redacted_thread = thread.model_copy(
        update={
            "messages": redacted_messages,
            "metadata": {
                **thread.metadata,
                "redaction_applied": bool(all_hits),
                "redaction_hit_count": len(all_hits),
            },
        },
        deep=True,
    )
    return RedactionResult(thread=redacted_thread, report=RedactionReport.from_hits(all_hits))


def redact_text(
    text: str,
    *,
    message_id: str = "text",
    role: str = "unknown",
    source_index: int | None = None,
    rules: list[RedactionRule] | None = None,
) -> tuple[str, list[RedactionHit]]:
    """Redact one text block and return replacement hits."""

    active_rules = rules or DEFAULT_RULES
    output = text
    hits: list[RedactionHit] = []

    for rule in active_rules:
        current_hits: list[RedactionHit] = []

        def replace(match: re.Match[str]) -> str:
            placeholder = match.expand(rule.replacement)
            current_hits.append(
                RedactionHit(
                    category=rule.category,
                    message_id=message_id,
                    role=role,
                    source_index=source_index,
                    start=match.start(),
                    end=match.end(),
                    placeholder=placeholder,
                )
            )
            return placeholder

        output = rule.pattern.sub(replace, output)
        hits.extend(current_hits)

    return output, hits


def _select_rules(config: RedactionConfig) -> list[RedactionRule]:
    rules: list[RedactionRule] = []
    for rule in DEFAULT_RULES:
        if rule.category == RedactionCategory.email and not config.redact_emails:
            continue
        if rule.category == RedactionCategory.phone and not config.redact_phone_numbers:
            continue
        if (
            rule.category == RedactionCategory.generic_secret_assignment
            and not config.redact_secret_assignments
        ):
            continue
        rules.append(rule)
    if config.custom_rules:
        rules.extend(config.custom_rules)
    return rules
