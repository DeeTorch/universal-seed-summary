# Repository Guidelines

## Project Structure & Module Organization

USS Engine is a Python package under `src/uss_engine/`. Core modules handle transcript normalization, redaction, prompt compilation, generation, validation, evidence mapping, inspection, scoring, reports, provider config, and the Typer CLI. Provider adapters live in `src/uss_engine/clients/`. Tests are in `tests/`, protocol files in `protocols/`, JSON schemas in `schemas/`, examples in `examples/`, and maintainer/user docs in `docs/`. GitHub Actions config is under `.github/workflows/`.

## Build, Test, and Development Commands

Use Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pytest -q
python -c "import uss_engine; print(uss_engine.__version__)"
uss run examples/thread_minimal.json --provider static --mode checkpoint --output-dir output/static
```

`pytest` runs the full test suite. `uss run` exercises the end-to-end static pipeline without network access.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints, and small functions with explicit data models. Runtime contracts are Pydantic models and dataclasses. Keep provider-specific logic inside `src/uss_engine/clients/`; the engine core should depend on the shared `LLMClient` protocol. Ruff is configured with a 100-character line length for `src` and `tests`.

## Testing Guidelines

Tests use `pytest` and are discovered from `tests/`. Name test files `test_*.py` and keep tests deterministic by preferring the static provider. Add regression tests for validation, evidence scoring, redaction, and generated report contracts when changing those areas.

## Commit & Pull Request Guidelines

Recent commits use short imperative messages, for example `Add v1.2 GitHub issue drafts` or `Freeze USS Engine v1.1.1 release baseline`. PRs should state scope, list tests run, link relevant issues, and call out any provider, security, or artifact-contract impact.

## Security & Configuration Tips

Never commit `.env`, `.venv/`, `output/`, caches, generated local provider outputs, or API keys. Do not print or inspect secret values. Use `.env.example` for documented key names only. Redaction is a safety layer, not permission to upload private transcripts.

## Agent-Specific Instructions

Do not move published tags or change package version unless explicitly requested. Do not implement v1.2 features during planning/documentation tasks. Preserve provider behavior unless fixing a verified bug with tests.
