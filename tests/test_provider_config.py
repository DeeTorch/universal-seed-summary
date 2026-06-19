import os

from typer.testing import CliRunner

from uss_engine.cli import app
from uss_engine.config import load_env_file, provider_secret_status


def test_load_env_file_sets_keys_without_printing_values(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text('OPENAI_API_KEY="sk-test"\n# comment\nBAD LINE\n', encoding="utf-8")
    result = load_env_file(env_file)
    assert result.loaded_keys == ("OPENAI_API_KEY",)
    assert "BAD LINE" in result.skipped_keys
    assert os.environ["OPENAI_API_KEY"] == "sk-test"


def test_provider_secret_status_detects_gemini_alias(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "google-test")
    status = provider_secret_status("gemini")
    assert status.configured is True
    assert status.env_key == "GOOGLE_API_KEY"


def test_provider_status_cli_does_not_print_secret(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("XAI_API_KEY=xai-secret-value\n", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(app, ["provider-status", "--env-file", str(env_file)])
    assert result.exit_code == 0, result.output
    assert "grok" in result.output
    assert "xai-secret-value" not in result.output
