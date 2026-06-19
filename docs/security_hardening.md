# Security Hardening

USS Engine can run against live providers, so local credentials and private transcripts must stay outside the repository.

## Current Rules

- Never commit `.env`.
- Never commit provider API keys.
- Keep `.venv/`, `output/`, caches, and generated local provider outputs out of Git.
- Rotate keys immediately if they are exposed in logs, screenshots, commits, or shared artifacts.
- Use environment variables or secret managers for provider credentials.
- Avoid uploading raw private transcripts to public repositories.
- Treat redaction as a safety layer, not a guarantee.

## Recommended Future Tools

- `pre-commit` for local checks before commit.
- `detect-secrets` or an equivalent scanner for credential detection.
- GitHub secret scanning for remote repository protection.
- Local output deny rules to block accidental commits from `output/` and provider artifact folders.

## Release Practice

- Validate ignore rules before release tagging.
- Store only sanitized examples in the repository.
- Prefer summary validation results over raw provider responses.
- If a secret is suspected to be committed, rotate the key first, then remove it from Git history with a deliberate remediation plan.
