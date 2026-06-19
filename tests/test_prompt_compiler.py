from pathlib import Path

from uss_engine.prompt_compiler import compile_repair_prompt, compile_runtime_prompt, load_protocol
from uss_engine.schema import InvocationMode, ValidationIssue, ValidationReport
from uss_engine.transcript import load_thread

ROOT = Path(__file__).resolve().parents[1]


def test_compile_runtime_prompt_contains_mode_and_transcript():
    protocol = load_protocol(ROOT / "protocols" / "uss_v1_3.protocol.json")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    prompt = compile_runtime_prompt(protocol=protocol, thread=thread, mode=InvocationMode.checkpoint)

    assert prompt.mode == InvocationMode.checkpoint
    assert "Invocation Mode: checkpoint" in prompt.user_prompt
    assert "thread_minimal_001" in prompt.user_prompt
    assert "Build USS Engine" in prompt.user_prompt or "USS Engine" in prompt.user_prompt
    assert prompt.as_messages()[0]["role"] == "system"
    assert prompt.as_messages()[1]["role"] == "user"


def test_archive_prompt_requires_execution_artifacts():
    protocol = load_protocol(ROOT / "protocols" / "uss_v1_3.protocol.json")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    prompt = compile_runtime_prompt(protocol=protocol, thread=thread, mode="archive")
    assert "EXECUTION ARTIFACTS (Archive Mode Only)" in prompt.user_prompt


def test_repair_prompt_embeds_validation_issues():
    protocol = load_protocol(ROOT / "protocols" / "uss_v1_3.protocol.json")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    prompt = compile_runtime_prompt(protocol=protocol, thread=thread, mode="checkpoint")
    report = ValidationReport.from_issues(
        issues=[ValidationIssue(code="missing_section", message="Missing required section")],
        mode=InvocationMode.checkpoint,
        protocol_version="1.3",
    )
    repair = compile_repair_prompt(
        previous_output="bad output",
        validation_report=report,
        runtime_prompt=prompt,
    )
    assert repair.metadata["repair"] is True
    assert "missing_section" in repair.user_prompt
    assert "bad output" in repair.user_prompt
