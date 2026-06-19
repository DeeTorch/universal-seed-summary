# USS Engine v1.1 API Key Activation

USS Engine v1.1 adds safe provider activation for local and enterprise-style execution.

## Security rule

Do not paste API keys into prompts, source files, README examples, issue comments, screenshots, or generated USS artifacts.

Use one of these instead:

1. environment variables
2. a local `.env` file excluded from Git
3. your enterprise secret manager
4. CI/CD encrypted secrets

## Local `.env` setup

```bash
cp .env.example .env
```

Fill only the providers you intend to use.

Then check status without printing secrets:

```bash
uss provider-status --env-file .env
```

## Provider smoke tests

```bash
uss provider-smoke --provider openai --model gpt-5.5 --env-file .env
uss provider-smoke --provider gemini --model gemini-3.5-flash --env-file .env
uss provider-smoke --provider grok --model grok-4.3 --env-file .env
uss provider-smoke --provider ollama --model llama3.2 --env-file .env
```

## Full USS run with live provider

```bash
uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-5.5 \
  --mode checkpoint \
  --output-dir output/openai_checkpoint \
  --env-file .env
```

```bash
uss run examples/thread_minimal.json \
  --provider gemini \
  --model gemini-3.5-flash \
  --mode checkpoint \
  --output-dir output/gemini_checkpoint \
  --env-file .env
```

```bash
uss run examples/thread_minimal.json \
  --provider grok \
  --model grok-4.3 \
  --mode checkpoint \
  --output-dir output/grok_checkpoint \
  --env-file .env
```

## Output contract

Every provider run writes:

```text
summary.md
validation_report.json
redaction_report.json
evidence_map.json
inspection_report.json
generation_report.json
```

## Provider variables

| Provider | Required variable | Optional base URL |
|---|---|---|
| OpenAI / ChatGPT Enterprise API Platform | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |
| Anthropic | `ANTHROPIC_API_KEY` | `ANTHROPIC_BASE_URL` |
| Gemini | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `GEMINI_BASE_URL` |
| Grok / xAI | `XAI_API_KEY` | `XAI_BASE_URL` |
| Ollama | none for local default | `OLLAMA_BASE_URL` |

## Enterprise note

For enterprise usage, do not share one personal API key across operators. Use project-scoped keys, service accounts, gateways, or secret-manager injected environment variables.
