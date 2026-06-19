# Gemini USS Run Example

```bash
cp .env.example .env
# Add GEMINI_API_KEY to .env

uss provider-status --env-file .env
uss provider-smoke --provider gemini --model gemini-3.5-flash --env-file .env

uss run examples/thread_minimal.json \
  --provider gemini \
  --model gemini-3.5-flash \
  --mode checkpoint \
  --output-dir output/gemini_checkpoint \
  --env-file .env \
  --fail-on-invalid
```
