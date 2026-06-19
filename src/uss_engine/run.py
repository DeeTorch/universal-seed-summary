"""Full end-to-end runner for USS Engine."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from .clients import AnthropicClient, GeminiClient, GrokClient, OllamaClient, OpenAIClient, StaticLLMClient
from .clients.base import LLMClient
from .evidence import build_evidence_map, validate_evidence_map
from .generator import GenerationConfig, GenerationResult, generate_summary
from .inspector import inspect_text
from .prompt_compiler import load_protocol
from .redactor import RedactionConfig
from .reports import (
    GenerationRunReport,
    ProviderKind,
    ReportArtifactPaths,
    RunStatus,
    build_run_report,
    now_utc,
    write_json_report,
)
from .schema import InvocationMode
from .transcript import NormalizedThread, load_thread


class E2ERunResult(BaseModel):
    """Returned by `run_uss_pipeline` after writing all artifacts."""

    report: GenerationRunReport
    generation: GenerationResult
    output_paths: ReportArtifactPaths


@dataclass(slots=True)
class RunConfig:
    """Configuration for a full USS Engine run."""

    mode: InvocationMode | str = InvocationMode.checkpoint
    provider: ProviderKind | str = ProviderKind.static
    model: str | None = None
    max_attempts: int = 2
    max_transcript_chars: int | None = None
    redaction: RedactionConfig | None = None
    static_candidate_path: str | Path | None = None
    fail_on_invalid: bool = False

    def __post_init__(self) -> None:
        self.mode = InvocationMode(self.mode)
        self.provider = ProviderKind(self.provider)
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


def run_uss_pipeline(
    *,
    thread_path: str | Path,
    output_dir: str | Path,
    protocol_path: str | Path = "protocols/uss_v1_3.protocol.json",
    config: RunConfig | None = None,
    client: LLMClient | None = None,
) -> E2ERunResult:
    """Execute the complete v1.0 MVP pipeline and write all expected artifacts.

    Output directory contract:
    - summary.md
    - validation_report.json
    - redaction_report.json
    - evidence_map.json
    - inspection_report.json
    - generation_report.json
    """

    cfg = config or RunConfig()
    started_monotonic = time.perf_counter()
    started_at = now_utc()
    run_id = _run_id(thread_path=thread_path, mode=cfg.mode, provider=cfg.provider, started_at=started_at)

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    paths = _artifact_paths(output_root)

    protocol = load_protocol(protocol_path)
    thread = load_thread(thread_path)
    selected_client = client or build_provider_client(
        provider=cfg.provider,
        model=cfg.model,
        thread=thread,
        mode=cfg.mode,
        candidate_path=cfg.static_candidate_path,
    )

    errors: list[str] = []
    warnings: list[str] = []

    try:
        generation = generate_summary(
            protocol=protocol,
            thread=thread,
            mode=cfg.mode,
            client=selected_client,
            config=GenerationConfig(
                max_attempts=cfg.max_attempts,
                max_transcript_chars=cfg.max_transcript_chars,
                redaction=cfg.redaction,
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive fatal report path
        finished_at = now_utc()
        duration_ms = int((time.perf_counter() - started_monotonic) * 1000)
        validation_stub = __import__("uss_engine.schema", fromlist=["ValidationReport"]).ValidationReport.from_issues(
            issues=[], mode=cfg.mode, protocol_version=str(protocol.get("version", "1.3"))
        )
        redaction_stub = __import__("uss_engine.redactor", fromlist=["RedactionReport"]).RedactionReport.from_hits([])
        report = build_run_report(
            run_id=run_id,
            status=RunStatus.failed_generation,
            mode=cfg.mode,
            provider=cfg.provider,
            model=cfg.model,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            input_thread_path=str(thread_path),
            protocol_path=str(protocol_path),
            output_paths=paths,
            validation_report=validation_stub,
            redaction_report=redaction_stub,
            inspection=None,
            attempts=[],
            errors=[str(exc)],
        )
        write_json_report(report, paths.generation_report_json)
        raise

    paths_summary = Path(paths.summary_md)
    paths_summary.write_text(generation.final_output.rstrip() + "\n", encoding="utf-8")
    write_json_report(generation.final_report, paths.validation_report_json)
    write_json_report(generation.redaction_report, paths.redaction_report_json)

    evidence_map = build_evidence_map(
        summary_text=generation.final_output,
        thread=generation.redacted_thread,
        artifact_id=str(paths_summary),
    )
    evidence_validation = validate_evidence_map(evidence_map, generation.redacted_thread)
    inspection = inspect_text(
        summary_text=generation.final_output,
        thread=generation.redacted_thread,
        artifact_path=str(paths_summary),
        thread_path=str(thread_path),
    )

    write_json_report(evidence_map, paths.evidence_map_json)
    write_json_report(inspection, paths.inspection_report_json)

    if not generation.valid:
        errors.append("Generated summary failed structural validation.")
    if evidence_map.coverage.unsupported_count:
        warnings.append(f"{evidence_map.coverage.unsupported_count} unsupported evidence claim(s) detected.")
    if not evidence_validation.valid:
        errors.extend(evidence_validation.issues)

    if errors:
        status = RunStatus.failed_validation
    elif warnings:
        status = RunStatus.completed_with_warnings
    else:
        status = RunStatus.completed

    finished_at = now_utc()
    duration_ms = int((time.perf_counter() - started_monotonic) * 1000)
    report = build_run_report(
        run_id=run_id,
        status=status,
        mode=cfg.mode,
        provider=cfg.provider,
        model=cfg.model,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        input_thread_path=str(thread_path),
        protocol_path=str(protocol_path),
        output_paths=paths,
        validation_report=generation.final_report,
        redaction_report=generation.redaction_report,
        inspection=inspection,
        attempts=generation.attempts,
        warnings=warnings,
        errors=errors,
    )
    write_json_report(report, paths.generation_report_json)

    if cfg.fail_on_invalid and not report.valid:
        raise RuntimeError("USS run completed but produced an invalid artifact")

    return E2ERunResult(report=report, generation=generation, output_paths=paths)


def build_provider_client(
    *,
    provider: ProviderKind | str,
    model: str | None = None,
    thread: NormalizedThread | None = None,
    mode: InvocationMode | str = InvocationMode.checkpoint,
    candidate_path: str | Path | None = None,
) -> LLMClient:
    """Build a client for the requested provider.

    Static mode uses a deterministic local USS artifact and performs no network
    request. Other providers use their env-backed adapters and never receive raw
    secrets because the redaction layer runs before prompt compilation.
    """

    provider_kind = ProviderKind(provider)
    resolved_mode = InvocationMode(mode)
    if provider_kind == ProviderKind.static:
        if candidate_path is not None:
            candidate = Path(candidate_path).read_text(encoding="utf-8")
        else:
            if thread is None:
                raise ValueError("thread is required for generated static candidates")
            candidate = render_static_uss_summary(thread=thread, mode=resolved_mode)
        return StaticLLMClient(outputs=[candidate])
    if provider_kind == ProviderKind.openai:
        return OpenAIClient.from_env(model=model or "gpt-4.1-mini")
    if provider_kind == ProviderKind.anthropic:
        return AnthropicClient.from_env(model=model or "claude-sonnet-4-5")
    if provider_kind == ProviderKind.gemini:
        return GeminiClient.from_env(model=model or "gemini-3.5-flash")
    if provider_kind in {ProviderKind.grok, ProviderKind.xai}:
        return GrokClient.from_env(model=model or "grok-4.3")
    if provider_kind == ProviderKind.ollama:
        return OllamaClient.from_env(model=model or "llama3.2")
    raise ValueError(f"Unsupported provider: {provider}")


def render_static_uss_summary(*, thread: NormalizedThread, mode: InvocationMode | str) -> str:
    """Render a deterministic USS artifact for static E2E testing.

    This is not a substitute for LLM generation. It is a contract fixture that
    proves the entire pipeline can write, validate, anchor, inspect, and report.
    """

    resolved_mode = InvocationMode(mode)
    now = now_utc()
    first_user = next((m for m in thread.messages if m.role.value == "user"), thread.messages[0])
    refs = ", ".join(message.id for message in thread.messages[: min(3, len(thread.messages))])
    ref_one = first_user.id
    thread_depth = str(thread.exchange_pair_count or max(1, len(thread.messages) // 2))
    archive_block = ""
    if resolved_mode == InvocationMode.archive:
        archive_block = f"""
