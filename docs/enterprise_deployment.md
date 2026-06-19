# USS Engine Enterprise Deployment Notes

USS Engine should be deployed local-first or inside the enterprise boundary that owns the transcript data.

## Recommended enterprise topology

```text
User workstation / secure runner
  -> USS Engine CLI
  -> Redaction layer
  -> Provider adapter
  -> Enterprise API gateway or approved provider endpoint
  -> USS output artifacts
  -> Internal archive store
```

## OpenAI / ChatGPT Enterprise distinction

USS Engine does not automate the ChatGPT web UI. It connects to the OpenAI API Platform using API credentials and provider endpoints. Enterprise ChatGPT workspaces and API Platform access may have separate administrative controls, billing, compliance boundaries, and endpoint requirements.

## Gemini enterprise path

For Gemini, use Google-approved API credentials and route through the Gemini API endpoint or your enterprise gateway. For Google Cloud / Vertex AI migration, add a dedicated Vertex adapter rather than overloading the Gemini API-key adapter.

## Grok enterprise path

For Grok, use xAI API keys or enterprise-approved xAI routing. `XAI_BASE_URL` allows an internal proxy or gateway to replace the public base URL.

## Controls to enforce

- `.env` excluded from Git
- CI secrets injected only at runtime
- separate staging and production provider projects
- spend/rate limits at provider dashboard or gateway
- artifact retention policy
- redaction enabled by default
- no raw provider prompts stored in generation reports

## Do not do this

- do not paste secrets into USS transcripts
- do not commit `.env`
- do not run confidential transcripts through personal provider accounts
- do not disable redaction for production unless formally approved
