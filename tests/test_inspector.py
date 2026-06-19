from pathlib import Path

from uss_engine.inspector import inspect_files, inspect_text
from uss_engine.transcript import load_thread

ROOT = Path(__file__).resolve().parents[1]


def test_inspector_runs_without_thread():
    inspection = inspect_files(summary_path=ROOT / "examples" / "checkpoint_valid.md")
    assert inspection.validation_report.valid
    assert inspection.evidence_map is None
    assert inspection.score.total_score < 100


def test_inspector_scores_summary_with_evidence_and_thread():
    inspection = inspect_files(
        summary_path=ROOT / "examples" / "summary_with_evidence.md",
        thread_path=ROOT / "examples" / "thread_minimal.json",
    )
    assert inspection.validation_report.valid
    assert inspection.evidence_map is not None
    assert inspection.evidence_validation is not None
    assert inspection.evidence_validation.valid
    assert inspection.score.total_score >= 80


def test_inspect_text_accepts_thread_object():
    summary = (ROOT / "examples" / "summary_with_evidence.md").read_text(encoding="utf-8")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    inspection = inspect_text(summary_text=summary, thread=thread)
    assert inspection.summary["evidence_claims"] > 0
    assert "grade" in inspection.summary
