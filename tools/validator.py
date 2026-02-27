#!/usr/bin/env python3
"""
USS Protocol Compliance Validator
Version 1.4 (ingestion-pack aware)

Validates Universal Seed Summary Invoker output for protocol compliance.
Checks required sections, field presence, formatting standards, and token budgets,
including Compression_Fidelity_Score and Resurrection_Hook.
"""

import re
import sys
from pathlib import Path
from typing import List, NamedTuple
import argparse


class ValidationResult(NamedTuple):
    """Result of USS validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]


class USSValidator:
    """Validator for USS protocol compliance"""

    REQUIRED_SECTIONS = [
        "HEADER (THREAD LOCK & AUDIT)",
        "FAILURE SEMANTICS & INTEGRITY FLAGS",
        "COSMIC CORE & EMERGENCE",
        "DECISIONS & GRAFTS",
        "OPEN VECTORS & THRUST",
        "INVOCATION LOCK",
    ]

    HEADER_FIELDS = [
        "Thread_Archetype",
        "Ignition_Vector",
        "Focus_Domains",
        "Thread_Depth",
        "Completion_State",
        "Momentum_Indicator",
        "Finalization_Beacon",
        "Invoker",
    ]

    FAILURE_SEMANTICS_FIELDS = [
        "Incoherence_Flags",
        "Compression_Loss_Warnings",
        "Inference_Boundary_Alerts",
        "Resolution_Impossibility_Markers",
        "Failure_Severity",
        "Compression_Fidelity_Score",  # ingestion-pack extension
    ]

    TOKEN_BUDGETS = {
        "checkpoint": (800, 1200),
        "re_entry": (1500, 2500),
        "archive": (3000, 5000),
    }

    MIN_INVOCATION_LOCK_WORDS = 20  # Minimum words for 2-4 sentences

    def __init__(self, content: str, verbose: bool = False):
        self.content = content
        self.verbose = verbose
        self.mode = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        self._check_frontmatter()
        self._check_required_sections()
        self._check_header_fields()
        self._check_failure_semantics()
        self._check_formatting()
        self._check_token_budget()
        self._check_invocation_lock()

        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors, self.warnings, self.info)

    # -------------------------------------------------------------------------
    # Frontmatter
    # -------------------------------------------------------------------------
    def _check_frontmatter(self):
        """Check for YAML frontmatter"""
        if not self.content.startswith("---"):
            self.errors.append("Missing YAML frontmatter at start of document")
            return

        frontmatter_match = re.search(r"^---\n(.*?)\n---", self.content, re.DOTALL)
        if not frontmatter_match:
            self.errors.append("Malformed YAML frontmatter")
            return

        frontmatter = frontmatter_match.group(1)

        # Check required frontmatter fields
        if "mode:" not in frontmatter:
            self.errors.append("Missing 'mode' field in frontmatter")

        # Allow either protocol_version or version for backward compatibility
        if "protocol_version:" not in frontmatter and "version:" not in frontmatter:
            self.warnings.append(
                "Missing 'protocol_version' or 'version' field in frontmatter"
            )

        if "timestamp:" not in frontmatter:
            self.errors.append("Missing 'timestamp' field in frontmatter")

        # Extract mode for token budget checking
        mode_match = re.search(r"mode:\s*([^\s\n]+)", frontmatter)
        if mode_match:
            self.mode = mode_match.group(1)
            self.info.append(f"Detected mode: {self.mode}")
        else:
            self.mode = None

    # -------------------------------------------------------------------------
    # Sections
    # -------------------------------------------------------------------------
    def _check_required_sections(self):
        """Check all required sections are present"""
        for section in self.REQUIRED_SECTIONS:
            section_pattern = rf"### {re.escape(section)}"
            if not re.search(section_pattern, self.content):
                self.errors.append(f"Missing required section: {section}")
            else:
                if self.verbose:
                    self.info.append(f"Found section: {section}")

    def _check_header_fields(self):
        """Check HEADER section has all required fields"""
        header_pattern = r"### HEADER \(THREAD LOCK & AUDIT\).*?\n---"
        header_match = re.search(header_pattern, self.content, re.DOTALL)

        if not header_match:
            self.errors.append("Cannot parse HEADER section")
            return

        header_content = header_match.group(0)

        for field in self.HEADER_FIELDS:
            field_pattern = rf"\*\*{field}\*\*:"
            if not re.search(field_pattern, header_content):
                self.errors.append(f"Missing required HEADER field: {field}")
            else:
                if self.verbose:
                    self.info.append(f"Found HEADER field: {field}")

    def _check_failure_semantics(self):
        """Check FAILURE SEMANTICS section"""
        fs_pattern = r"### FAILURE SEMANTICS & INTEGRITY FLAGS.*?\n---"
        fs_match = re.search(fs_pattern, self.content, re.DOTALL)

        if not fs_match:
            self.errors.append("Cannot parse FAILURE SEMANTICS section")
            return

        fs_content = fs_match.group(0)

        # Check required fields exist
        for field in self.FAILURE_SEMANTICS_FIELDS:
            field_pattern = rf"\*\*{field}\*\*:"
            if not re.search(field_pattern, fs_content):
                self.errors.append(
                    f"Missing required FAILURE SEMANTICS field: {field}"
                )
            else:
                if self.verbose:
                    self.info.append(f"Found FAILURE SEMANTICS field: {field}")

        # Check for vague null declarations
        vague_patterns = [
            "may be",
            "possibly",
            "some nuance",
            "might have",
            "could be",
            "perhaps",
            "maybe",
        ]

        fs_content_lower = fs_content.lower()
        for pattern in vague_patterns:
            if pattern.lower() in fs_content_lower:
                self.warnings.append(
                    f"Potentially vague language in FAILURE SEMANTICS: '{pattern}'"
                )

        # Validate Compression_Fidelity_Score format: 0.00–1.00 or 'Unknown'
        fidelity_pattern = (
            r"\*\*Compression_Fidelity_Score\*\*:\s*(1\.00|0\.\d{1,2}|Unknown)"
        )
        if not re.search(fidelity_pattern, fs_content):
            self.errors.append(
                "FAILURE SEMANTICS: Compression_Fidelity_Score must be a float "
                "between 0.00 and 1.00, or 'Unknown'."
            )

    # -------------------------------------------------------------------------
    # Formatting
    # -------------------------------------------------------------------------
    def _check_formatting(self):
        """Check formatting standards compliance"""
        # Check section headers use ### (warn on # or ## for uppercase headings)
        invalid_headers = re.findall(r"^#{1,2}\s+[A-Z]", self.content, re.MULTILINE)
        if invalid_headers:
            self.warnings.append(
                f"Found {len(invalid_headers)} headers not using ### format"
            )

        # Check field format **Field_Name**:
        fields = re.findall(r"\*\*(\w+)\*\*:", self.content)
        if self.verbose:
            self.info.append(f"Found {len(fields)} formatted fields")

        # Check for section separators
        separators = re.findall(r"^---$", self.content, re.MULTILINE)
        if len(separators) < len(self.REQUIRED_SECTIONS):
            self.warnings.append(
                "Fewer section separators than required sections "
                "(expected at least one '---' between major sections)"
            )

    # -------------------------------------------------------------------------
    # Token budgets
    # -------------------------------------------------------------------------
    def _check_token_budget(self):
        """Check token count against mode budget"""
        if (
            not hasattr(self, "mode")
            or self.mode is None
            or self.mode not in self.TOKEN_BUDGETS
        ):
            self.warnings.append("Cannot validate token budget (unknown or unsupported mode)")
            return

        # Rough token estimate: words * 1.3
        words = len(self.content.split())
        estimated_tokens = int(words * 1.3)

        min_tokens, max_tokens = self.TOKEN_BUDGETS[self.mode]

        self.info.append(
            f"Estimated tokens: {estimated_tokens} (target: {min_tokens}-{max_tokens})"
        )

        if estimated_tokens < min_tokens:
            self.warnings.append(
                f"Token count below target ({estimated_tokens} < {min_tokens})"
            )
        elif estimated_tokens > max_tokens:
            self.warnings.append(
                f"Token count exceeds target ({estimated_tokens} > {max_tokens})"
            )
        else:
            self.info.append("Token count within budget")

    # -------------------------------------------------------------------------
    # Invocation lock
    # -------------------------------------------------------------------------
    def _check_invocation_lock(self):
        """Check INVOCATION LOCK section exists and is conclusive"""
        if "INVOCATION LOCK" not in self.content:
            self.errors.append("Missing INVOCATION LOCK section")
            return

        # Extract INVOCATION LOCK content (last section)
        lock_pattern = r"### INVOCATION LOCK\s*\n(.+?)(?=\n---|$)"
        lock_match = re.search(lock_pattern, self.content, re.DOTALL)

        if not lock_match:
            self.errors.append("Cannot parse INVOCATION LOCK content")
            return

        lock_content = lock_match.group(1).strip()

        # Check it's not too short
        if len(lock_content.split()) < self.MIN_INVOCATION_LOCK_WORDS:
            self.warnings.append(
                "INVOCATION LOCK seems too brief (should be 2-4 sentences)"
            )

        # Check for conclusive language
        conclusive_terms = ["complete", "locked", "sealed", "artifact", "ready"]
        if not any(term in lock_content.lower() for term in conclusive_terms):
            self.warnings.append(
                "INVOCATION LOCK lacks conclusive language (e.g., 'complete', 'locked', 'sealed', 'artifact', 'ready')"
            )

        # Validate Resurrection_Hook presence and format
        hook_pattern = r"\*\*Resurrection_Hook\*\*:\s*> INGESTION:.*"
        if not re.search(hook_pattern, lock_content):
            self.errors.append(
                "INVOCATION LOCK: Missing or improperly formatted Resurrection_Hook. "
                "Must begin with '> INGESTION:'."
            )


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Validate USS protocol compliance for conversation summaries"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to USS summary markdown file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed validation info",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )

    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    try:
        content = args.file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    validator = USSValidator(content, verbose=args.verbose)
    result = validator.validate()

    # Print results
    print(f"\nValidating: {args.file}")
    print("=" * 60)

    if result.errors:
        print(f"\n[ERROR] ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")

    if result.warnings:
        print(f"\n[WARNING] ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning}")

    if result.info and args.verbose:
        print(f"\n[INFO] ({len(result.info)}):")
        for item in result.info:
            print(f"  - {item}")

    print("\n" + "=" * 60)

    if args.strict and result.warnings:
        print("[FAIL] VALIDATION FAILED (strict mode: warnings treated as errors)")
        sys.exit(1)
    elif result.errors:
        print("[FAIL] VALIDATION FAILED")
        sys.exit(1)
    else:
        print("[PASS] VALIDATION PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
