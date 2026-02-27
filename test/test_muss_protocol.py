#!/usr/bin/env python3
# test_muss_protocol.py — MUSS v1.0 Protocol Structural Test Suite
# Tests: XML integrity, layer presence, command registry, schema sections,
#        model profiles, lifecycle engine, critical fields, validation gate.
# Usage: python tools/test_muss_protocol.py
# Run from repo root directory.

import sys
import re
from pathlib import Path

PROTOCOL_PATH = Path("protocols/MUSS_v1.0_protocol.xml")

REQUIRED_LAYERS = [
    "live_governance", "artifact_schema", "lifecycle_engine",
    "validation_gate", "model_profiles", "toolchain", "quickstart",
]

REQUIRED_COMMANDS = [
    "/muss start", "/muss status", "/muss refresh", "/muss reseed",
    "/muss seed", "/muss archive", "/muss resurrect", "/muss log",
    "/muss notebook", "/muss compile", "/muss show reasoning", "/muss integrity",
]

REQUIRED_SECTIONS = [
    "HEADER", "LIVE MEMORY SNAPSHOT", "FAILURE SEMANTICS", "COSMIC CORE",
    "DECISIONS", "OPEN VECTORS", "INVOCATION LOCK",
    "THREAD TOPOLOGY", "EXECUTION ARTIFACTS",
]

REQUIRED_MODELS = ["claude", "chatgpt", "grok", "gemini", "perplexity"]

REQUIRED_CONSTRAINTS = [
    "NEVER invent", "NEVER output XML tags", "NEVER omit",
    "NEVER summarize with vague", "NEVER narrate",
    "NEVER allow context drift", "NEVER introduce external knowledge",
    "NEVER skip the SAFEGUARD_CHECK",
]

LIFECYCLE_TRANSITIONS = ["ACTIVE.*SEED", "ACTIVE.*ARCHIVE", "RESURRECT"]

YAML_FIELDS = ["mode", "protocol", "protocol_version", "timestamp",
               "session_id", "exchange_count", "drift_risk", "invoker"]

PASSED = []
WARNINGS = []
ERRORS = []


def check(label, condition, critical=True):
    if condition:
        PASSED.append(label)
    elif critical:
        ERRORS.append(label)
    else:
        WARNINGS.append(label)


def run_tests():
    if not PROTOCOL_PATH.exists():
        print(f"\nFATAL: Protocol file not found at {PROTOCOL_PATH}")
        print("  Ensure you are running from the repo root directory.")
        print("  Expected: protocols/MUSS_v1.0_protocol.xml\n")
        sys.exit(1)

    content = PROTOCOL_PATH.read_text(encoding="utf-8")

    # T1 FILE INTEGRITY
    check("T1.1  File is non-empty (>1000 chars)", len(content) > 1000)
    check("T1.2  Root <MUSS_PROTOCOL> tag present",
          bool(re.search(r"<MUSS_PROTOCOL", content)))
    check("T1.3  Protocol id: Memory-Augmented-Universal-Seed-System",
          "Memory-Augmented-Universal-Seed-System" in content)
    check("T1.4  Version 1.0 declared", 'version="1.0"' in content)
    check("T1.5  Author: Jusstin DeRemus declared", "Jusstin DeRemus" in content)
    check("T1.6  Closing </MUSS_PROTOCOL> tag present",
          bool(re.search(r"</MUSS_PROTOCOL>", content)))

    # T2 LAYER PRESENCE
    for layer in REQUIRED_LAYERS:
        check(f"T2    Layer present: <{layer}>",
              bool(re.search(rf"<{layer}>", content)))

    # T3 NEGATIVE CONSTRAINTS
    for constraint in REQUIRED_CONSTRAINTS:
        check(f"T3    Constraint: '{constraint[:45]}'", constraint in content)

    # T4 COMMAND REGISTRY
    for cmd in REQUIRED_COMMANDS:
        check(f"T4    Command registered: {cmd}", cmd in content)

    # T5 ARTIFACT SCHEMA SECTIONS
    for section in REQUIRED_SECTIONS:
        check(f"T5    Schema section defined: {section}", section in content)

    # T6 YAML FRONTMATTER FIELDS
    for field in YAML_FIELDS:
        check(f"T6    YAML field specified: {field}", field in content)

    # T7 MODEL PROFILES
    for model in REQUIRED_MODELS:
        check(f"T7    Model profile present: <{model}>",
              bool(re.search(rf"<{model}>", content)))

    # T8 LIFECYCLE TRANSITIONS
    for transition in LIFECYCLE_TRANSITIONS:
        check(f"T8    Lifecycle transition: {transition}",
              bool(re.search(transition, content, re.IGNORECASE)))

    # T9 CRITICAL FIELDS
    check("T9.1  Compression_Fidelity_Score defined",
          "Compression_Fidelity_Score" in content)
    check("T9.2  Resurrection_Hook MUSS format: '> MUSS INGESTION:'",
          "MUSS INGESTION:" in content)
    check("T9.3  SESSION_LOG_DIGEST defined", "SESSION_LOG_DIGEST" in content)
    check("T9.4  NOTEBOOK_STATE defined", "NOTEBOOK_STATE" in content)
    check("T9.5  DRIFT_FLAG format defined", "DRIFT_FLAG" in content)
    check("T9.6  safeguard_check block defined", "safeguard_check" in content)
    check("T9.7  Drift thresholds LOW/MEDIUM/HIGH all present",
          all(t in content for t in ["LOW", "MEDIUM", "HIGH"]))
    check("T9.8  Token budgets defined (800 and 5000)",
          "800" in content and "5000" in content)
    check("T9.9  Toolchain files referenced (muss_validator, indexer, converter)",
          all(f in content for f in ["muss_validator.py", "indexer.py", "converter.py"]))
    check("T9.10 Obsidian Wikilink format referenced", "Wikilink" in content)
    check("T9.11 Quickstart steps 1 and 6 present",
          "STEP 1" in content and "STEP 6" in content)

    # T10 VALIDATION GATE
    check("T10.1 <validation_gate> block present", "<validation_gate>" in content)
    check("T10.2 Fidelity score range 0.00-1.00 specified",
          "0.00" in content and "1.00" in content)
    check("T10.3 No XML in output constraint present",
          "No XML tags present in output" in content)

    # REPORT
    total = len(PASSED) + len(WARNINGS) + len(ERRORS)
    print()
    print("=" * 65)
    print("  MUSS v1.0 — PROTOCOL STRUCTURAL TEST SUITE")
    print(f"  File  : {PROTOCOL_PATH}")
    print(f"  Total : {total} tests | Passed: {len(PASSED)} | "
          f"Warn: {len(WARNINGS)} | Errors: {len(ERRORS)}")
    print("=" * 65)

    if PASSED:
        print(f"\n  PASSED ({len(PASSED)})")
        for p in PASSED:
            print(f"    [OK] {p}")

    if WARNINGS:
        print(f"\n  WARNINGS ({len(WARNINGS)})")
        for w in WARNINGS:
            print(f"    [!!] {w}")

    if ERRORS:
        print(f"\n  FAILED ({len(ERRORS)})")
        for e in ERRORS:
            print(f"    [XX] {e}")
        print("\n  STATUS: PROTOCOL INTEGRITY CHECK FAILED")
        print("=" * 65 + "\n")
        sys.exit(1)
    else:
        pct = round((len(PASSED) / total) * 100)
        print(f"\n  STATUS: ALL TESTS PASSED ({pct}% integrity score)")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    run_tests()
