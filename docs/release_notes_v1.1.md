# USS Engine v1.1 Release Notes

## Theme

Provider activation and enterprise-safe API key handling.

## Added

- `.env.example`
- `src/uss_engine/config.py`
- `src/uss_engine/clients/gemini_client.py`
- `src/uss_engine/clients/grok_client.py`
- `uss provider-status`
- `uss provider-smoke`
- `--env-file` support for `uss generate` and `uss run`
- Gemini provider support
- Grok / xAI provider support
- enterprise deployment notes
- live provider validation guide

## Security posture

- secrets are read from environment variables or `.env`
- key status command never prints secret values
- redaction remains enabled by default
- generation reports exclude raw prompts

## Test result

38 tests passing.
