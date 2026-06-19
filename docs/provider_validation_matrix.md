# Provider Validation Matrix

This matrix records the current release validation state for USS Engine providers. Pending providers require local credentials or services and should not be marked validated until smoke and checkpoint runs both pass.

| Provider | Model | Smoke Test | Checkpoint Run | Inspection Score | Unsupported Claims | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| static | N/A | passing | passing | 98.91 A or latest local proof | 0 | validated | deterministic local proof |
| gemini | gemini-2.5-flash | passing | passing | 96.69 A | 0 | validated | live provider proof after v1.1.1 calibration |
| openai | TBD | not tested | not tested | TBD | TBD | pending | requires API key |
| anthropic | TBD | not tested | not tested | TBD | TBD | pending | requires API key |
| grok/xai | TBD | not tested | not tested | TBD | TBD | pending | requires XAI_API_KEY |
| ollama | TBD | not tested | not tested | TBD | TBD | pending | requires local Ollama server |

## Validation Rules

- Do not commit provider keys or local `.env` files.
- Record only summary validation results, not raw private transcripts or secrets.
- A provider is validated only after both smoke and checkpoint runs pass.
- Keep provider-specific failures as release notes or issues unless the fix is verified and minimal.
