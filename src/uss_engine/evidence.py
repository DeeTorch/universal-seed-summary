"""Evidence anchoring for USS Engine v0.4.

This module turns the USS protocol rule "thread-derived only" into a measurable
artifact: every parsed summary claim can be connected to message IDs from the
normalized source thread, marked as supported/weak/unsupported, and scored.

The anchoring logic is intentionally deterministic and local-first. It does not
claim semantic proof; it creates a reproducible baseline that can later be
augmented by a stronger retrieval model or LLM judge.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .schema import InvocationMode
from .transcript import NormalizedThread, TranscriptMessage, load_thread
from .validator import parse_fields, parse_frontmatter, parse_sections

EVIDENCE_REF_RE = re.compile(
    r"(?:\[evidence\s*:\s*(?P<bracket>[^\]]+)\]|Evidence\s*:\s*(?P<plain>[^\n]+))",
    re.IGNORECASE,
)
MESSAGE_ID_RE = re.compile(r"\b(?:msg|message|m)_[A-Za-z0-9_.:-]+\b|\bmsg\d{1,6}\b")
WORD_RE = re.compile(r"[A-Za-z0-9_]{3,}")
BULLET_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)(?P<text>.+?)\s*$")


DERIVED_METADATA_FIELDS = {
    "Thread_Archetype",
    "Focus_Domains",
    "Completion_State",
    "Momentum_Indicator",
}

SYSTEM_METADATA_FIELDS = {
    "Thread_Depth",
    "Finalization_Beacon",
    "Invoker",
}

PROTOCOL_ASSESSMENT_FIELDS = {
    "Failure_Severity",
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "must", "will",
    "should", "would", "could", "there", "their", "thread", "summary", "output",
    "field", "section", "mode", "none", "detected", "within", "bounds", "no",
    "significant", "identified", "required", "explicit", "absence", "using", "only",
    "protocol", "artifact", "current", "invocation", "complete", "locked",
}


class EvidenceStatus(StrEnum):
    """Support status for a generated claim."""

    supported = "supported"
    weakly_supported = "weakly_supported"
    unsupported = "unsupported"
    absent_claim = "absent_claim"
    derived_metadata = "derived_metadata"
    system_metadata = "system_metadata"
    protocol_null_declaration = "protocol_null_declaration"
    protocol_assessment = "protocol_assessment"


class EvidenceConfidence(StrEnum):
    """Confidence level attached to an evidence claim."""

    explicit_reference = "explicit_reference"
    lexical_match = "lexical_match"
    weak_lexical_match = "weak_lexical_match"
    absent = "absent"
    unsupported = "unsupported"
    derived_metadata = "derived_metadata"
    system_metadata = "system_metadata"
    protocol_null_declaration = "protocol_null_declaration"
    protocol_assessment = "protocol_assessment"


class EvidenceAnchor(BaseModel):
    """A single source-thread anchor supporting a USS claim."""

    model_config = ConfigDict(extra="forbid")

    message_id: str
    role: str
    source_index: int | None = None
    timestamp: str | None = None
    excerpt: str = ""
    match_score: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence: EvidenceConfidence = EvidenceConfidence.unsupported


class EvidenceClaim(BaseModel):
    """One parsed claim extracted from a USS summary field."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str
    section: str
    field: str
    claim_text: str
    status: EvidenceStatus = EvidenceStatus.unsupported
    confidence: EvidenceConfidence = EvidenceConfidence.unsupported
    anchors: list[EvidenceAnchor] = Field(default_factory=list)
    explicit_message_refs: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @field_validator("claim_text")
    @classmethod
    def claim_text_must_not_be_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("claim_text cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def align_status_with_anchors(self) -> "EvidenceClaim":
        if self.status == EvidenceStatus.supported and not self.anchors:
            raise ValueError("supported evidence claims must include at least one anchor")
        return self


class EvidenceCoverage(BaseModel):
    """Aggregate evidence coverage metrics."""

    claim_count: int = 0
    supported_count: int = 0
    weakly_supported_count: int = 0
    unsupported_count: int = 0
    absent_claim_count: int = 0
    derived_metadata_count: int = 0
    system_metadata_count: int = 0
    protocol_null_declaration_count: int = 0
    protocol_assessment_count: int = 0
    explicit_ref_count: int = 0
    anchor_count: int = 0
    coverage_ratio: float = Field(ge=0.0, le=1.0, default=0.0)
    weighted_support_ratio: float = Field(ge=0.0, le=1.0, default=0.0)


class EvidenceMap(BaseModel):
    """Machine-readable map from USS claims to source-thread messages."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    thread_id: str
    mode: InvocationMode | None = None
    protocol_version: str | None = None
    generated_at: str
    claims: list[EvidenceClaim] = Field(default_factory=list)
    coverage: EvidenceCoverage = Field(default_factory=EvidenceCoverage)
    warnings: list[str] = Field(default_factory=list)


class EvidenceValidationReport(BaseModel):
    """Validation report for an evidence map."""

    valid: bool
    issue_count: int = 0
    issues: list[str] = Field(default_factory=list)
    missing_message_refs: list[str] = Field(default_factory=list)
    unsupported_claim_ids: list[str] = Field(default_factory=list)


def build_evidence_map(
    *,
    summary_text: str,
    thread: NormalizedThread,
    artifact_id: str | None = None,
    max_claims_per_field: int = 5,
) -> EvidenceMap:
    """Build an evidence map for a USS Markdown artifact against a normalized thread."""

    frontmatter: dict[str, Any] = {}
    body = summary_text
    try:
        frontmatter, body = parse_frontmatter(summary_text)
    except ValueError:
        # Evidence building can still run on malformed summaries so the inspector
        # can return a complete diagnostic bundle.
        body = summary_text

    mode = _resolve_mode(frontmatter.get("mode"))
    protocol_version = str(frontmatter.get("protocol_version") or frontmatter.get("version") or "") or None
    artifact_key = artifact_id or _artifact_id(summary_text)
    claims = extract_claims(summary_text, max_claims_per_field=max_claims_per_field)

    anchored_claims = [anchor_claim(claim, thread) for claim in claims]
    coverage = calculate_coverage(anchored_claims)
    warnings: list[str] = []
    if not anchored_claims:
        warnings.append("No evidence claims were extracted from the artifact.")
    if coverage.unsupported_count:
        warnings.append(f"{coverage.unsupported_count} claim(s) are unsupported by deterministic anchoring.")

    return EvidenceMap(
        artifact_id=artifact_key,
        thread_id=thread.thread_id,
        mode=mode,
        protocol_version=protocol_version,
        generated_at=_now_utc(),
        claims=anchored_claims,
        coverage=coverage,
        warnings=warnings,
    )


def build_evidence_map_from_files(
    *,
    summary_path: str | Path,
    thread_path: str | Path,
    max_claims_per_field: int = 5,
) -> EvidenceMap:
    """Load files and build an evidence map."""

    summary = Path(summary_path).read_text(encoding="utf-8")
    thread = load_thread(thread_path)
    return build_evidence_map(
        summary_text=summary,
        thread=thread,
        artifact_id=str(Path(summary_path)),
        max_claims_per_field=max_claims_per_field,
    )


def extract_claims(summary_text: str, *, max_claims_per_field: int = 5) -> list[EvidenceClaim]:
    """Extract evidence-checkable claims from USS field values.

    The validator already checks required fields. This function converts each
    meaningful field value into one or more claim units while skipping pure null
    declarations and the dedicated optional evidence section if present.
    """

    try:
        _, body = parse_frontmatter(summary_text)
    except ValueError:
        body = summary_text

    sections = parse_sections(body)
    claims: list[EvidenceClaim] = []
    for section_title, section_body in sections.items():
        if section_title.upper().startswith("EVIDENCE MAP"):
            continue
        if section_title == "INVOCATION LOCK":
            claim_texts = _split_claim_text(section_body, max_items=1)
            for idx, claim_text in enumerate(claim_texts):
                claims.append(_make_claim(section_title, "Invocation_Lock", claim_text, idx))
            continue
        fields = parse_fields(section_body)
        for field_name, value in fields.items():
            if _is_structural_or_null(value):
                claim_texts = [value.strip()]
            else:
                claim_texts = _split_claim_text(value, max_items=max_claims_per_field)
            for idx, claim_text in enumerate(claim_texts):
                claims.append(_make_claim(section_title, field_name, claim_text, idx))
    return claims


def anchor_claim(claim: EvidenceClaim, thread: NormalizedThread) -> EvidenceClaim:
    """Attach best-effort thread anchors to one extracted claim."""

    explicit_refs = _extract_explicit_refs(claim.claim_text)
    classification = _classified_status_for_claim(claim)
    if classification is not None:
        status, confidence, note = classification
        return claim.model_copy(
            update={
                "status": status,
                "confidence": confidence,
                "explicit_message_refs": explicit_refs,
                "notes": [note],
            }
        )
    valid_ref_anchors: list[EvidenceAnchor] = []
    message_by_id = {message.id: message for message in thread.messages}

    for ref in explicit_refs:
        message = message_by_id.get(ref)
        if message is not None:
            valid_ref_anchors.append(_anchor_from_message(message, score=1.0, confidence=EvidenceConfidence.explicit_reference))

    if valid_ref_anchors:
        return claim.model_copy(
            update={
                "status": EvidenceStatus.supported,
                "confidence": EvidenceConfidence.explicit_reference,
                "anchors": valid_ref_anchors,
                "explicit_message_refs": explicit_refs,
                "notes": _missing_ref_notes(explicit_refs, message_by_id),
            }
        )

    if _is_absence_or_null_claim(claim.claim_text):
        return claim.model_copy(
            update={
                "status": EvidenceStatus.protocol_null_declaration,
                "confidence": EvidenceConfidence.protocol_null_declaration,
                "explicit_message_refs": explicit_refs,
                "notes": [
                    *_missing_ref_notes(explicit_refs, message_by_id),
                    "Protocol-required null declaration; excluded from unsupported evidence penalties.",
                ],
            }
        )

    scored = sorted(
        ((_lexical_support_score(claim.claim_text, message.content), message) for message in thread.messages),
        key=lambda item: item[0],
        reverse=True,
    )
    best_score, best_message = scored[0] if scored else (0.0, None)

    if best_message is None or best_score < 0.18:
        return claim.model_copy(
            update={
                "status": EvidenceStatus.unsupported,
                "confidence": EvidenceConfidence.unsupported,
                "explicit_message_refs": explicit_refs,
                "notes": [*_missing_ref_notes(explicit_refs, message_by_id), "No source message crossed lexical support threshold."],
            }
        )

    if best_score >= 0.34:
        status = EvidenceStatus.supported
        confidence = EvidenceConfidence.lexical_match
    else:
        status = EvidenceStatus.weakly_supported
        confidence = EvidenceConfidence.weak_lexical_match

    anchors = [_anchor_from_message(best_message, score=best_score, confidence=confidence)]
    return claim.model_copy(
        update={
            "status": status,
            "confidence": confidence,
            "anchors": anchors,
            "explicit_message_refs": explicit_refs,
            "notes": _missing_ref_notes(explicit_refs, message_by_id),
        }
    )


def validate_evidence_map(evidence_map: EvidenceMap, thread: NormalizedThread) -> EvidenceValidationReport:
    """Validate references inside an evidence map against a normalized thread."""

    valid_message_ids = {message.id for message in thread.messages}
    issues: list[str] = []
    missing_refs: list[str] = []
    unsupported_claim_ids: list[str] = []

    if evidence_map.thread_id != thread.thread_id:
        issues.append(f"Evidence map thread_id {evidence_map.thread_id!r} does not match source thread {thread.thread_id!r}.")

    for claim in evidence_map.claims:
        if claim.status == EvidenceStatus.unsupported:
            unsupported_claim_ids.append(claim.claim_id)
        for ref in claim.explicit_message_refs:
            if ref not in valid_message_ids:
                missing_refs.append(ref)
        for anchor in claim.anchors:
            if anchor.message_id not in valid_message_ids:
                missing_refs.append(anchor.message_id)

    missing_refs = sorted(set(missing_refs))
    if missing_refs:
        issues.append(f"Evidence map references missing source messages: {', '.join(missing_refs)}")

    return EvidenceValidationReport(
        valid=not issues,
        issue_count=len(issues),
        issues=issues,
        missing_message_refs=missing_refs,
        unsupported_claim_ids=unsupported_claim_ids,
    )


def calculate_coverage(claims: list[EvidenceClaim]) -> EvidenceCoverage:
    """Calculate aggregate support metrics for evidence claims."""

    claim_count = len(claims)
    supported = sum(1 for claim in claims if claim.status == EvidenceStatus.supported)
    weak = sum(1 for claim in claims if claim.status == EvidenceStatus.weakly_supported)
    unsupported = sum(1 for claim in claims if claim.status == EvidenceStatus.unsupported)
    absent = sum(1 for claim in claims if claim.status == EvidenceStatus.absent_claim)
    derived_metadata = sum(1 for claim in claims if claim.status == EvidenceStatus.derived_metadata)
    system_metadata = sum(1 for claim in claims if claim.status == EvidenceStatus.system_metadata)
    protocol_null = sum(1 for claim in claims if claim.status == EvidenceStatus.protocol_null_declaration)
    protocol_assessment = sum(1 for claim in claims if claim.status == EvidenceStatus.protocol_assessment)
    non_penalized = derived_metadata + system_metadata + protocol_null + protocol_assessment
    explicit_refs = sum(len(claim.explicit_message_refs) for claim in claims)
    anchors = sum(len(claim.anchors) for claim in claims)
    if claim_count == 0:
        coverage_ratio = 0.0
        weighted = 0.0
    else:
        coverage_ratio = (supported + weak + absent + non_penalized) / claim_count
        weighted = (supported + 0.5 * weak + 0.75 * absent + non_penalized) / claim_count
    return EvidenceCoverage(
        claim_count=claim_count,
        supported_count=supported,
        weakly_supported_count=weak,
        unsupported_count=unsupported,
        absent_claim_count=absent,
        derived_metadata_count=derived_metadata,
        system_metadata_count=system_metadata,
        protocol_null_declaration_count=protocol_null,
        protocol_assessment_count=protocol_assessment,
        explicit_ref_count=explicit_refs,
        anchor_count=anchors,
        coverage_ratio=round(coverage_ratio, 4),
        weighted_support_ratio=round(weighted, 4),
    )


def _classified_status_for_claim(claim: EvidenceClaim) -> tuple[EvidenceStatus, EvidenceConfidence, str] | None:
    """Classify claims that do not require direct lexical anchoring.

    USS artifacts include fields that are derived from the whole thread, system
    metadata, protocol null declarations, or protocol-level assessments. Treating
    those as ordinary factual claims creates false unsupported-evidence penalties.
    """

    if _is_absence_or_null_claim(claim.claim_text):
        return (
            EvidenceStatus.protocol_null_declaration,
            EvidenceConfidence.protocol_null_declaration,
            "Protocol-required null declaration; excluded from unsupported evidence penalties.",
        )

    if claim.field in DERIVED_METADATA_FIELDS:
        return (
            EvidenceStatus.derived_metadata,
            EvidenceConfidence.derived_metadata,
            "Derived metadata field; evaluated as whole-thread classification, not direct lexical evidence.",
        )

    if claim.field in SYSTEM_METADATA_FIELDS:
        return (
            EvidenceStatus.system_metadata,
            EvidenceConfidence.system_metadata,
            "System metadata field; derived from transcript/runtime metadata rather than message body text.",
        )

    if claim.field in PROTOCOL_ASSESSMENT_FIELDS:
        return (
            EvidenceStatus.protocol_assessment,
            EvidenceConfidence.protocol_assessment,
            "Protocol assessment field; evaluated from failure semantics rather than direct lexical evidence.",
        )

    return None


def _make_claim(section: str, field: str, claim_text: str, index: int) -> EvidenceClaim:
    seed = f"{section}|{field}|{index}|{claim_text}".encode("utf-8")
    claim_id = "claim_" + hashlib.sha1(seed).hexdigest()[:12]
    return EvidenceClaim(claim_id=claim_id, section=section, field=field, claim_text=claim_text.strip())


def _split_claim_text(value: str, *, max_items: int) -> list[str]:
    # Field parsers can include Markdown section separators as continuation
    # lines. They are formatting, not claims.
    clean = "\n".join(line for line in value.strip().splitlines() if line.strip() != "---").strip()
    if not clean:
        return []

    # Keep inline evidence hints attached to the claim they support. Splitting
    # evidence-bearing sentences can create one unsupported claim plus one
    # evidence-only claim, which makes deterministic coverage noisier.
    if EVIDENCE_REF_RE.search(clean) and not any(BULLET_RE.match(line) for line in clean.splitlines()):
        return [clean]

    bullets: list[str] = []
    continuation: list[str] = []
    for line in clean.splitlines():
        match = BULLET_RE.match(line)
        if match:
            if continuation and not bullets:
                bullets.append(" ".join(continuation).strip())
                continuation = []
            bullets.append(match.group("text").strip())
        elif line.strip():
            continuation.append(line.strip())
    if bullets:
        return [item for item in bullets if item][:max_items]

    sentence_parts = re.split(r"(?<=[.!?])\s+", " ".join(continuation or [clean]))
    sentence_parts = [part.strip() for part in sentence_parts if part.strip()]
    if len(sentence_parts) > 1:
        return sentence_parts[:max_items]
    return [clean]


def _strip_evidence_annotations(value: str) -> str:
    return EVIDENCE_REF_RE.sub("", value)


def _extract_explicit_refs(text: str) -> list[str]:
    refs: list[str] = []
    for evidence_match in EVIDENCE_REF_RE.finditer(text):
        raw = evidence_match.group("bracket") or evidence_match.group("plain") or ""
        refs.extend(MESSAGE_ID_RE.findall(raw))
    refs.extend(MESSAGE_ID_RE.findall(text))
    return sorted(set(refs))


def _missing_ref_notes(refs: list[str], message_by_id: dict[str, TranscriptMessage]) -> list[str]:
    missing = [ref for ref in refs if ref not in message_by_id]
    return [f"Explicit evidence reference not found in thread: {ref}" for ref in missing]


def _anchor_from_message(
    message: TranscriptMessage,
    *,
    score: float,
    confidence: EvidenceConfidence,
) -> EvidenceAnchor:
    return EvidenceAnchor(
        message_id=message.id,
        role=message.role.value,
        source_index=message.source_index,
        timestamp=message.timestamp,
        excerpt=_excerpt(message.content),
        match_score=round(score, 4),
        confidence=confidence,
    )


def _lexical_support_score(claim_text: str, message_text: str) -> float:
    claim_tokens = _tokens(claim_text)
    message_tokens = _tokens(message_text)
    if not claim_tokens or not message_tokens:
        return 0.0
    claim_counter = Counter(claim_tokens)
    message_counter = Counter(message_tokens)
    overlap = sum(min(count, message_counter[token]) for token, count in claim_counter.items())
    token_ratio = overlap / max(sum(claim_counter.values()), 1)

    phrase_bonus = 0.0
    claim_clean = " ".join(claim_tokens)
    message_clean = " ".join(message_tokens)
    if len(claim_clean) >= 24 and claim_clean in message_clean:
        phrase_bonus = 0.25

    return min(1.0, token_ratio + phrase_bonus)


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text) if token.lower() not in STOPWORDS]


def _excerpt(content: str, *, max_chars: int = 240) -> str:
    clean = " ".join(content.strip().split())
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "…"


def _is_absence_or_null_claim(value: str) -> bool:
    clean = value.strip().lower()
    return (
        clean.startswith("none detected")
        or clean.startswith("no significant")
        or clean.startswith("no inference")
        or "explicitly declare absence" in clean
        or "absent" in clean
    )


def _is_structural_or_null(value: str) -> bool:
    clean = value.strip()
    return bool(clean) and _is_absence_or_null_claim(clean)


def _resolve_mode(value: Any) -> InvocationMode | None:
    if value is None:
        return None
    try:
        return InvocationMode(str(value))
    except ValueError:
        return None


def _artifact_id(text: str) -> str:
    return "artifact_" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