---

### EXECUTION ARTIFACTS (Archive Mode Only)

**Generated_Outputs**: USS summary artifact, validation report, redaction report, evidence map, inspection report, and generation report are expected outputs for the engine run. [evidence: {refs}]
**Tool_Usage_Patterns**: The static provider path uses the same validator, evidence mapper, and inspector without external LLM calls. [evidence: {refs}]
**Reusability_Index**: The pipeline pattern is reusable for checkpoint, re-entry, and archive USS modes. [evidence: {refs}]
**Integration_Notes**: Provider-backed generation can replace the static candidate through the shared LLMClient contract. [evidence: {refs}]
"""

    return f"""---
mode: {resolved_mode.value}
protocol: Universal Seed Summary Invoker
protocol_version: "1.3"
timestamp: "{now}"
source_thread_id: {thread.thread_id}
tool_version: "1.1.0"
---

### HEADER (THREAD LOCK & AUDIT)

**Thread_Archetype**: Development_Forge [evidence: {refs}]
**Ignition_Vector**: The thread requested a USS Engine execution path that converts a transcript into validated continuity artifacts. [evidence: {ref_one}]
**Focus_Domains**: AI_Architecture + Epistemic_Distillation + CLI_Tooling [evidence: {refs}]
**Thread_Depth**: {thread_depth} [evidence: {refs}]
**Completion_State**: Stabilizing [evidence: {refs}]
**Momentum_Indicator**: Accelerating [evidence: {refs}]
**Finalization_Beacon**: {now}
**Invoker**: Invoking user and target model are known only within the supplied normalized thread bounds. [evidence: {refs}]

