#!/usr/bin/env python3
"""
muss_validator.py -- MUSS v1.0 Artifact Validator
Extends USS validator.py with MUSS-specific field checks.
Usage: python muss_validator.py <artifact.md>
"""

import re
import sys
from pathlib import Path

# -- REQUIRED YAML FRONTMATTER FIELDS ----------------------------------------
YAML_FIELDS = [
    "mode",
    "protocol",
    "protocol_version",
    "timestamp",
    "session_id",
    "exchange_count",
    "drift_risk",
    "invoker",
]

# -- REQUIRED SECTIONS BY MODE ----------------------------------------------
SECTIONS_ALWAYS = [
    "HEADER",
    "LIVE MEMORY SNAPSHOT",
    "FAILURE SEMANTICS",
    "COSMIC CORE",
    "DECISIONS",
    "OPEN VECTORS",
    "INVOCATION LOCK",
]

SECTIONS_ARCHIVE_ONLY = [
    "EXECUTION ARTIFACTS",
]

SECTIONS_CONDITIONAL = [
    "THREAD TOPOLOGY",  # only if cross-thread links exist - not enforced
]

# -- FIELD PATTERN VALIDATORS -----------------------------------------------
PATTERNS = {
    "Compression_Fidelity_Score": re.compile(
        r"\*\*Compression_Fidelity_Score\*\*:\s*(0\.\d{1,2}|1\.00?)", re.MULTILINE
    ),
    "Resurrection_Hook": re.compile(
        r"> MUSS INGESTION:", re.MULTILINE
    ),
    "SESSION_LOG_DIGEST": re.compile(
        r"\*\*SESSION_LOG_DIGEST\*\*", re.MULTILINE
    ),
    "NOTEBOOK_STATE": re.compile(
        r"\*\*NOTEBOOK_STATE\*\*", re.MULTILINE
    ),
    "Failure_Severity": re.compile(
        r"\*\*Failure_Severity\*\*:\s*(Low|Medium|High)", re.MULTILINE
    ),
    "Drift_Event_Log": re.compile(
        r"\*\*Drift_Event_Log\*\*", re.MULTILINE
    ),
    "Momentum_Indicator": re.compile(
        r"\*\*Momentum_Indicator\*\*:\s*(Active|Concluding|Stalled|Pivoting)",
        re.MULTILINE,
    ),
}

YAML_PATTERN = re.compile(
    r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE
)

# -- VALIDATOR -------------------------------------------------------------

def validate(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        print(f"[MUSS VALIDATOR] ERROR: File not found -- {filepath}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    errors = []
    warnings = []
    passed = []

    # 1. YAML FRONTMATTER
    yaml_block_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL | re.MULTILINE)
    if not yaml_block_match:
        errors.append("YAML frontmatter block not found (expected --- ... ---)")
    else:
        yaml_block = yaml_block_match.group(1)
        for field in YAML_FIELDS:
            if re.search(rf"^{field}:", yaml_block, re.MULTILINE):
                passed.append(f"YAML field present: {field}")
            else:
                errors.append(f"YAML field missing: {field}")

    # 2. REQUIRED SECTIONS
    for section in SECTIONS_ALWAYS:
        if re.search(rf"###.*{re.escape(section)}", content, re.IGNORECASE):
            passed.append(f"Section found: {section}")
        else:
            errors.append(f"Required section missing: ### {section}")

    # Detect mode for archive-only sections
    mode_match = re.search(r"^mode:\s*(.+)", content, re.MULTILINE)
    if mode_match:
        mode = mode_match.group(1).strip().strip('"')
        if mode == "archive":
            for section in SECTIONS_ARCHIVE_ONLY:
                if re.search(rf"###.*{re.escape(section)}", content, re.IGNORECASE):
                    passed.append(f"Archive section found: {section}")
                else:
                    errors.append(f"Archive-mode section missing: ### {section}")

    # 3. FIELD PATTERN CHECKS
    for field_name, pattern in PATTERNS.items():
        if pattern.search(content):
            passed.append(f"Field valid: {field_name}")
        else:
            if field_name in ("Compression_Fidelity_Score", "Resurrection_Hook",
                               "SESSION_LOG_DIGEST", "NOTEBOOK_STATE"):
                errors.append(f"Required field missing or malformed: {field_name}")
            else:
                warnings.append(f"Field may be missing or malformed: {field_name}")

    # 4. NO XML TAGS IN OUTPUT
    xml_tags = re.findall(r"<[A-Za-z_][A-Za-z0-9_]*[^>]*>", content)
    if xml_tags:
        warnings.append(f"XML tags detected in artifact (should be Markdown only): {xml_tags[:5]}")
    else:
        passed.append("No XML tags in artifact output")

    # 5. PROTOCOL VERSION CHECK
    version_pattern = r'protocol_version:\s*["\']?1\.0["\']?'
    if re.search(version_pattern, content):
        passed.append("Protocol version: MUSS v1.0 confirmed")
    else:
        warnings.append("Protocol version not confirmed as MUSS v1.0 -- check frontmatter")

    # -- REPORT -------------------------------------------------------------
    print("\n" + "="*60)
    print("  MUSS v1.0 VALIDATOR -- REPORT")
    print("  File:", filepath)
    print("="*60)

    if passed:
        print(f"\n  + PASSED ({len(passed)})")
        for p in passed:
            print(f"    + {p}")

    if warnings:
        print(f"\n  ! WARNINGS ({len(warnings)})")
        for w in warnings:
            print(f"    ! {w}")

    if errors:
        print(f"\n  X ERRORS ({len(errors)})")
        for e in errors:
            print(f"    X {e}")
        print("\n  STATUS: VALIDATION FAILED")
        print("="*60 + "\n")
        sys.exit(1)
    else:
        print("\n  STATUS: VALIDATION PASSED")
        print("="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python muss_validator.py <artifact.md>")
        sys.exit(1)
    validate(sys.argv[1])
