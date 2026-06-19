# Ollama Local Run Example

This example shows the local-provider path for USS Engine v1.0.

## Setup

Start Ollama:

```bash
ollama serve
```

Pull a model:

```bash
ollama pull llama3.2
```

## Run

```bash
uss run examples/thread_minimal.json \
  --provider ollama \
  --model llama3.2 \
  --mode checkpoint \
  --output-dir output/ollama-checkpoint
```

## Custom Ollama URL

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
```

Then rerun the command.

## Inspect Outputs

```bash
cat output/ollama-checkpoint/generation_report.json
cat output/ollama-checkpoint/inspection_report.json
```

Expected files:

```text
output/ollama-checkpoint/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## Notes

- Ollama keeps inference local when run on your own machine.
- Model size and context window affect artifact quality.
- Use static mode first to verify the pipeline before testing local generation.
