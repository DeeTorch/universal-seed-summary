# USS Engine Codebase Overview

This document explains the USS Engine v1.1.2 repository for future maintainers before v1.2 work begins. v1.1.2 is a documentation and release-freeze baseline. The package version still reports `1.1.1` because the tag did not change core engine behavior.

## What USS Engine Is

USS Engine is a local-first continuity engine for Universal Seed Summary artifacts. It turns raw or normalized conversation transcripts into validated USS Markdown summaries, then produces machine-readable reports that prove structure, redaction, evidence anchoring, inspection score, and run metadata.

The project is intentionally conservative at this stage:

- It normalizes transcripts into a stable internal thread model.
- It redacts common secrets and PII before prompt compilation.
- It compiles a protocol-driven runtime prompt.
- It routes generation through a small provider client contract.
- It validates generated USS Markdown against the protocol structure.
- It builds deterministic evidence maps from summary claims to source messages.
- It scores artifacts for release/MVP readiness.
- It writes a reproducible artifact bundle from one `uss run` command.

## High-Level Runtime Pipeline

The full `uss run` path is implemented in `src/uss_engine/run.py`.

```text
input transcript
  -> transcript.load_thread()
  -> prompt_compiler.load_protocol()
  -> build provider client
  -> generator.generate_summary()
     -> redactor.redact_thread()
     -> prompt_compiler.compile_runtime_prompt()
     -> client.complete()
     -> validator.validate_text()
     -> optional repair prompt retry
  -> write summary.md
  -> write validation_report.json
  -> write redaction_report.json
  -> evidence.build_evidence_map()
  -> evidence.validate_evidence_map()
  -> inspector.inspect_text()
  -> scoring.score_artifact()
  -> write evidence_map.json
  -> write inspection_report.json
  -> reports.build_run_report()
  -> write generation_report.json
```

Static provider runs are deterministic and network-free. Live provider runs use the same pipeline after credentials are loaded from environment variables or a local `.env` file.

## Major Directories

### `protocols/`

Protocol source files and canonical protocol definitions. The default runtime protocol is `protocols/uss_v1_3.protocol.json`, which is loaded by `prompt_compiler.load_protocol()` and used by `uss run`, `uss generate`, and `uss compile-prompt`.

### `schemas/`

JSON schema files for durable output artifacts such as summaries, evidence maps, generation reports, redaction reports, and normalized threads. These are useful for downstream validation and integration, while the Python runtime currently relies mainly on Pydantic models.

### `src/uss_engine/`

The engine implementation. This contains the CLI, transcript normalization, prompt compilation, generation orchestration, validation, redaction, evidence anchoring, inspection, scoring, report writing, provider configuration, and the full end-to-end runner.

### `src/uss_engine/clients/`

Provider adapters and the shared client contract. The engine core depends on the `LLMClient` protocol in `clients/base.py`, not on provider-specific SDKs. Current adapters include static, OpenAI, Anthropic, Gemini, Grok/xAI, and Ollama.

### `tests/`

Pytest coverage for the engine contract. Tests cover static client behavior, end-to-end static runs, evidence anchoring, generation, inspection, prompt compilation, provider config, redaction, transcript loading, and validation.

### `examples/`

Sample transcripts, valid and invalid USS artifacts, provider run examples, and example output bundles. These are intended for documentation, smoke tests, and demonstrating expected artifact shapes. Do not treat generated local `output/` contents as examples unless they are sanitized and intentionally promoted.

### `docs/`

Maintainer and user documentation. Current docs cover installation, quickstarts, provider setup, release notes, release freeze state, provider validation, security hardening, release process, and roadmap planning.

### `.github/`

GitHub automation. The current workflow runs the test suite in CI.

## Major Modules

### `transcript.py`

Defines the normalized transcript model:

- `TranscriptRole`
- `TranscriptMessage`
- `NormalizedThread`

It supports permissive loading from JSON, Markdown, and text. Role-prefixed raw text is converted into structured messages. JSON inputs accept common aliases such as `messages`, `conversation`, `items`, `role`, `speaker`, `author`, `content`, `text`, and `message`.

The normalized thread is the stable input contract for redaction, prompt compilation, evidence mapping, and static generation.

### `prompt_compiler.py`

Loads the USS protocol JSON and compiles a `RuntimePrompt` containing a system prompt, user prompt, and metadata. It injects:

- protocol metadata
- invocation mode
- output specification
- enforcement rules
- required sections
- validation checklist
- redaction report
- normalized transcript block