---

### FAILURE SEMANTICS & INTEGRITY FLAGS

**Incoherence_Flags**: None detected within thread bounds.
**Compression_Loss_Warnings**: No significant compression loss identified.
**Inference_Boundary_Alerts**: No inference boundary approached.
**Resolution_Impossibility_Markers**:
- Live provider behavior cannot be proven by static mode alone; provider execution requires configured runtime credentials or a local Ollama server. [evidence: {refs}]
**Failure_Severity**: Low - static E2E output is structurally valid but not a semantic substitute for live provider generation. [evidence: {refs}]

---

### COSMIC CORE & EMERGENCE

**Ontological_Constructs**:
- USS Engine is treated as a local-first continuity engine rather than a loose prompt. [evidence: {refs}]
- The artifact must stay thread-derived and validation-backed. [evidence: {refs}]
**Paradigm_Nodes**:
1. The mission moved from protocol design into executable end-to-end tooling. [evidence: {refs}]
2. Evidence anchoring makes thread-derived claims inspectable after generation. [evidence: {refs}]
**Emergent_Universals**:
- Durable AI memory artifacts require generation, validation, redaction, evidence mapping, and inspection as separate layers. [evidence: {refs}]

---

### DECISIONS & GRAFTS

**Architecture_Commits**:
- Preserve the validator as the trust spine. [evidence: {refs}]
- Run redaction before prompt compilation and generation. [evidence: {refs}]
- Emit summary, validation, redaction, evidence, inspection, and generation reports from one command. [evidence: {refs}]
**Heuristic_Branches**:
- Static generation proves orchestration while OpenAI, Anthropic, and Ollama adapters provide live execution paths. [evidence: {refs}]
**Epistemic_Locks**:
- Claims must be grounded in supplied source messages or explicitly marked as unresolved. [evidence: {refs}]

---

### OPEN VECTORS & THRUST

**Unresolved_Queries**:
- Which live provider should become the default production path remains unresolved within this artifact. [evidence: {refs}]
**Priority_Vectors**:
1. Verify provider-backed generation with configured credentials or a local Ollama runtime. [evidence: {refs}]
2. Harden repair prompts using exact validator errors. [evidence: {refs}]
3. Package v1.0 with release docs and reproducible examples. [evidence: {refs}]
**Risk_Surfaces**:
- Static output can prove file contracts and validation, but not provider quality, cost, latency, or model-specific formatting drift. [evidence: {refs}]
{archive_block}
---

### INVOCATION LOCK

This USS artifact is complete for `{resolved_mode.value}` mode and locked as a deterministic v1.0 MVP pipeline output. It is suitable for validating the end-to-end artifact contract, while live provider conclusions remain bounded by future configured execution. [evidence: {refs}]
""".strip()


def _artifact_paths(output_dir: Path) -> ReportArtifactPaths:
    return ReportArtifactPaths(
        output_dir=str(output_dir),
        summary_md=str(output_dir / "summary.md"),
        validation_report_json=str(output_dir / "validation_report.json"),
        redaction_report_json=str(output_dir / "redaction_report.json"),
        evidence_map_json=str(output_dir / "evidence_map.json"),
        inspection_report_json=str(output_dir / "inspection_report.json"),
        generation_report_json=str(output_dir / "generation_report.json"),
    )


def _run_id(*, thread_path: str | Path, mode: InvocationMode, provider: ProviderKind, started_at: str) -> str:
    seed = f"{thread_path}|{mode.value}|{provider.value}|{started_at}".encode("utf-8")
    return "run_" + hashlib.sha1(seed).hexdigest()[:12]
