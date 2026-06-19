# Live Provider Validation

This document defines the v1.1 live provider validation flow.

## 1. Confirm key visibility

```bash
uss provider-status --env-file .env
```

Expected: selected provider shows `configured` without printing the key value.

## 2. Smoke-test routing

```bash
uss provider-smoke --provider openai --model gpt-5.5 --env-file .env
```

Expected: provider returns a short response and command exits zero.

## 3. Run full checkpoint

```bash
uss run examples/thread_minimal.json \
  --provider openai \
  --model gpt-5.5 \
  --mode checkpoint \
  --output-dir output/live_openai_checkpoint \
  --env-file .env \
  --fail-on-invalid
```

## 4. Inspect the result

```bash
uss inspect output/live_openai_checkpoint/summary.md \
  --thread examples/thread_minimal.json \
  --output output/live_openai_checkpoint/inspection_report.json
```

## 5. Acceptance criteria

A live provider run is accepted when:

- `generation_report.json.status` is `completed` or `completed_with_warnings`
- `generation_report.json.valid` is `true`
- `validation_report.json.valid` is `true`
- `inspection_report.json.score.mvp_ready` is `true`
- redaction was enabled unless a specific exception was approved

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Missing API key | env variable not loaded | check `.env`, shell session, or secret manager |
| HTTP 401/403 | invalid key or forbidden model | verify dashboard access and model name |
| HTTP 404 | wrong base URL or model | check provider docs and `*_BASE_URL` |
| Validation failed | model output drifted | increase attempts or use repair loop |
| Evidence support low | summary omitted evidence hints | re-run or adjust prompt compiler evidence guidance |
