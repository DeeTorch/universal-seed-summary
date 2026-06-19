"""Artifact inspector for USS Engine v0.4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .evidence import EvidenceMap, EvidenceValidationReport, build_evidence_map, validate_evidence_map
from .scoring import ArtifactScore, score_artifact
from .schema import ValidationReport
from .transcript import NormalizedThread, load_thread
from .validator import validate_text


class ArtifactInspection(BaseModel):
    """Full inspection bundle for a USS artifact."""

    artifact_path: str | None = None
    thread_path: str | None = None
    validation_report: ValidationReport
    evidence_map: EvidenceMap | None = None
    evidence_validation: EvidenceValidationReport | None = None
    score: ArtifactScore
    summary: dict[str, Any] = Field(default_factory=dict)

    @property
    def valid(self) -> bool:
        evidence_ok = self.evidence_validation.valid if self.evidence_validation is not None else True
        return self.validation_report.valid and evidence_ok


def inspect_text(
    *,
    summary_text: str,
    thread: NormalizedThread | None = None,
    artifact_path: str | None = None,
    thread_path: str | None = None,
) -> ArtifactInspection:
    """Inspect an artifact string, optionally with its source thread."""

    validation_report = validate_text(summary_text)
    validation_report.artifact_path = artifact_path

    evidence_map: EvidenceMap | None = None
    evidence_validation: EvidenceValidationReport | None = None
    if thread is not None:
        evidence_map = build_evidence_map(
            summary_text=summary_text,
            thread=thread,
            artifact_id=artifact_path,
        )
        evidence_validation = validate_evidence_map(evidence_map, thread)

    score = score_artifact(
        validation_report=validation_report,
        evidence_map=evidence_map,
        evidence_validation=evidence_validation,
    )

    summary = {
        "valid": validation_report.valid and (evidence_validation.valid if evidence_validation else True),
        "mode": validation_report.mode.value if validation_report.mode else None,
        "protocol_version": validation_report.protocol_version,
        "validation_issues": validation_report.issue_count,
        "score": score.total_score,
        "grade": score.grade,
        "mvp_ready": score.mvp_ready,
    }
    if evidence_map is not None:
        summary.update(
            {
                "evidence_claims": evidence_map.coverage.claim_count,
                "evidence_supported": evidence_map.coverage.supported_count,
                "evidence_weak": evidence_map.coverage.weakly_supported_count,
                "evidence_unsupported": evidence_map.coverage.unsupported_count,
                "evidence_weighted_support_ratio": evidence_map.coverage.weighted_support_ratio,
            }
        )

    return ArtifactInspection(
        artifact_path=artifact_path,
        thread_path=thread_path,
        validation_report=validation_report,
        evidence_map=evidence_map,
        evidence_validation=evidence_validation,
        score=score,
        summary=summary,
    )


def inspect_files(
    *,
    summary_path: str | Path,
    thread_path: str | Path | None = None,
) -> ArtifactInspection:
    """Inspect a USS artifact file, optionally with the source thread file."""

    summary_file = Path(summary_path)
    summary_text = summary_file.read_text(encoding="utf-8")
    thread = load_thread(thread_path) if thread_path is not None else None
    return inspect_text(
        summary_text=summary_text,
        thread=thread,
        artifact_path=str(summary_file),
        thread_path=str(thread_path) if thread_path is not None else None,
    )


def write_inspection_json(inspection: ArtifactInspection, path: str | Path) -> None:
    """Write an inspection report to JSON."""

    output_path = Path(path)
    output_path.write_text(
        json.dumps(inspection.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
