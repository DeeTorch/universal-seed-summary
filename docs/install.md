# USS Engine v1.0 — Install Guide

USS Engine is designed to run local-first. Use an isolated Python environment instead of installing into global site-packages.

## Requirements

```text
Python 3.11+
pip
```

## Recommended Setup

From the repository root:

```bash
python -m venv .venv
```

Activate the environment.

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install in editable development mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Verify:

```bash
uss --help
pytest -q
```

## Smoke Test

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/smoke
```

Expected files:

```text
output/smoke/
├── summary.md
├── validation_report.json
├── redaction_report.json
├── evidence_map.json
├── inspection_report.json
└── generation_report.json
```

## Clean Reinstall

```bash
python -m pip uninstall -y uss-engine
python -m pip install -e .[dev]
```

## Notes

- Static mode requires no network access.
- Hosted provider modes require API keys.
- Ollama mode requires a running local or remote Ollama-compatible server.
