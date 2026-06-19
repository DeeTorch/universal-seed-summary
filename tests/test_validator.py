from pathlib import Path

from uss_engine.validator import validate_file, validate_text, parse_fields

ROOT = Path(__file__).resolve().parents[1]


def test_checkpoint_fixture_is_valid():
    report = validate_file(ROOT / "examples" / "checkpoint_valid.md")
    assert report.valid, report.model_dump()
    assert report.issue_count == 0


def test_archive_fixture_is_valid():
    report = validate_file(ROOT / "examples" / "archive_valid.md")
    assert report.valid, report.model_dump()
    assert report.issue_count == 0


def test_missing_failure_semantics_is_invalid():
    report = validate_file(ROOT / "examples" / "invalid_missing_failure_semantics.md")
    assert not report.valid
    assert any(issue.code == "missing_section" for issue in report.issues)


def test_archive_requires_execution_artifacts():
    text = (ROOT / "examples" / "checkpoint_valid.md").read_text(encoding="utf-8")
    text = text.replace("mode: checkpoint", "mode: archive")
    report = validate_text(text)
    assert not report.valid
    assert any("EXECUTION ARTIFACTS" in issue.message for issue in report.issues)


def test_field_parser_captures_multiline_values():
    body = """**A**: one\n- two\n- three\n**B**: four"""
    fields = parse_fields(body)
    assert fields["A"] == "one\n- two\n- three"
    assert fields["B"] == "four"
