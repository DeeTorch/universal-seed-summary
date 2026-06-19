import json
from pathlib import Path

from typer.testing import CliRunner

from uss_engine.cli import app
from uss_engine.reports import ProviderKind, RunStatus
from uss_engine.run import RunConfig, render_static_uss_summary, run_uss_pipeline
from uss_engine.schema import InvocationMode
from uss_engine.transcript import load_thread
from uss_engine.validator import validate_text

ROOT = Path(__file__).resolve().parents[1]


def test_static_summary_candidate_is_valid():
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    text = render_static_uss_summary(thread=thread, mode=InvocationMode.checkpoint)
    report = validate_text(text)
    assert report.valid, [issue.model_dump() for issue in report.issues]


def test_e2e_static_run_writes_all_expected_artifacts(tmp_path):
    result = run_uss_pipeline(
        thread_path=ROOT / "examples" / "thread_minimal.json",
        protocol_path=ROOT / "protocols" / "uss_v1_3.protocol.json",
        output_dir=tmp_path,
        config=RunConfig(provider=ProviderKind.static, mode=InvocationMode.checkpoint),
    )

    assert result.report.status in {RunStatus.completed, RunStatus.completed_with_warnings}
    assert result.report.valid is True
    expected = [
        "summary.md",
        "validation_report.json",
        "redaction_report.json",
        "evidence_map.json",
        "inspection_report.json",
        "generation_report.json",
    ]
    for name in expected:
        assert (tmp_path / name).exists(), name

    generation_report = json.loads((tmp_path / "generation_report.json").read_text())
    assert generation_report["provider"] == "static"
    assert generation_report["mode"] == "checkpoint"
    assert generation_report["valid"] is True
    assert generation_report["output_paths"]["summary_md"].endswith("summary.md")


def test_run_cli_static(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            str(ROOT / "examples" / "thread_minimal.json"),
            "--protocol",
            str(ROOT / "protocols" / "uss_v1_3.protocol.json"),
            "--provider",
            "static",
            "--mode",
            "checkpoint",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "summary.md").exists()
    assert (tmp_path / "generation_report.json").exists()
