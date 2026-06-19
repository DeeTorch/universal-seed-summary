# USS Engine v1.1

**Universal Seed Summary Engine** is a local-first continuity engine for converting AI conversation transcripts into validated, redacted, evidence-anchored Universal Seed Summary artifacts.

The canonical protocol source is `protocols/uss_v1_3.protocol.json`, based on **Universal Seed Summary Invoker v1.3**. The engine treats that protocol as the operational source of truth and compiles it into a runnable pipeline.

## Runtime Path

```text
Transcript
  → NormalizedThread
  → Redaction
  → RuntimePrompt
  → Provider Client
  → USS Markdown
  → Validation Report
  → Evidence Map
  → Inspection Report
  → Generation Report
```

## What v1.1 Adds

v1.1 activates real provider routing while preserving the local-first trust spine.

New provider activation layer:

- `.env.example`
- `uss provider-status`
- `uss provider-smoke`
- `--env-file` support for `uss generate` and `uss run`
- Gemini adapter
- Grok / xAI adapter
- enterprise deployment notes
- live provider validation docs

## Install

```bash
python -m pip install -e .[dev]
pytest -q
uss --help
```

## Configure Provider Keys

```bash
cp .env.example .env
uss provider-status --env-file .env
```

Do not commit `.env`.

Supported variables:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY or GOOGLE_API_KEY
XAI_API_KEY
OLLAMA_BASE_URL optional, defaults to http://localhost:11434
```

## Provider Smoke Tests

```bash
uss provider-smoke --provider openai --model gpt-5.5 --env-file .env
uss provider-smoke --provider gemini --model gemini-3.5-flash --env-file .env
uss provider-smoke --provider grok --model grok-4.3 --env-file .env
uss provider-smoke --provider ollama --model llama3.2 --env-file .env
```

## Full Run

Static CI-safe proof:

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/static
```

OpenAI / ChatGPT Enterprise API Platform path:

```bash
uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-5.5 \
  --mode checkpoint \
  --output-dir output/openai \
  --env-file .env
```

Gemini path:

```bash
uss run examples/thread_minimal.json \
  --provider gemini \
  --model gemini-3.5-flash \
  --mode checkpoint \
  --output-dir output/gemini \
  --env-file .env
```

Grok / xAI path:

```bash
uss run examples/thread_minimal.json \
  --provider grok \
  --model grok-4.3 \
  --mode checkpoint \
  --output-dir output/grok \
  --env-file .env
```

Ollama local path:

```bash
uss run examples/thread_minimal.json \
  --provider ollama \
  --model llama3.2 \
  --mode checkpoint \
  --output-dir output/ollama
```

Expected output:

```text
output/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## Core Commands

```bash
uss validate examples/checkpoint_valid.md
uss normalize examples/thread_minimal.json --json
uss redact examples/thread_with_secrets.json --json
uss compile-prompt examples/thread_minimal.json --mode checkpoint --output prompt.txt
uss generate examples/thread_minimal.json examples/checkpoint_valid.md --mode checkpoint
uss evidence-map examples/summary_with_evidence.md examples/thread_minimal.json --output evidence_map.json
uss inspect examples/summary_with_evidence.md --thread examples/thread_minimal.json --output inspection_report.json
uss run examples/thread_minimal.json --provider static --mode checkpoint --output-dir output/
```

## Release Docs

```text
CHANGELOG.md
LICENSE
docs/install.md
docs/provider_setup.md
docs/api_key_activation.md
docs/enterprise_deployment.md
docs/live_provider_validation.md
docs/v1_mvp_acceptance.md
examples/openai_run_example.md
examples/gemini_run_example.md
examples/grok_run_example.md
examples/enterprise_openai_run_example.md
examples/ollama_local_run_example.md
```

## Status

**USS Engine v1.1 is provider-activation ready.**

The next post-MVP work is true live-provider validation in your environment, semantic evidence scoring, optional archive storage, browser/export ingestion, and a web dashboard.
