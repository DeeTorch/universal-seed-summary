"""USS Engine command-line interface."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import typer
from rich.console import Console

from .clients import AnthropicClient, GeminiClient, GrokClient, OllamaClient, OpenAIClient, StaticLLMClient
from .config import all_provider_secret_statuses, load_env_file, provider_secret_status
from .evidence import build_evidence_map_from_files
from .generator import GenerationConfig, generate_summary_from_files
from .inspector import inspect_files, write_inspection_json
from .prompt_compiler import compile_runtime_prompt, load_protocol
from .redactor import RedactionConfig, redact_thread
from .reports import ProviderKind
from .run import RunConfig, run_uss_pipeline
from .schema import InvocationMode
from .transcript import load_thread, save_thread
from .validator import validate_file

app = typer.Typer(no_args_is_help=True, help="USS Engine v1.1 CLI")
console = Console()


@app.command()
def validate(
    input_path: Path = typer.Argument(..., help="Path to a USS Markdown artifact."),
    protocol: Path | None = typer.Option(None, "--protocol", help="Reserved for future protocol selection."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON validation report."),
) -> None:
    """Validate a USS Markdown artifact."""

    if protocol is not None and not protocol.exists():
        raise typer.BadParameter(f"Protocol file does not exist: {protocol}")

    report = validate_file(input_path)

    if json_output:
        console.print(json.dumps(report.model_dump(mode="json"), indent=2))
    else:
        _print_validation_report(input_path, report)

    raise typer.Exit(code=0 if report.valid else 1)


@app.command()
def normalize(
    input_path: Path = typer.Argument(..., help="Path to a raw .txt/.md transcript or JSON transcript."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Path for normalized thread JSON."),
    json_output: bool = typer.Option(False, "--json", help="Print normalized JSON to stdout."),
) -> None:
    """Normalize a raw transcript into USS Engine thread JSON."""

    thread = load_thread(input_path)
    payload = json.dumps(thread.model_dump(mode="json"), indent=2, ensure_ascii=False)

    if output is not None:
        save_thread(thread, output)
        console.print(f"[green]NORMALIZED:[/green] {input_path} -> {output}")
    elif json_output:
        console.print(payload)
    else:
        console.print(f"[green]NORMALIZED:[/green] {input_path}")
        console.print(f"Thread ID: {thread.thread_id}")
        console.print(f"Source: {thread.source}")
        console.print(f"Messages: {len(thread.messages)}")
        console.print(f"Exchange Pairs: {thread.exchange_pair_count}")


@app.command()
def redact(
    input_path: Path = typer.Argument(..., help="Path to normalized/raw thread input."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write redacted normalized thread JSON."),
    report_output: Path | None = typer.Option(None, "--report", help="Write redaction report JSON."),
    keep_emails: bool = typer.Option(False, "--keep-emails", help="Do not redact email addresses."),
    keep_phone_numbers: bool = typer.Option(False, "--keep-phone-numbers", help="Do not redact phone numbers."),
    json_output: bool = typer.Option(False, "--json", help="Print redaction report JSON."),
) -> None:
    """Redact secrets/PII from a transcript before generation."""

    thread = load_thread(input_path)
    result = redact_thread(
        thread,
        RedactionConfig(
            redact_emails=not keep_emails,
            redact_phone_numbers=not keep_phone_numbers,
        ),
    )

    if output is not None:
        save_thread(result.thread, output)
        console.print(f"[green]REDACTED THREAD:[/green] {output}")
    if report_output is not None:
        report_output.write_text(
            json.dumps(result.report.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        console.print(f"[green]REDACTION REPORT:[/green] {report_output}")

    if json_output:
        console.print(json.dumps(result.report.model_dump(mode="json"), indent=2, ensure_ascii=False))
    elif output is None and report_output is None:
        console.print(f"[green]REDACTION COMPLETE[/green] hits={result.report.hit_count}")
        for category, count in result.report.categories.items():
            console.print(f"- {category}: {count}")


@app.command("compile-prompt")
def compile_prompt(
    input_path: Path = typer.Argument(..., help="Path to normalized/raw thread input."),
    mode: InvocationMode = typer.Option(InvocationMode.checkpoint, "--mode", help="USS invocation mode."),
    protocol: Path = typer.Option(Path("protocols/uss_v1_3.protocol.json"), "--protocol", help="Protocol JSON path."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write compiled prompt text."),
    max_transcript_chars: int | None = typer.Option(None, "--max-transcript-chars", help="Optional transcript char budget."),
    no_redaction: bool = typer.Option(False, "--no-redaction", help="Compile prompt without pre-generation redaction."),
) -> None:
    """Compile protocol + normalized/redacted thread into an LLM runtime prompt."""

    protocol_data = load_protocol(protocol)
    thread = load_thread(input_path)
    redaction_result = redact_thread(thread, RedactionConfig(enabled=not no_redaction))
    runtime_prompt = compile_runtime_prompt(
        protocol=protocol_data,
        thread=redaction_result.thread,
        mode=mode,
        max_transcript_chars=max_transcript_chars,
        redaction_report=redaction_result.report,
    )
    prompt_text = runtime_prompt.as_text()

    if output is not None:
        output.write_text(prompt_text + "\n", encoding="utf-8")
        console.print(f"[green]COMPILED:[/green] {output}")
    else:
        console.print(prompt_text)


@app.command()
def generate(
    input_path: Path = typer.Argument(..., help="Path to normalized/raw thread input."),
    candidate_output: Path | None = typer.Argument(
        None,
        help="Path to a prepared candidate USS Markdown output for static/demo generation.",
    ),
    mode: InvocationMode = typer.Option(InvocationMode.checkpoint, "--mode", help="USS invocation mode."),
    protocol: Path = typer.Option(Path("protocols/uss_v1_3.protocol.json"), "--protocol", help="Protocol JSON path."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write final generated artifact."),
    max_attempts: int = typer.Option(1, "--max-attempts", help="Maximum validation/repair attempts."),
    json_report: bool = typer.Option(False, "--json", help="Print final validation report as JSON."),
    redaction_report: Path | None = typer.Option(None, "--redaction-report", help="Write redaction report JSON."),
    no_redaction: bool = typer.Option(False, "--no-redaction", help="Disable pre-generation redaction."),
    provider: str = typer.Option("static", "--provider", help="static, openai, anthropic, gemini, grok/xai, or ollama."),
    model: str | None = typer.Option(None, "--model", help="Provider model name."),
    env_file: Path | None = typer.Option(Path(".env"), "--env-file", help="Optional .env file to load before provider calls."),
) -> None:
    """Run generator orchestration with redaction + provider adapter support.

    Static mode uses a prepared candidate artifact. Provider modes call the chosen
    adapter through the shared LLMClient contract.
    """

    if env_file is not None:
        load_env_file(env_file)
    client = _build_client(provider=provider, model=model, candidate_output=candidate_output, max_attempts=max_attempts)
    result = generate_summary_from_files(
        protocol_path=protocol,
        thread_path=input_path,
        mode=mode,
        client=client,
        config=GenerationConfig(
            max_attempts=max_attempts,
            redaction=RedactionConfig(enabled=not no_redaction),
        ),
    )

    if output is not None:
        output.write_text(result.final_output + "\n", encoding="utf-8")
        console.print(f"[green]GENERATED:[/green] {output}")

    if redaction_report is not None:
        redaction_report.write_text(
            json.dumps(result.redaction_report.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        console.print(f"[green]REDACTION REPORT:[/green] {redaction_report}")

    if json_report:
        console.print(json.dumps(result.final_report.model_dump(mode="json"), indent=2))
    else:
        status = "VALID" if result.valid else "INVALID"
        style = "green" if result.valid else "red"
        console.print(f"[{style}]{status}:[/{style}] generation attempts={len(result.attempts)}")
        console.print(f"Mode: {result.mode.value}")
        console.print(f"Redaction Hits: {result.redaction_report.hit_count}")
        console.print(f"Issues: {result.final_report.issue_count}")
        for issue in result.final_report.issues:
            console.print(f"- [{issue.severity}] [{issue.code}] {issue.message}")

    raise typer.Exit(code=0 if result.valid else 1)


@app.command("run")
def run_pipeline(
    input_path: Path = typer.Argument(..., help="Path to normalized/raw thread input."),
    provider: ProviderKind = typer.Option(ProviderKind.static, "--provider", help="static, openai, anthropic, gemini, grok/xai, or ollama."),
    mode: InvocationMode = typer.Option(InvocationMode.checkpoint, "--mode", help="USS invocation mode."),
    output_dir: Path = typer.Option(Path("output"), "--output-dir", help="Directory for full E2E artifacts."),
    protocol: Path = typer.Option(Path("protocols/uss_v1_3.protocol.json"), "--protocol", help="Protocol JSON path."),
    model: str | None = typer.Option(None, "--model", help="Provider model name."),
    max_attempts: int = typer.Option(2, "--max-attempts", help="Maximum validation/repair attempts."),
    max_transcript_chars: int | None = typer.Option(None, "--max-transcript-chars", help="Optional transcript char budget."),
    candidate_output: Path | None = typer.Option(None, "--candidate", help="Optional static provider candidate artifact."),
    no_redaction: bool = typer.Option(False, "--no-redaction", help="Disable pre-generation redaction."),
    fail_on_invalid: bool = typer.Option(False, "--fail-on-invalid", help="Raise non-zero when final artifact is invalid."),
    env_file: Path | None = typer.Option(Path(".env"), "--env-file", help="Optional .env file to load before provider calls."),
    json_output: bool = typer.Option(False, "--json", help="Print generation report JSON."),
) -> None:
    """Run the complete MVP pipeline and write all six release artifacts."""

    if env_file is not None:
        load_env_file(env_file)

    result = run_uss_pipeline(
        thread_path=input_path,
        protocol_path=protocol,
        output_dir=output_dir,
        config=RunConfig(
            mode=mode,
            provider=provider,
            model=model,
            max_attempts=max_attempts,
            max_transcript_chars=max_transcript_chars,
            redaction=RedactionConfig(enabled=not no_redaction),
            static_candidate_path=candidate_output,
            fail_on_invalid=fail_on_invalid,
        ),
    )

    if json_output:
        console.print(json.dumps(result.report.model_dump(mode="json"), indent=2, ensure_ascii=False))
    else:
        style = "green" if result.report.valid else "red"
        console.print(f"[{style}]RUN {result.report.status.value.upper()}[/{style}]")
        console.print(f"Provider: {result.report.provider.value}")
        console.print(f"Mode: {result.report.mode.value}")
        console.print(f"MVP Ready: {result.report.mvp_ready}")
        console.print(f"Inspection Score: {result.report.inspection_score} ({result.report.inspection_grade})")
        console.print(f"Output Dir: {result.output_paths.output_dir}")
        console.print("Artifacts:")
        console.print(f"- {result.output_paths.summary_md}")
        console.print(f"- {result.output_paths.validation_report_json}")
        console.print(f"- {result.output_paths.redaction_report_json}")
        console.print(f"- {result.output_paths.evidence_map_json}")
        console.print(f"- {result.output_paths.inspection_report_json}")
        console.print(f"- {result.output_paths.generation_report_json}")
        for warning in result.report.warnings:
            console.print(f"[yellow]WARNING:[/yellow] {warning}")
        for error in result.report.errors:
            console.print(f"[red]ERROR:[/red] {error}")

    raise typer.Exit(code=0 if result.report.valid else 1)


@app.command("evidence-map")
def evidence_map(
    summary_path: Path = typer.Argument(..., help="Path to a USS Markdown artifact."),
    thread_path: Path = typer.Argument(..., help="Path to the source normalized/raw thread input."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write evidence map JSON."),
    json_output: bool = typer.Option(False, "--json", help="Print evidence map JSON."),
) -> None:
    """Build a deterministic evidence map from summary claims to source messages."""

    result = build_evidence_map_from_files(summary_path=summary_path, thread_path=thread_path)
    payload = json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False)
    if output is not None:
        output.write_text(payload + "\n", encoding="utf-8")
        console.print(f"[green]EVIDENCE MAP:[/green] {output}")
    elif json_output:
        console.print(payload)
    else:
        console.print(f"[green]EVIDENCE MAP[/green] claims={result.coverage.claim_count}")
        console.print(f"Supported: {result.coverage.supported_count}")
        console.print(f"Weak: {result.coverage.weakly_supported_count}")
        console.print(f"Unsupported: {result.coverage.unsupported_count}")
        console.print(f"Weighted Support: {result.coverage.weighted_support_ratio}")


@app.command()
def inspect(
    summary_path: Path = typer.Argument(..., help="Path to a USS Markdown artifact."),
    thread_path: Path | None = typer.Option(None, "--thread", help="Optional source thread for evidence anchoring."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write full inspection JSON."),
    json_output: bool = typer.Option(False, "--json", help="Print full inspection JSON."),
) -> None:
    """Inspect structure, evidence support, risk surface, and MVP readiness."""

    result = inspect_files(summary_path=summary_path, thread_path=thread_path)
    if output is not None:
        write_inspection_json(result, output)
        console.print(f"[green]INSPECTION REPORT:[/green] {output}")

    if json_output:
        console.print(json.dumps(result.model_dump(mode="json"), indent=2, ensure_ascii=False))
    else:
        style = "green" if result.score.mvp_ready else "yellow"
        console.print(f"[{style}]INSPECTION SCORE:[/{style}] {result.score.total_score} ({result.score.grade})")
        console.print(f"MVP Ready: {result.score.mvp_ready}")
        console.print(f"Structural Valid: {result.validation_report.valid}")
        if result.evidence_map is not None:
            console.print(f"Evidence Claims: {result.evidence_map.coverage.claim_count}")
            console.print(f"Evidence Weighted Support: {result.evidence_map.coverage.weighted_support_ratio}")
            console.print(f"Unsupported Claims: {result.evidence_map.coverage.unsupported_count}")
        else:
            console.print("Evidence: not evaluated; pass --thread to anchor claims.")
        for recommendation in result.score.recommendations:
            console.print(f"- {recommendation}")


def _build_client(*, provider: str, model: str | None, candidate_output: Path | None, max_attempts: int):
    provider_key = provider.strip().lower()
    if provider_key == "static":
        if candidate_output is None:
            raise typer.BadParameter("candidate_output is required when --provider static")
        candidate = candidate_output.read_text(encoding="utf-8")
        return StaticLLMClient(outputs=[candidate] * max_attempts)
    if provider_key == "openai":
        return OpenAIClient.from_env(model=model or "gpt-4.1-mini")
    if provider_key == "anthropic":
        return AnthropicClient.from_env(model=model or "claude-sonnet-4-5")
    if provider_key == "gemini":
        return GeminiClient.from_env(model=model or "gemini-3.5-flash")
    if provider_key in {"grok", "xai"}:
        return GrokClient.from_env(model=model or "grok-4.3")
    if provider_key == "ollama":
        return OllamaClient.from_env(model=model or "llama3.2")
    raise typer.BadParameter("provider must be one of: static, openai, anthropic, gemini, grok, xai, ollama")


@app.command("provider-status")
def provider_status(
    env_file: Path | None = typer.Option(Path(".env"), "--env-file", help="Optional .env file to load before checking providers."),
    json_output: bool = typer.Option(False, "--json", help="Print provider status as JSON."),
) -> None:
    """Check whether provider API keys are configured without printing secrets."""

    loaded = None
    if env_file is not None:
        loaded = load_env_file(env_file)

    statuses = all_provider_secret_statuses()
    payload = {
        "env_file": loaded.path if loaded is not None else None,
        "loaded_keys": list(loaded.loaded_keys) if loaded is not None else [],
        "providers": [asdict(status) for status in statuses],
    }
    if json_output:
        console.print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if loaded is not None and loaded.loaded_keys:
            console.print(f"[green]ENV LOADED:[/green] {loaded.path} ({len(loaded.loaded_keys)} key names)")
        elif loaded is not None:
            console.print(f"[yellow]ENV:[/yellow] no new keys loaded from {loaded.path}")
        for status in statuses:
            style = "green" if status.configured else "red"
            source = f" via {status.env_key or status.source}" if status.configured else f" missing {status.env_key}"
            console.print(f"[{style}]{status.provider}:[/{style}] {'configured' if status.configured else 'not configured'}{source}")


@app.command("provider-smoke")
def provider_smoke(
    provider: ProviderKind = typer.Option(..., "--provider", help="openai, anthropic, gemini, grok/xai, or ollama."),
    model: str | None = typer.Option(None, "--model", help="Provider model name."),
    env_file: Path | None = typer.Option(Path(".env"), "--env-file", help="Optional .env file to load before calling provider."),
) -> None:
    """Run a tiny live provider call to verify credentials and routing."""

    if provider == ProviderKind.static:
        raise typer.BadParameter("provider-smoke requires a live provider, not static")
    if env_file is not None:
        load_env_file(env_file)
    status = provider_secret_status(provider.value)
    if not status.configured and provider != ProviderKind.ollama:
        raise typer.BadParameter(f"Missing API key for {provider.value}: set {status.env_key}")
    client = _build_client(provider=provider.value, model=model, candidate_output=None, max_attempts=1)
    response = client.complete([
        {"role": "system", "content": "Reply with exactly: USS_PROVIDER_OK"},
        {"role": "user", "content": "Provider smoke test."},
    ])
    console.print(f"[green]PROVIDER OK:[/green] {provider.value}")
    console.print(response.strip()[:500])


def _print_validation_report(input_path: Path, report) -> None:
    status = "VALID" if report.valid else "INVALID"
    style = "green" if report.valid else "red"
    console.print(f"[{style}]{status}:[/{style}] {input_path}")
    console.print(f"Mode: {report.mode or 'unknown'}")
    console.print(f"Protocol Version: {report.protocol_version or 'unknown'}")
    console.print(f"Issues: {report.issue_count}")
    for issue in report.issues:
        location = ""
        if issue.section or issue.field:
            location = f" ({issue.section or ''}{'.' if issue.section and issue.field else ''}{issue.field or ''})"
        console.print(f"- [{issue.severity}] [{issue.code}] {issue.message}{location}")


if __name__ == "__main__":
    app()