It also builds repair prompts after validation failures. Repair prompts preserve the original system prompt but focus the user prompt on fixing validator issues without adding facts outside the source thread.

### `generator.py`

Provider-agnostic generation orchestration. It accepts a protocol, normalized thread, invocation mode, `LLMClient`, and `GenerationConfig`.

Its safety order is:

1. Redact the normalized thread.
2. Compile the runtime prompt from the redacted thread.
3. Call the provider client.
4. Validate the generated output.
5. Retry with a repair prompt when invalid and attempts remain.

The result includes all attempts, the final output, final validation report, redaction report, and redacted thread.

### `validator.py`

The structural validator for USS Markdown artifacts. It parses YAML front matter, Markdown sections, and `**Field**:` values, then checks required sections and required fields from `schema.py`.

It fails closed on missing front matter, missing sections, missing fields, vague nulls, invalid failure-severity values, and archive-mode requirements. It returns a machine-readable `ValidationReport`.

### `redactor.py`

Redacts common secrets and PII from normalized transcripts before prompt compilation. It works message-by-message and returns both a redacted thread and a `RedactionReport`.

Default categories include:

- email
- phone
- OpenAI-style API key
- Anthropic-style API key
- GitHub token
- AWS access key ID
- bearer token
- URL credentials
- private key block
- generic secret assignment

Redaction replaces matched values with placeholders and records hit metadata without preserving the original secret value.

### `evidence.py`

Builds deterministic evidence maps from USS summary claims to normalized source-thread messages. It extracts claims from USS fields, finds explicit evidence references, performs lexical matching when no explicit reference exists, and calculates coverage metrics.

After v1.1.1, evidence classification distinguishes ordinary factual claims from protocol/system fields that should not be penalized as unsupported factual claims.

### `inspector.py`

Combines structural validation, optional evidence mapping, evidence-reference validation, and scoring into an `ArtifactInspection` bundle. It is used by both CLI inspection and the full `uss run` pipeline.

### `scoring.py`

Computes a pragmatic 0-100 artifact score. The score is not a truth score; it measures whether the artifact is structurally valid, inspectable, and sufficiently anchored to the supplied thread.

Weights:

- `structure_validation`: 40%
- `evidence_coverage`: 35%
- `anchor_integrity`: 15%
- `risk_surface`: 10%

Grades are `A`, `B`, `C`, `D`, or `F`. `mvp_ready` requires a valid structure and a total score of at least 85.

### `run.py`

The full end-to-end runner behind `uss run`. It loads inputs, builds the provider client, runs generation, writes all artifacts, builds evidence and inspection reports, builds the final generation run report, and returns an `E2ERunResult`.

It also contains `render_static_uss_summary()`, the deterministic static artifact generator used for local and CI proof without network calls.

### `reports.py`

Defines provider kinds, run statuses, output paths, generation attempt summaries, and the top-level `GenerationRunReport`.

Report summaries intentionally exclude raw prompts. Attempt summaries include safe metadata, output length, and a short output preview.

### `config.py`

Environment and provider-secret helpers. It implements a minimal `.env` loader without third-party dotenv dependencies and exposes provider-secret status without printing secret values.

Supported provider key families:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `XAI_API_KEY`
- `OLLAMA_API_KEY` or local/default Ollama configuration

### `cli.py`

Typer-based command-line interface. Main commands:

- `uss validate`
- `uss normalize`
- `uss redact`
- `uss compile-prompt`
- `uss generate`
- `uss run`
- `uss evidence-map`
- `uss inspect`
- `uss provider-status`
- `uss provider-smoke`

`uss run` is the preferred full-pipeline entry point. `uss generate` is lower-level and requires a prepared candidate artifact for static mode.

## Provider Client Structure

All providers implement the `LLMClient` protocol:

```text
complete(messages: list[dict[str, str]]) -> str
```

The engine expects one candidate USS Markdown artifact per `complete()` call. Provider adapters are intentionally thin:

- `clients/base.py` defines `LLMClient`, `StaticLLMClient`, and `ClientConfig`.
- `clients/_http.py` provides shared HTTP POST behavior.
- `openai_client.py`, `anthropic_client.py`, `gemini_client.py`, `grok_client.py`, and `ollama_client.py` translate the common chat-message shape into each provider's API format.
- `run.build_provider_client()` selects the runtime provider for `uss run`.
- `cli._build_client()` selects the provider for the lower-level `uss generate` and `uss provider-smoke` commands.

Do not add a new provider by changing generation orchestration first. The intended seam is a new adapter that satisfies `LLMClient`, plus explicit tests and provider validation documentation.

