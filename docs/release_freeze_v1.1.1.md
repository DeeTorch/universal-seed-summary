# USS Engine v1.1.1 Release Freeze

USS Engine v1.1.1 is the first stabilized post-MVP release. It should be treated as the clean baseline before any v1.2 architecture or feature expansion begins.

## Context

USS Engine v1.1 introduced provider activation and enterprise API key handling. This made live provider runs possible while keeping provider credentials outside the repository through local environment variables.

USS Engine v1.1.1 calibrated evidence scoring after a live Gemini checkpoint run. The calibration separates metadata, system, protocol-null, and protocol-assessment fields from unsupported factual claims. The verified Gemini checkpoint improved from `91.13 / B` with `3 unsupported claims` to `96.69 / A` with `0 unsupported claims`, `evidence_validation.valid: true`, and `mvp_ready: true`.

This release is a freeze point. Do not add new architecture, provider clients, or v1.2 feature work until provider validation and adoption documentation are complete.

## Freeze Checklist

- main is synced with origin/main
- pytest passes
- package version reports 1.1.1
- .env is ignored
- provider smoke test works for at least Gemini or static
- release tag exists or is ready to create
- GitHub Release notes are ready
- v1.2 roadmap issues are created or drafted

## Release Discipline

- Preserve the current provider behavior unless a verified bug requires a minimal fix.
- Keep local provider keys, `.env`, `.venv/`, `output/`, caches, and generated local artifacts out of Git.
- Prefer documentation, validation proof, and security hardening over new engine behavior.
- Use this release as the baseline for v1.2 planning.
