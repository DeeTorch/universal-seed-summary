"""Pydantic models for USS Engine v0.1.

These models define the validation spine for Universal Seed Summary artifacts.
The Markdown validator in `validator.py` performs structural parsing, then emits
machine-readable reports using these models.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InvocationMode(StrEnum):
    """Supported USS v1.3 invocation modes."""

    checkpoint = "checkpoint"
    re_entry = "re_entry"
    archive = "archive"


class ThreadArchetype(StrEnum):
    """Canonical thread archetypes from USS v1.3, plus Other for future tolerance."""

    Development_Forge = "Development_Forge"
    Inquiry_Audit = "Inquiry_Audit"
    Conceptual_Synthesis = "Conceptual_Synthesis"
    Adversarial_Design = "Adversarial_Design"
    Implementation_Debug = "Implementation_Debug"
    Exploratory_Research = "Exploratory_Research"
    Other = "Other"


class CompletionState(StrEnum):
    Exploratory = "Exploratory"
    Development = "Development"
    Stabilizing = "Stabilizing"
    Complete = "Complete"


class MomentumIndicator(StrEnum):
    Accelerating = "Accelerating"
    Steady = "Steady"
    Stalled = "Stalled"
    Pivoting = "Pivoting"
    Concluding = "Concluding"


class FailureSeverity(StrEnum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class ConfidenceLevel(StrEnum):
    explicit = "explicit"
    inferred_within_thread = "inferred_within_thread"
    absent = "absent"
    uncertain = "uncertain"


class EvidenceAnchor(BaseModel):
    """Optional future evidence anchor for thread-derived claims."""

    message_id: str | None = None
    speaker: str | None = None
    timestamp: str | None = None
    confidence: ConfidenceLevel = ConfidenceLevel.uncertain
    excerpt: str | None = None


class FrontMatter(BaseModel):
    """YAML front matter expected at the top of USS Markdown artifacts."""

    model_config = ConfigDict(extra="allow")

    mode: InvocationMode
    protocol: str = Field(default="Universal Seed Summary Invoker")
    protocol_version: str = Field(default="1.3")
    timestamp: str
    source_thread_id: str | None = None
    tool_version: str | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_iso_utc(cls, value: str) -> str:
        _validate_iso_utc(value, field_name="timestamp")
        return value


class HeaderSection(BaseModel):
    Thread_Archetype: str
    Ignition_Vector: str
    Focus_Domains: str
    Thread_Depth: str
    Completion_State: str
    Momentum_Indicator: str
    Finalization_Beacon: str
    Invoker: str

    @field_validator("Finalization_Beacon")
    @classmethod
    def finalization_beacon_must_be_iso_utc(cls, value: str) -> str:
        _validate_iso_utc(value, field_name="Finalization_Beacon")
        return value


class FailureSemanticsSection(BaseModel):
    Incoherence_Flags: str
    Compression_Loss_Warnings: str
    Inference_Boundary_Alerts: str
    Resolution_Impossibility_Markers: str
    Failure_Severity: str


class CosmicCoreSection(BaseModel):
    Ontological_Constructs: str
    Paradigm_Nodes: str
    Emergent_Universals: str


class DecisionsGraftsSection(BaseModel):
    Architecture_Commits: str
    Heuristic_Branches: str
    Epistemic_Locks: str


class OpenVectorsSection(BaseModel):
    Unresolved_Queries: str
    Priority_Vectors: str
    Risk_Surfaces: str


class ThreadTopologySection(BaseModel):
    Parent_Threads: str | None = None
    Child_Threads: str | None = None
    Sibling_Threads: str | None = None
    Cross_Project_Links: str | None = None


class ExecutionArtifactsSection(BaseModel):
    Generated_Outputs: str
    Tool_Usage_Patterns: str
    Reusability_Index: str
    Integration_Notes: str


class USSSummaryArtifact(BaseModel):
    """Structured representation of a USS Markdown artifact."""

    frontmatter: FrontMatter
    header: HeaderSection
    failure_semantics: FailureSemanticsSection
    cosmic_core: CosmicCoreSection
    decisions_grafts: DecisionsGraftsSection
    open_vectors: OpenVectorsSection
    invocation_lock: str
    thread_topology: ThreadTopologySection | None = None
    execution_artifacts: ExecutionArtifactsSection | None = None

    @model_validator(mode="after")
    def archive_requires_execution_artifacts(self) -> "USSSummaryArtifact":
        if self.frontmatter.mode == InvocationMode.archive and self.execution_artifacts is None:
            raise ValueError("archive mode requires execution_artifacts")
        return self


class ValidationIssueSeverity(StrEnum):
    info = "info"
    warning = "warning"
    error = "error"


class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: ValidationIssueSeverity = ValidationIssueSeverity.error
    section: str | None = None
    field: str | None = None


class ValidationReport(BaseModel):
    valid: bool
    mode: InvocationMode | None = None
    protocol_version: str | None = None
    artifact_path: str | None = None
    issue_count: int = 0
    issues: list[ValidationIssue] = Field(default_factory=list)

    @classmethod
    def from_issues(
        cls,
        *,
        issues: list[ValidationIssue],
        mode: InvocationMode | None = None,
        protocol_version: str | None = None,
        artifact_path: str | None = None,
    ) -> "ValidationReport":
        return cls(
            valid=not any(issue.severity == ValidationIssueSeverity.error for issue in issues),
            mode=mode,
            protocol_version=protocol_version,
            artifact_path=artifact_path,
            issue_count=len(issues),
            issues=issues,
        )


def _validate_iso_utc(value: str, *, field_name: str) -> None:
    """Validate strict ISO-8601 UTC timestamps ending in Z."""

    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field_name} must be ISO-8601 UTC and end with 'Z'")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO-8601 timestamp") from exc


# Section contract derived from USS v1.3.
REQUIRED_SECTIONS: dict[str, list[str]] = {
    "HEADER (THREAD LOCK & AUDIT)": [
        "Thread_Archetype",
        "Ignition_Vector",
        "Focus_Domains",
        "Thread_Depth",
        "Completion_State",
        "Momentum_Indicator",
        "Finalization_Beacon",
        "Invoker",
    ],
    "FAILURE SEMANTICS & INTEGRITY FLAGS": [
        "Incoherence_Flags",
        "Compression_Loss_Warnings",
        "Inference_Boundary_Alerts",
        "Resolution_Impossibility_Markers",
        "Failure_Severity",
    ],
    "COSMIC CORE & EMERGENCE": [
        "Ontological_Constructs",
        "Paradigm_Nodes",
        "Emergent_Universals",
    ],
    "DECISIONS & GRAFTS": [
        "Architecture_Commits",
        "Heuristic_Branches",
        "Epistemic_Locks",
    ],
    "OPEN VECTORS & THRUST": [
        "Unresolved_Queries",
        "Priority_Vectors",
        "Risk_Surfaces",
    ],
    "INVOCATION LOCK": [],
}

ARCHIVE_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "EXECUTION ARTIFACTS (Archive Mode Only)": [
        "Generated_Outputs",
        "Tool_Usage_Patterns",
        "Reusability_Index",
        "Integration_Notes",
    ]
}

OPTIONAL_SECTIONS: dict[str, list[str]] = {
    "THREAD TOPOLOGY (Optional)": [
        "Parent_Threads",
        "Child_Threads",
        "Sibling_Threads",
        "Cross_Project_Links",
    ]
}

FAILURE_NULL_EXACT_STRINGS: dict[str, str] = {
    "Incoherence_Flags": "None detected within thread bounds.",
    "Compression_Loss_Warnings": "No significant compression loss identified.",
    "Inference_Boundary_Alerts": "No inference boundary approached.",
}

VAGUE_NULLS = {"", "n/a", "na", "none", "null", "not applicable", "unknown", "tbd"}
