"""Artifact scoring for USS Engine v0.4."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .evidence import EvidenceMap, EvidenceValidationReport
from .schema import ValidationIssueSeverity, ValidationReport


class ScoreComponent(BaseModel):
    name: str
    weight: float = Field(ge=0.0, le=1.0)
    raw_score: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)
    notes: list[str] = Field(default_factory=list)


class ArtifactScore(BaseModel):
    total_score: float = Field(ge=0.0, le=100.0)
    grade: str
    mvp_ready: bool
    components: list[ScoreComponent]
    recommendations: list[str] = Field(default_factory=list)


def score_artifact(
    *,
    validation_report: ValidationReport,
    evidence_map: EvidenceMap | None = None,
    evidence_validation: EvidenceValidationReport | None = None,
) -> ArtifactScore:
    """Compute a pragmatic 0-100 inspection score.

    The score is not a truth score. It answers: "Is this artifact structurally
    valid, inspectable, and sufficiently anchored to the supplied thread?"
    """

    components: list[ScoreComponent] = []
    recommendations: list[str] = []

    structure_raw = 1.0 if validation_report.valid else max(0.0, 1.0 - _error_count(validation_report) * 0.18)
    if not validation_report.valid:
        recommendations.append("Fix structural validation errors before trusting or archiving this artifact.")
    components.append(_component("structure_validation", 0.40, structure_raw, _issue_notes(validation_report)))

    if evidence_map is None:
        evidence_raw = 0.0
        recommendations.append("Build an evidence map with the source thread to measure thread-derived support.")
        evidence_notes = ["No evidence map supplied."]
    else:
        evidence_raw = evidence_map.coverage.weighted_support_ratio
        evidence_notes = [
            f"claims={evidence_map.coverage.claim_count}",
            f"supported={evidence_map.coverage.supported_count}",
            f"weak={evidence_map.coverage.weakly_supported_count}",
            f"unsupported={evidence_map.coverage.unsupported_count}",
        ]
        if evidence_map.coverage.unsupported_count:
            recommendations.append("Review unsupported claims and either anchor them, weaken them, or declare absence.")
    components.append(_component("evidence_coverage", 0.35, evidence_raw, evidence_notes))

    if evidence_validation is None:
        integrity_raw = 0.0 if evidence_map is not None else 0.5
        integrity_notes = ["No evidence validation report supplied."]
    else:
        integrity_raw = 1.0 if evidence_validation.valid else max(0.0, 1.0 - evidence_validation.issue_count * 0.25)
        integrity_notes = evidence_validation.issues or ["All evidence references resolve to source-thread messages."]
        if not evidence_validation.valid:
            recommendations.append("Remove or correct evidence references that do not exist in the normalized thread.")
    components.append(_component("anchor_integrity", 0.15, integrity_raw, integrity_notes))

    risk_raw = 1.0
    risk_notes: list[str] = []
    warning_count = sum(1 for issue in validation_report.issues if issue.severity == ValidationIssueSeverity.warning)
    if warning_count:
        risk_raw -= min(0.4, warning_count * 0.1)
        risk_notes.append(f"validation_warnings={warning_count}")
    if evidence_map and evidence_map.coverage.unsupported_count:
        ratio = evidence_map.coverage.unsupported_count / max(evidence_map.coverage.claim_count, 1)
        risk_raw -= min(0.5, ratio)
        risk_notes.append(f"unsupported_claim_ratio={ratio:.2f}")
    risk_raw = max(0.0, risk_raw)
    components.append(_component("risk_surface", 0.10, risk_raw, risk_notes or ["No major risk penalties detected."]))

    total = round(sum(component.weighted_score for component in components) * 100, 2)
    grade = _grade(total)
    mvp_ready = validation_report.valid and total >= 85.0
    if not mvp_ready:
        recommendations.append("Treat artifact as draft/inspectable, not final MVP-grade archive output.")

    return ArtifactScore(
        total_score=total,
        grade=grade,
        mvp_ready=mvp_ready,
        components=components,
        recommendations=_dedupe(recommendations),
    )


def _component(name: str, weight: float, raw_score: float, notes: list[str]) -> ScoreComponent:
    raw = min(1.0, max(0.0, raw_score))
    return ScoreComponent(
        name=name,
        weight=weight,
        raw_score=round(raw, 4),
        weighted_score=round(raw * weight, 4),
        notes=notes,
    )


def _error_count(report: ValidationReport) -> int:
    return sum(1 for issue in report.issues if issue.severity == ValidationIssueSeverity.error)


def _issue_notes(report: ValidationReport) -> list[str]:
    if report.valid:
        return ["USS structural validator passed."]
    return [f"{issue.code}: {issue.message}" for issue in report.issues[:8]]


def _grade(score: float) -> str:
    if score >= 95:
        return "A"
    if score >= 85:
        return "B"
    if score >= 75:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output
