"""Structural validator for USS Markdown artifacts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .schema import (
    ARCHIVE_REQUIRED_SECTIONS,
    FAILURE_NULL_EXACT_STRINGS,
    OPTIONAL_SECTIONS,
    REQUIRED_SECTIONS,
    VAGUE_NULLS,
    ExecutionArtifactsSection,
    FailureSemanticsSection,
    FrontMatter,
    HeaderSection,
    InvocationMode,
    ValidationIssue,
    ValidationIssueSeverity,
    ValidationReport,
)

SECTION_RE = re.compile(r"^###\s+(?P<title>.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\*\*(?P<key>[A-Za-z0-9_]+)\*\*:\s*(?P<value>.*)$")


def validate_file(path: str | Path) -> ValidationReport:
    artifact_path = Path(path)
    text = artifact_path.read_text(encoding="utf-8")
    report = validate_text(text)
    report.artifact_path = str(artifact_path)
    return report


def validate_text(text: str) -> ValidationReport:
    """Validate a USS Markdown artifact and return a report.

    The validator intentionally fails closed. Missing required information is an error.
    """

    issues: list[ValidationIssue] = []
    frontmatter_data: dict[str, Any] = {}
    mode: InvocationMode | None = None
    protocol_version: str | None = None

    try:
        frontmatter_data, body = parse_frontmatter(text)
        frontmatter = FrontMatter.model_validate(frontmatter_data)
        mode = frontmatter.mode
        protocol_version = frontmatter.protocol_version
    except ValueError as exc:
        body = text
        issues.append(ValidationIssue(code="frontmatter_error", message=str(exc)))
    except ValidationError as exc:
        body = text
        issues.extend(_issues_from_pydantic(exc, section="frontmatter"))

    sections = parse_sections(body)

    required_sections = dict(REQUIRED_SECTIONS)
    if mode == InvocationMode.archive:
        required_sections.update(ARCHIVE_REQUIRED_SECTIONS)

    for section_title, required_fields in required_sections.items():
        if section_title not in sections:
            issues.append(
                ValidationIssue(
                    code="missing_section",
                    message=f"Missing required section: {section_title}",
                    section=section_title,
                )
            )
            continue

        section_body = sections[section_title]
        if section_title == "INVOCATION LOCK":
            if not section_body.strip():
                issues.append(
                    ValidationIssue(
                        code="empty_invocation_lock",
                        message="Invocation Lock section must contain a conclusive paragraph.",
                        section=section_title,
                    )
                )
            continue

        fields = parse_fields(section_body)
        for field_name in required_fields:
            value = fields.get(field_name)
            if value is None:
                issues.append(
                    ValidationIssue(
                        code="missing_field",
                        message=f"{section_title} is missing required field: {field_name}",
                        section=section_title,
                        field=field_name,
                    )
                )
            elif is_vague_null(value):
                issues.append(
                    ValidationIssue(
                        code="vague_or_empty_field",
                        message=f"{section_title}.{field_name} has a vague or empty value.",
                        section=section_title,
                        field=field_name,
                    )
                )

        if section_title == "FAILURE SEMANTICS & INTEGRITY FLAGS":
            issues.extend(validate_failure_semantics(fields, section_title))

        if section_title == "HEADER (THREAD LOCK & AUDIT)" and not any(
            issue.section == section_title and issue.severity == ValidationIssueSeverity.error
            for issue in issues
        ):
            try:
                HeaderSection.model_validate(fields)
            except ValidationError as exc:
                issues.extend(_issues_from_pydantic(exc, section=section_title))

        if section_title == "EXECUTION ARTIFACTS (Archive Mode Only)" and not any(
            issue.section == section_title and issue.severity == ValidationIssueSeverity.error
            for issue in issues
        ):
            try:
                ExecutionArtifactsSection.model_validate(fields)
            except ValidationError as exc:
                issues.extend(_issues_from_pydantic(exc, section=section_title))

    # Optional section validation: if present, check required optional fields are not blank.
    for section_title, optional_fields in OPTIONAL_SECTIONS.items():
        if section_title in sections:
            fields = parse_fields(sections[section_title])
            for field_name in optional_fields:
                if field_name in fields and is_vague_null(fields[field_name]):
                    issues.append(
                        ValidationIssue(
                            code="vague_optional_field",
                            message=f"{section_title}.{field_name} is present but vague/empty.",
                            severity=ValidationIssueSeverity.warning,
                            section=section_title,
                            field=field_name,
                        )
                    )

    return ValidationReport.from_issues(
        issues=issues,
        mode=mode,
        protocol_version=protocol_version,
    )


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return YAML front matter and Markdown body."""

    if not text.startswith("---\n"):
        raise ValueError("Artifact must begin with YAML front matter delimited by ---")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("YAML front matter closing delimiter not found")
    raw_yaml = text[4:end]
    body = text[end + len("\n---\n") :]
    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML front matter must parse to an object")
    return data, body


def parse_sections(body: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(body))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        title = match.group("title").strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def parse_fields(section_body: str) -> dict[str, str]:
    """Parse USS field lines and attach continuation lines until next field."""

    fields: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in section_body.splitlines():
        field_match = FIELD_RE.match(line.strip())
        if field_match:
            current_key = field_match.group("key")
            fields[current_key] = [field_match.group("value").strip()]
        elif current_key is not None:
            fields[current_key].append(line.rstrip())

    return {key: "\n".join(value).strip() for key, value in fields.items()}


def validate_failure_semantics(fields: dict[str, str], section_title: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field_name, exact_null in FAILURE_NULL_EXACT_STRINGS.items():
        value = fields.get(field_name, "")
        if is_vague_null(value):
            issues.append(
                ValidationIssue(
                    code="invalid_failure_null",
                    message=(
                        f"{section_title}.{field_name} cannot use a vague null. "
                        f"Use exact null declaration if no issue exists: {exact_null!r}"
                    ),
                    section=section_title,
                    field=field_name,
                )
            )

    if "Failure_Severity" in fields:
        severity = fields["Failure_Severity"].strip().split()[0]
        if severity not in {"Low", "Medium", "High"}:
            issues.append(
                ValidationIssue(
                    code="invalid_failure_severity",
                    message="Failure_Severity must begin with Low, Medium, or High.",
                    section=section_title,
                    field="Failure_Severity",
                )
            )

    try:
        FailureSemanticsSection.model_validate(fields)
    except ValidationError as exc:
        issues.extend(_issues_from_pydantic(exc, section=section_title))

    return issues


def is_vague_null(value: str) -> bool:
    cleaned = value.strip().lower().strip(" .:-")
    return cleaned in VAGUE_NULLS


def _issues_from_pydantic(exc: ValidationError, *, section: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", [])) or None
        issues.append(
            ValidationIssue(
                code="schema_validation_error",
                message=error.get("msg", "Schema validation error"),
                section=section,
                field=loc,
            )
        )
    return issues
