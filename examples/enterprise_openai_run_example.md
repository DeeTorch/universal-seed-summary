# Enterprise OpenAI / ChatGPT Enterprise API Platform Run Example

USS Engine connects through the OpenAI API Platform, not by controlling the ChatGPT web app.

```bash
cp .env.example .env
# Add OPENAI_API_KEY to .env
# Optional: set OPENAI_BASE_URL to an approved enterprise/gateway endpoint.

uss provider-status --env-file .env
uss provider-smoke --provider openai --model gpt-5.5 --env-file .env

uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-5.5 \
  --mode checkpoint \
  --output-dir output/enterprise_openai_checkpoint \
  --env-file .env \
  --fail-on-invalid
```

For FedRAMP or regulated enterprise deployments, use the endpoint and model set approved by the workspace administrator.
