from pathlib import Path

import pytest

from uss_engine.transcript import (
    NormalizedThread,
    TranscriptRole,
    load_thread,
    normalize_transcript_json,
    normalize_transcript_text,
)

ROOT = Path(__file__).resolve().parents[1]


def test_normalize_minimal_json_fixture():
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    assert isinstance(thread, NormalizedThread)
    assert thread.thread_id == "thread_minimal_001"
    assert len(thread.messages) == 3
    assert thread.messages[0].role == TranscriptRole.user
    assert thread.exchange_pair_count == 1


def test_normalize_role_prefixed_text():
    raw = """User: Build USS Engine.\nAssistant: Start with validation.\nUser: Add transcript normalization."""
    thread = normalize_transcript_text(raw, thread_id="raw-test")
    assert thread.thread_id == "raw-test"
    assert [message.role for message in thread.messages] == [
        TranscriptRole.user,
        TranscriptRole.assistant,
        TranscriptRole.user,
    ]
    assert thread.messages[1].content == "Start with validation."


def test_unprefixed_text_becomes_single_user_message():
    thread = normalize_transcript_text("Build the repo blueprint.")
    assert len(thread.messages) == 1
    assert thread.messages[0].role == TranscriptRole.user


def test_json_requires_messages():
    with pytest.raises(ValueError):
        normalize_transcript_json({"thread_id": "bad"})
