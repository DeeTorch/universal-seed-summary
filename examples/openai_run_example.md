# OpenAI-Compatible Run Example

This example shows the hosted-provider path for USS Engine v1.0.

## Setup

```bash
export OPENAI_API_KEY="your-key-here"
```

Optional custom gateway:

```bash
export OPENAI_BASE_URL="https://your-compatible-gateway.example/v1"
```

## Run

```bash
uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-4.1-mini \
  --mode checkpoint \
  --output-dir output/openai-checkpoint
```

## Inspect Outputs

```bash
cat output/openai-checkpoint/generation_report.json
cat output/openai-checkpoint/validation_report.json
```

Expected files:

```text
output/openai-checkpoint/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## Notes

- Redaction runs before prompt compilation unless `--no-redaction` is explicitly used.
- Provider output quality may vary by model.
- Use `--max-attempts` to allow validation/repair loops.
