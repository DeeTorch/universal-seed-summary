# Release Process

Use this process for tagged USS Engine releases.

## v1.1.1 Tag

```powershell
git switch main
git pull origin main
python -m pytest -q
python -c "import uss_engine; print(uss_engine.__version__)"
git tag v1.1.1
git push origin v1.1.1
```

## GitHub Release

Title:

```text
USS Engine v1.1.1 — Evidence Classifier Calibration
```

Summary:

```text
Stabilizes evidence scoring after live Gemini validation. Metadata, system, protocol-null, and protocol-assessment fields are now classified separately from unsupported factual claims.
```

## Pre-Release Checks

- `main` is synced with `origin/main`.
- Tests pass.
- Package version matches the tag.
- `.env`, `.venv/`, `output/`, caches, and generated local outputs are ignored.
- Provider validation matrix is updated.
- Release notes are ready.
