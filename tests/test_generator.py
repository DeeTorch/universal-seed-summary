from pathlib import Path

from uss_engine.generator import GenerationConfig, StaticLLMClient, generate_summary
from uss_engine.prompt_compiler import load_protocol
from uss_engine.schema import InvocationMode
from uss_engine.transcript import load_thread

ROOT = Path(__file__).resolve().parents[1]


def test_generator_accepts_valid_static_output():
    protocol = load_protocol(ROOT / "protocols" / "uss_v1_3.protocol.json")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    valid_output = (ROOT / "examples" / "checkpoint_valid.md").read_text(encoding="utf-8")
    result = generate_summary(
        protocol=protocol,
        thread=thread,
        mode=InvocationMode.checkpoint,
        client=StaticLLMClient(outputs=[valid_output]),
    )
    assert result.valid
    assert len(result.attempts) == 1


def test_generator_retries_after_invalid_output():
    protocol = load_protocol(ROOT / "protocols" / "uss_v1_3.protocol.json")
    thread = load_thread(ROOT / "examples" / "thread_minimal.json")
    invalid_output = "not a valid USS artifact"
    valid_output = (ROOT / "examples" / "checkpoint_valid.md").read_text(encoding="utf-8")
    result = generate_summary(
        protocol=protocol,
        thread=thread,
        mode="checkpoint",
        client=StaticLLMClient(outputs=[invalid_output, valid_output]),
        config=GenerationConfig(max_attempts=2),
    )
    assert result.valid
    assert len(result.attempts) == 2
    assert not result.attempts[0].validation_report.valid
    assert result.attempts[1].validation_report.valid
