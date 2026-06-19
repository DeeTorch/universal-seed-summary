# USS Engine v0.3 Release Notes

## Release Theme

Security boundary + provider adapter boundary.

## Added

- `redactor.py` with default rules for emails, phone numbers, API keys, bearer tokens, GitHub tokens, AWS access key IDs, private key blocks, URL credentials, and generic secret assignments.
- `clients/base.py` with `LLMClient`, `StaticLLMClient`, and `ClientConfig`.
- `clients/openai_client.py` for OpenAI-compatible chat completions.
- `clients/anthropic_client.py` for Anthropic Messages API.
- `clients/ollama_client.py` for Ollama `/api/chat`.
- `examples/thread_with_secrets.json`.
- Redaction report schema.
- CLI `redact` command.
- Provider-aware `generate` command.

## Changed

- Generator now redacts before prompt compilation by default.
- Prompt compiler accepts and embeds a redaction report.
- Generation result now includes `redaction_report`.
- CLI help/version framing updated to v0.3.

## Tests

- 20 passing tests.
- Existing validator, transcript, prompt compiler, and generator tests preserved.
- New redaction tests added.
- New client contract tests added.

## Known Limits

- Redaction is pattern-based, not a perfect data-loss-prevention system.
- Provider adapters are intentionally minimal and synchronous.
- Streaming generation is not implemented.
- Evidence anchoring is not implemented yet.
