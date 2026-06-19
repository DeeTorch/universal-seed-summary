from pathlib import Path

from uss_engine.redactor import RedactionCategory, RedactionConfig, redact_text, redact_thread
from uss_engine.transcript import load_thread

ROOT = Path(__file__).resolve().parents[1]


def test_redact_text_masks_common_secrets():
    text = "Email oracle@example.com token=supersecretvalue12345 Bearer abcdefghijklmnopqrstuvwxyz123"
    redacted, hits = redact_text(text)
    assert "oracle@example.com" not in redacted
    assert "supersecretvalue12345" not in redacted
    assert "abcdefghijklmnopqrstuvwxyz123" not in redacted
    categories = {hit.category for hit in hits}
    assert RedactionCategory.email in categories
    assert RedactionCategory.generic_secret_assignment in categories
    assert RedactionCategory.bearer_token in categories


def test_redact_thread_returns_copy_and_report():
    thread = load_thread(ROOT / "examples" / "thread_with_secrets.json")
    result = redact_thread(thread)
    assert result.report.redacted
    assert result.report.hit_count >= 5
    joined = "\n".join(message.content for message in result.thread.messages)
    assert "oracle@example.com" not in joined
    assert "503-555-0199" not in joined
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in joined
    assert thread.messages[0].content != result.thread.messages[0].content


def test_redaction_can_keep_emails():
    thread = load_thread(ROOT / "examples" / "thread_with_secrets.json")
    result = redact_thread(thread, RedactionConfig(redact_emails=False))
    joined = "\n".join(message.content for message in result.thread.messages)
    assert "oracle@example.com" in joined
    assert "503-555-0199" not in joined
