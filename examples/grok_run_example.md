# Grok / xAI USS Run Example

```bash
cp .env.example .env
# Add XAI_API_KEY to .env

uss provider-status --env-file .env
uss provider-smoke --provider grok --model grok-4.3 --env-file .env

uss run examples/thread_minimal.json \
  --provider grok \
  --model grok-4.3 \
  --mode checkpoint \
  --output-dir output/grok_checkpoint \
  --env-file .env \
  --fail-on-invalid
```
