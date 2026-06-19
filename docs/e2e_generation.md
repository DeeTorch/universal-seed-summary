# USS Engine v1.0 — End-to-End Generation

v1.0 includes the full `uss run` command. The command executes the complete MVP pipeline and writes every durable artifact required for inspection and handoff.

## Pipeline

```text
Transcript
  → NormalizedThread
  → Redaction
  → RuntimePrompt
  → Provider Client
  → USS Markdown
  → Structural Validation
  → Evidence Map
  → Artifact Inspection
  → Generation Run Report
```

## Command

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/
```

Provider options:

```text
static
openai
anthropic
ollama
```

Static mode is deterministic and network-free. It is used for CI, contract tests, and local smoke tests.

## Output Contract

```text
output/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## Provider Environment Variables

OpenAI-compatible Chat Completions:

```bash
export OPENAI_API_KEY="..."
uss run examples/thread_minimal.json --provider openai --model gpt-4.1-mini --output-dir output/openai
```

Anthropic Messages API:

```bash
export ANTHROPIC_API_KEY="..."
uss run examples/thread_minimal.json --provider anthropic --model claude-sonnet-4-5 --output-dir output/anthropic
```

Ollama local chat:

```bash
ollama serve
ollama pull llama3.2
uss run examples/thread_minimal.json --provider ollama --model llama3.2 --output-dir output/ollama
```

## Exit Behavior

By default, `uss run` writes all reports even when the generated artifact is imperfect. The CLI exits non-zero only when the final structural artifact is invalid. Use `--fail-on-invalid` in automation when invalid outputs should halt the pipeline.

## Trust Boundaries

- `summary.md` is the generated USS artifact.
- `validation_report.json` proves structural compliance.
- `redaction_report.json` records pre-generation sensitive-data handling.
- `evidence_map.json` maps claims to source message IDs.
- `inspection_report.json` scores artifact readiness.
- `generation_report.json` summarizes the run without storing raw prompts.

## v1.0 Boundary

The repository includes provider adapter contract tests and a static E2E proof. Live provider calls require user-supplied credentials or a running local Ollama server. v1.0 is MVP complete for the local-first CLI engine; browser ingestion, dashboards, and archive databases are post-MVP.
