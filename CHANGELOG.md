# Changelog

All notable changes to USS Engine are documented here.

## [1.1.1] - 2026-06-19

### Fixed

- Calibrated evidence classification to avoid false unsupported penalties for metadata and protocol fields.
- Added `derived_metadata`, `system_metadata`, `protocol_null_declaration`, and `protocol_assessment` evidence statuses.
- Classified `Focus_Domains`, `Invoker`, and `Failure_Severity` correctly after live Gemini provider validation.
- Preserved strict unsupported scoring for real unanchored factual claims.


## [1.1.0] - 2026-06-18

### Status

Provider activation release.

### Added

- `.env.example` for local provider credentials.
- `src/uss_engine/config.py` for safe `.env` loading and provider status checks.
- `GeminiClient` for Google Gemini `generateContent` execution.
- `GrokClient` for xAI Grok chat-completions execution.
- `uss provider-status` to check key presence without printing secrets.
- `uss provider-smoke` for tiny live provider routing tests.
- `--env-file` support for provider-backed `generate` and `run` commands.
- `docs/api_key_activation.md`.
- `docs/enterprise_deployment.md`.
- `docs/live_provider_validation.md`.
- Gemini, Grok, and enterprise OpenAI example run docs.

### Security

- Real keys stay outside source control.
- Redaction remains enabled by default.
- Generation reports still avoid raw prompt storage.

## [1.0.0] - 2026-06-18

### Status

First MVP release.

### Added

- Release-ready README with install, test, provider, and command overview.
- MIT `LICENSE` file.
- `docs/install.md` for local-first environment setup.
- `docs/provider_setup.md` for static, OpenAI-compatible, Anthropic, and Ollama provider configuration.
- `docs/v1_mvp_acceptance.md` with explicit MVP acceptance checklist.
- `examples/openai_run_example.md` with OpenAI-compatible run guidance.
- `examples/ollama_local_run_example.md` with local Ollama run guidance.
- v1.0 package metadata and version identifiers.

### Confirmed MVP Capabilities

- Transcript normalization.
- Pre-generation redaction.
- Runtime prompt compilation from USS v1.3 protocol.
- Provider-client execution path.
- Structural validation.
- Evidence map generation.
- Artifact inspection and scoring.
- Full six-file `uss run` output bundle.
- Static E2E proof bundle for deterministic CI verification.

### Notes

- Live provider execution requires local user configuration: API keys for hosted providers or a running Ollama server for local inference.
- Static mode remains the canonical network-free proof path.

## [0.5.0]

### Added

- Full `uss run` end-to-end CLI command.
- Run report generation.
- Static E2E tests.
- Provider payload contract tests.
- GitHub Actions CI workflow.
- Example six-artifact E2E output bundle.

## [0.4.0]

### Added

- Evidence anchoring.
- Artifact inspector.
- Scoring layer.
- Evidence map schema.

## [0.3.0]

### Added

- Redaction layer.
- OpenAI-compatible, Anthropic, and Ollama provider adapters.
- Provider client contract.

## [0.2.0]

### Added

- Transcript normalizer.
- Runtime prompt compiler.
- Generator loop foundation.

## [0.1.0]

### Added

- Product definition.
- Repository blueprint.
- Pydantic schema foundation.
- Markdown/YAML validator foundation.
