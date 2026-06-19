# USS Engine v1.1 — Provider Setup

USS Engine supports these provider modes:

```text
static
openai
anthropic
gemini
grok
xai
ollama
```

## Static Provider

Static mode is deterministic, network-free, and suitable for CI, local smoke tests, and artifact contract verification.

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/static
```

Static mode proves the pipeline shape:

```text
thread → redaction → prompt compiler → candidate artifact → validator → evidence map → inspector → reports
```

It does not prove live model quality.

## API Key Setup

Copy the example file:

```bash
cp .env.example .env
```

Fill only the providers you intend to use. Then verify without printing secrets:

```bash
uss provider-status --env-file .env
```

## OpenAI / ChatGPT Enterprise API Platform

Set:

```bash
OPENAI_API_KEY=your-key-here
```

Run:

```bash
uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-5.5 \
  --mode checkpoint \
  --output-dir output/openai \
  --env-file .env
```

Optional OpenAI-compatible gateway:

```bash
OPENAI_BASE_URL=https://your-compatible-gateway.example/v1
```

For regulated or enterprise environments, use the endpoint approved by your admin.

## Anthropic Provider

Set:

```bash
ANTHROPIC_API_KEY=your-key-here
```

Run:

```bash
uss run examples/thread_minimal.json \
  --provider anthropic \
  --model claude-sonnet-4-5 \
  --mode checkpoint \
  --output-dir output/anthropic \
  --env-file .env
```

## Gemini Provider

Set one of:

```bash
GEMINI_API_KEY=your-key-here
# or
GOOGLE_API_KEY=your-key-here
```

Run:

```bash
uss run examples/thread_minimal.json \
  --provider gemini \
  --model gemini-3.5-flash \
  --mode checkpoint \
  --output-dir output/gemini \
  --env-file .env
```

Optional custom base URL:

```bash
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta
```

## Grok / xAI Provider

Set:

```bash
XAI_API_KEY=your-key-here
```

Run:

```bash
uss run examples/thread_minimal.json \
  --provider grok \
  --model grok-4.3 \
  --mode checkpoint \
  --output-dir output/grok \
  --env-file .env
```

Alias:

```bash
--provider xai
```

Optional custom base URL:

```bash
XAI_BASE_URL=https://api.x.ai/v1
```

## Ollama Provider

Start Ollama and pull a model:

```bash
ollama serve
ollama pull llama3.2
```

Run:

```bash
uss run examples/thread_minimal.json \
  --provider ollama \
  --model llama3.2 \
  --mode checkpoint \
  --output-dir output/ollama
```

Optional remote/local server override:

```bash
OLLAMA_BASE_URL=http://localhost:11434
```

Optional bearer token for secured endpoints:

```bash
OLLAMA_API_KEY=your-token-here
```

## Provider Trust Boundaries

- Redaction runs before prompt compilation by default.
- Generation reports intentionally avoid storing raw prompts.
- Static mode proves orchestration but not live provider behavior.
- Hosted providers may still receive redacted source thread content; do not send material that your operational policy forbids sharing with that provider.
- Do not commit `.env`.

## Recommended Provider Test Order

1. `provider-status` for key visibility.
2. `static` for deterministic local proof.
3. `ollama` for local live-model proof.
4. `openai`, `gemini`, `grok`, or `anthropic` for hosted model proof.
5. Compare outputs with `uss inspect` and the generated inspection scores.
