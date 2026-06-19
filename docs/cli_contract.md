# USS Engine CLI Contract v0.4

## `uss validate`

```bash
uss validate examples/checkpoint_valid.md
uss validate examples/checkpoint_valid.md --json
```

Validates USS Markdown structure, front matter, required sections, required fields, failure semantics, timestamp format, and archive-only artifact requirements.

## `uss normalize`

```bash
uss normalize examples/thread_minimal.json --json
uss normalize raw_thread.txt --output normalized_thread.json
```

Normalizes raw or JSON transcripts into `NormalizedThread`.

## `uss redact`

```bash
uss redact examples/thread_with_secrets.json --json
uss redact examples/thread_with_secrets.json --output redacted_thread.json --report redaction_report.json
```

Redacts secrets and selected PII before prompt compilation.

## `uss compile-prompt`

```bash
uss compile-prompt examples/thread_minimal.json --mode checkpoint --output prompt.txt
```

Compiles USS v1.3 protocol + normalized/redacted transcript into a runtime LLM prompt.

## `uss generate`

```bash
uss generate examples/thread_minimal.json examples/checkpoint_valid.md --mode checkpoint
uss generate examples/thread_minimal.json --provider ollama --model llama3.2 --mode checkpoint --output summary.md
```

Runs transcript loading, redaction, prompt compilation, provider call, validation, and retry-on-validation failure.

## `uss evidence-map`

```bash
uss evidence-map examples/summary_with_evidence.md examples/thread_minimal.json --json
uss evidence-map examples/summary_with_evidence.md examples/thread_minimal.json --output evidence_map.json
```

Builds a deterministic map from summary claims to source-thread message anchors.

## `uss inspect`

```bash
uss inspect examples/checkpoint_valid.md
uss inspect examples/summary_with_evidence.md --thread examples/thread_minimal.json --output inspection_report.json
```

Runs structural validation, optional evidence anchoring, evidence validation, scoring, and MVP-readiness reporting.

---

## v1.0 Full Run Command

```bash
uss run <thread_path> --provider static --mode checkpoint --output-dir output/
```

### Required Output Contract

```text
output/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

### Provider Options

```text
static
openai
anthropic
ollama
```

Static mode is deterministic and requires no network access.
