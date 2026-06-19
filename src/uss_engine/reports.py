"""Report models and writers for USS Engine end-to-end runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .inspector import ArtifactInspection
from .redactor import RedactionReport
from .schema import InvocationMode, ValidationReport


class ProviderKind(StrEnum):
    """Supported execution providers for the run command."""

    static = "static"
    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"
    grok = "grok"
    xai = "xai"
    ollama = "ollama"


class RunStatus(StrEnum):
    """Terminal status for a full USS run."""

    completed = "completed"
    completed_with_warnings = "completed_with_warnings"
    failed_validation = "failed_validation"
    failed_generation = "failed_generation"


class ReportArtifactPaths(BaseModel):
    """Canonical output paths produced by `uss run`."""

    model_config = ConfigDict(extra="forbid")

    output_dir: str
    summary_md: str
    validation_report_json: str
    redaction_report_json: str
    evidence_map_json: str
    inspection_report_json: str
    generation_report_json: str


class GenerationAttemptSummary(BaseModel):
    """Sanitized generation attempt metadata for durable reports.

    Raw prompts are intentionally excluded so generation reports remain safe to
    archive even when input threads contain sensitive material.
    """

    attempt_number: int
    valid: bool
    issue_count: int
    prompt_metadata: dict[str, Any] = Field(default_factory=dict)
    output_char_count: int = 0
    output_preview: str = ""


class GenerationRunReport(BaseModel):
    """Machine-readable run report for one complete USS Engine execution."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: RunStatus
    mode: InvocationMode
    provider: ProviderKind
    model: str | None = None
    started_at: str
    finished_at: str
    duration_ms: int
    input_thread_path: str
    protocol_path: str
    output_paths: ReportArtifactPaths
    valid: bool
    mvp_ready: bool
    validation_issue_count: int
    redaction_hit_count: int
    evidence_claim_count: int | None = None
    evidence_weighted_support_ratio: float | None = None
    inspection_score: float | None = None
    inspection_grade: str | None = None
    attempts: list[GenerationAttemptSummary] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @field_validator("started_at", "finished_at")
    @classmethod
    def timestamp_must_be_iso_utc(cls, value: str) -> str:
        if not value.endswith("Z"):
            raise ValueError("timestamp must be UTC and end with Z")
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


def build_attempt_summaries(attempts: list[Any]) -> list[GenerationAttemptSummary]:
    """Convert generator attempts into safe report summaries."""

    summaries: list[GenerationAttemptSummary] = []
    for attempt in attempts:
        output = getattr(attempt, "output", "") or ""
        report = getattr(attempt, "validation_report", None)
        prompt_metadata = getattr(attempt, "prompt_metadata", {}) or {}
        summaries.append(
            GenerationAttemptSummary(
                attempt_number=int(getattr(attempt, "attempt_number", len(summaries) + 1)),
                valid=bool(getattr(report, "valid", False)) if report is not None else False,
                issue_count=int(getattr(report, "issue_count", 0)) if report is not None else 0,
                prompt_metadata=prompt_metadata,
                output_char_count=len(output),
                output_preview=_preview(output),
            )
        )
    return summaries


def build_run_report(
    *,
    run_id: str,
    status: RunStatus,
    mode: InvocationMode,
    provider: ProviderKind,
    model: str | None,
    started_at: str,
    finished_at: str,
    duration_ms: int,
    input_thread_path: str,
    protocol_path: str,
    output_paths: ReportArtifactPaths,
    validation_report: ValidationReport,
    redaction_report: RedactionReport,
    inspection: ArtifactInspection | None,
    attempts: list[Any],
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
) -> GenerationRunReport:
    """Assemble the top-level generation run report."""

    evidence_map = inspection.evidence_map if inspection is not None else None
    score = inspection.score if inspection is not None else None
    return GenerationRunReport(
        run_id=run_id,
        status=status,
        mode=mode,
        provider=provider,
        model=model,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        input_thread_path=input_thread_path,
        protocol_path=protocol_path,
        output_paths=output_paths,
        valid=validation_report.valid,
        mvp_ready=bool(score.mvp_ready) if score is not None else False,
        validation_issue_count=validation_report.issue_count,
        redaction_hit_count=redaction_report.hit_count,
        evidence_claim_count=evidence_map.coverage.claim_count if evidence_map is not None else None,
        evidence_weighted_support_ratio=(
            evidence_map.coverage.weighted_support_ratio if evidence_map is not None else None
        ),
        inspection_score=score.total_score if score is not None else None,
        inspection_grade=score.grade if score is not None else None,
        attempts=build_attempt_summaries(attempts),
        warnings=warnings or [],
        errors=errors or [],
    )


def write_json_report(payload: BaseModel | dict[str, Any], path: str | Path) -> None:
    """Write a Pydantic model or dict as pretty JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, BaseModel):
        data = payload.model_dump(mode="json")
    else:
        data = payload
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now_utc() -> str:
    """UTC timestamp helper shared by run/report code."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _preview(text: str, *, max_chars: int = 500) -> str:
    clean = " ".join(text.strip().split())
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "…"
