"""Generation orchestration for USS Engine v0.3.

The generator is LLM-client agnostic and now redacts normalized transcripts before
prompt compilation by default. Production users can wire in OpenAI, Anthropic,
Ollama, or internal gateway clients by implementing `LLMClient`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from .clients.base import LLMClient, StaticLLMClient
from .prompt_compiler import RuntimePrompt, compile_repair_prompt, compile_runtime_prompt, load_protocol
from .redactor import RedactionConfig, RedactionReport, redact_thread
from .schema import InvocationMode, ValidationReport
from .transcript import NormalizedThread, load_thread
from .validator import validate_text


class GenerationAttempt(BaseModel):
    attempt_number: int
    prompt_metadata: dict = Field(default_factory=dict)
    output: str
    validation_report: ValidationReport


class GenerationResult(BaseModel):
    valid: bool
    mode: InvocationMode
    attempts: list[GenerationAttempt]
    final_output: str
    final_report: ValidationReport
    redaction_report: RedactionReport
    redacted_thread: NormalizedThread


@dataclass(slots=True)
class GenerationConfig:
    max_attempts: int = 2
    max_transcript_chars: int | None = None
    redaction: RedactionConfig | None = None

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


def generate_summary(
    *,
    protocol: dict,
    thread: NormalizedThread,
    mode: InvocationMode | str,
    client: LLMClient,
    config: GenerationConfig | None = None,
) -> GenerationResult:
    """Generate a USS summary and validate after each attempt.

    v0.3 safety order:
    1. Normalize/load transcript upstream.
    2. Redact the normalized thread.
    3. Compile runtime prompt from the redacted thread.
    4. Generate candidate output.
    5. Validate candidate output.
    6. Retry with repair prompt when invalid.
    """

    cfg = config or GenerationConfig()
    resolved_mode = InvocationMode(mode)
    redaction_result = redact_thread(thread, cfg.redaction)
    runtime_prompt: RuntimePrompt = compile_runtime_prompt(
        protocol=protocol,
        thread=redaction_result.thread,
        mode=resolved_mode,
        max_transcript_chars=cfg.max_transcript_chars,
        redaction_report=redaction_result.report,
    )

    attempts: list[GenerationAttempt] = []
    active_prompt = runtime_prompt
    output = ""
    report = ValidationReport.from_issues(
        issues=[],
        mode=resolved_mode,
        protocol_version=str(protocol.get("version", "1.3")),
    )

    for attempt_number in range(1, cfg.max_attempts + 1):
        output = client.complete(active_prompt.as_messages()).strip()
        report = validate_text(output)
        attempts.append(
            GenerationAttempt(
                attempt_number=attempt_number,
                prompt_metadata=active_prompt.metadata,
                output=output,
                validation_report=report,
            )
        )
        if report.valid:
            break
        if attempt_number < cfg.max_attempts:
            active_prompt = compile_repair_prompt(
                previous_output=output,
                validation_report=report,
                runtime_prompt=runtime_prompt,
            )

    return GenerationResult(
        valid=report.valid,
        mode=resolved_mode,
        attempts=attempts,
        final_output=output,
        final_report=report,
        redaction_report=redaction_result.report,
        redacted_thread=redaction_result.thread,
    )


def generate_summary_from_files(
    *,
    protocol_path: str | Path,
    thread_path: str | Path,
    mode: InvocationMode | str,
    client: LLMClient,
    config: GenerationConfig | None = None,
) -> GenerationResult:
    """Convenience wrapper for file-backed generation."""

    protocol = load_protocol(protocol_path)
    thread = load_thread(thread_path)
    return generate_summary(protocol=protocol, thread=thread, mode=mode, client=client, config=config)