## How Redaction Works

Redaction happens before prompt compilation in `generator.generate_summary()`. The original normalized thread is copied, message contents are replaced with placeholders where rules match, and redaction metadata is added to message and thread metadata.

Important properties:

- Redaction is deterministic and local.
- Redaction reports record categories, message IDs, roles, offsets, and placeholders.
- Redaction reports do not preserve original secret values.
- Redaction can be disabled through config or CLI flags, but default generation keeps it enabled.
- Redaction is a safety layer, not a guarantee. Do not send private material to a provider unless that provider is approved for the data.

## Evidence Scoring After v1.1.1

v1.1.1 calibrated evidence classification after live Gemini validation. Before that calibration, metadata and protocol-derived fields could be counted as unsupported factual claims even when they were not ordinary claims requiring direct lexical evidence.

Current evidence statuses include:

- `supported`
- `weakly_supported`
- `unsupported`
- `absent_claim`
- `derived_metadata`
- `system_metadata`
- `protocol_null_declaration`
- `protocol_assessment`

Key v1.1.1 behavior:

- Derived metadata fields such as `Thread_Archetype`, `Focus_Domains`, `Completion_State`, and `Momentum_Indicator` are classified separately.
- System metadata fields such as `Thread_Depth`, `Finalization_Beacon`, and `Invoker` are classified separately.
- Protocol null declarations such as "None detected within thread bounds" are not penalized as unsupported claims.
- Protocol assessment fields such as `Failure_Severity` are evaluated separately from direct lexical evidence.
- Unsupported factual claims still count as unsupported and reduce evidence coverage and risk score.

Coverage uses `weighted_support_ratio`:

- supported claims count fully
- weakly supported claims count partially
- non-penalized metadata/null/assessment classifications count fully for coverage
- unsupported claims reduce coverage

## What `uss run` Produces

`uss run <thread_path> --provider <provider> --mode <mode> --output-dir <dir>` writes six canonical artifacts:

```text
output/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

Purpose:

- `summary.md`: final USS Markdown artifact.
- `validation_report.json`: structural validation result.
- `redaction_report.json`: redaction categories and hit counts.
- `evidence_map.json`: claim-to-source-message evidence map.
- `inspection_report.json`: combined validation, evidence, and score bundle.
- `generation_report.json`: top-level run metadata, status, paths, attempts, score, warnings, and errors.

## How To Run Tests

From the repository root:

```powershell
python -m pytest -q
```

Expected v1.1.2 release-baseline result:

```text
39 passed
```

To confirm package version:

```powershell
python -c "import uss_engine; print(uss_engine.__version__)"
```

Expected v1.1.2 release-baseline output:

```text
1.1.1
```

The version remains `1.1.1` because v1.1.2 is a documentation/release-hardening tag, not a package behavior release.

## What Should Not Be Changed Casually

- The normalized transcript model in `transcript.py`.
- The validation contract in `schema.py` and `validator.py`.
- The redaction-before-prompt order in `generator.py`.
- The `LLMClient.complete()` provider contract.
- The six-artifact `uss run` output contract.
- The evidence status classifications added for v1.1.1 calibration.
- The scoring weights and `mvp_ready` threshold without new validation evidence.
- Provider default behavior, model defaults, or credential handling.
- `.env`, `.venv/`, `output/`, caches, or generated local provider outputs.

Any change to these areas should include tests, documentation updates, and provider validation notes.

## Recommended Entry Points For v1.2 Development

Start v1.2 work from narrow, testable seams:

- Semantic evidence matching: extend or wrap `evidence.py` without breaking deterministic evidence-map output.
- Archive store: add storage/indexing around the existing six-artifact output bundle from `run.py`.
- Artifact index/search: build on `ReportArtifactPaths`, generated JSON reports, and sanitized examples.
- Provider validation automation: generate or update `docs/provider_validation_matrix.md` from smoke/checkpoint results without embedding secrets.
- GitHub issue/PR summarizer: normalize external thread-like data into `NormalizedThread` before entering the existing pipeline.
- Obsidian export: transform validated `summary.md` and report metadata after generation rather than altering generation logic.
- Pre-commit secret scanning: add repository hygiene tooling without changing engine runtime behavior.
- Package distribution workflow: build from `pyproject.toml` and CI after release tagging policy is settled.

Avoid starting v1.2 by rewriting core orchestration. The stable extension pattern is:

```text
new input/source integration
  -> normalize into NormalizedThread
  -> use existing run/generate/validate/evidence/report pipeline
  -> add tests
  -> update docs
```
