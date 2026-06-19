# USS Engine v1.0 — MVP Acceptance Checklist

This document defines what “100% MVP complete” means for USS Engine v1.0.

## Core Acceptance Criteria

- [x] Repository installs in an isolated Python environment.
- [x] CLI entrypoint exists as `uss`.
- [x] USS v1.3 protocol is stored as a canonical source artifact.
- [x] Transcript inputs can be normalized into `NormalizedThread`.
- [x] Sensitive content can be redacted before generation.
- [x] Runtime prompts can be compiled from the protocol and normalized thread.
- [x] Provider adapter contract exists.
- [x] Static provider proves deterministic E2E behavior.
- [x] OpenAI-compatible adapter path exists.
- [x] Anthropic adapter path exists.
- [x] Ollama adapter path exists.
- [x] Generated USS Markdown can be structurally validated.
- [x] Evidence maps can be generated from summaries and source threads.
- [x] Artifact inspection report can score readiness.
- [x] `uss run` writes all six expected MVP artifacts.
- [x] Test suite passes.
- [x] GitHub Actions workflow exists.
- [x] README documents the MVP path.
- [x] Install guide exists.
- [x] Provider setup guide exists.
- [x] Changelog exists.
- [x] License file exists.

## Canonical MVP Command

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/
```

## Required Output Bundle

```text
output/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## MVP Quality Gate

A v1.0 artifact run is considered acceptable when:

- `validation_report.json.valid` is `true`.
- `generation_report.json.valid` is `true`.
- `generation_report.json.mvp_ready` is `true` for the static proof path.
- `inspection_report.json` includes a numeric score and grade.
- `evidence_map.json` contains claim coverage metrics.
- `redaction_report.json` exists even if there are zero redaction hits.

## Known MVP Boundaries

- Browser scraping/export ingestion is not included.
- SaaS dashboard is not included.
- SQLite archive storage is not included.
- Live hosted provider calls require user-provided credentials.
- Static mode proves orchestration, not provider quality.
- Evidence anchoring is deterministic and source-ID based; deeper semantic entailment is post-MVP.

## Tagged Release Checklist

Before tagging:

```bash
pytest -q
uss run examples/thread_minimal.json --provider static --mode checkpoint --output-dir output/release-smoke
```

Then verify:

```text
CHANGELOG.md updated
README.md current
LICENSE present
pyproject.toml version = 1.0.0
src/uss_engine/__init__.py version = 1.0.0
examples/e2e_output refreshed
```

Suggested tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```
