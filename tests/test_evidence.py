from pathlib import Path

from uss_engine.evidence import (
    EvidenceStatus,
    build_evidence_map,
    build_evidence_map_from_files,
    extract_claims,
    validate_evidence_map,
)
from uss_engine.transcript import load_thread

ROOT = Path(__file__).resolve().parents[1]


def test_extract_claims_from_summary_fields():
    text = (ROOT / "examples" / "summary_with_evidence.md").read_text(encoding="utf-8")
    claims = extract_claims(text)
    assert claims
    assert any(claim.field == "Architecture_Commits" for claim in claims)


def test_build_evidence_map_resolves_explicit_message_refs():
    summary = (ROOT / "examples" / "summary_with_evidence.md").read_text(encoding="utf-8")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    evidence_map = build_evidence_map(summary_text=summary, thread=thread)
    assert evidence_map.thread_id == "thread_minimal_001"
    assert evidence_map.coverage.claim_count > 0
    assert evidence_map.coverage.supported_count > 0
    assert evidence_map.coverage.anchor_count > 0
    assert any(claim.status == EvidenceStatus.supported for claim in evidence_map.claims)


def test_validate_evidence_map_detects_missing_refs():
    summary = (ROOT / "examples" / "summary_with_evidence.md").read_text(encoding="utf-8")
    summary = summary.replace("msg_001", "msg_999")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    evidence_map = build_evidence_map(summary_text=summary, thread=thread)
    report = validate_evidence_map(evidence_map, thread)
    assert not report.valid
    assert "msg_999" in report.missing_message_refs


def test_build_evidence_map_from_files():
    evidence_map = build_evidence_map_from_files(
        summary_path=ROOT / "examples" / "summary_with_evidence.md",
        thread_path=ROOT / "examples" / "thread_minimal.json",
    )
    assert evidence_map.coverage.weighted_support_ratio > 0.5

def test_metadata_and_protocol_fields_are_not_unsupported():
    summary = """---
mode: checkpoint
protocol_version: '1.3'
timestamp: '2026-06-19T00:00:00Z'
---

### HEADER (THREAD LOCK & AUDIT)

**Thread_Archetype**: Development_Forge
**Ignition_Vector**: The objective is to transform USS into a local-first tool. [evidence: msg_001]
**Focus_Domains**: Protocol_Design + Tool_Development + Local_First_Architecture + AI_Engineering
**Thread_Depth**: 2
**Completion_State**: Development (25-75%)
**Momentum_Indicator**: Accelerating
**Finalization_Beacon**: 2026-06-19T00:00:00Z
**Invoker**: User, Assistant

### FAILURE SEMANTICS & INTEGRITY FLAGS

**Incoherence_Flags**: None detected within thread bounds.
**Compression_Loss_Warnings**: No significant compression loss identified.
**Inference_Boundary_Alerts**: No inference boundary approached.
**Resolution_Impossibility_Markers**:
- External provider behavior requires live testing.
**Failure_Severity**: Low

### INVOCATION LOCK

This checkpoint is complete and locked.
"""
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    evidence_map = build_evidence_map(summary_text=summary, thread=thread)
    by_field = {claim.field: claim for claim in evidence_map.claims}

    assert by_field["Focus_Domains"].status == EvidenceStatus.derived_metadata
    assert by_field["Invoker"].status == EvidenceStatus.system_metadata
    assert by_field["Failure_Severity"].status == EvidenceStatus.protocol_assessment
    assert by_field["Incoherence_Flags"].status == EvidenceStatus.protocol_null_declaration
    assert not any(
        claim.status == EvidenceStatus.unsupported
        for claim in evidence_map.claims
        if claim.field in {"Focus_Domains", "Invoker", "Failure_Severity"}
    )

