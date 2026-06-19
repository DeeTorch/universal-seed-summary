# USS Engine 5-Minute Quickstart

This guide gets a new local checkout running with the deterministic static provider first, then shows how to run one live provider using a local `.env` file.

## Windows PowerShell

```powershell
git clone https://github.com/DeeTorch/universal-seed-summary.git
cd universal-seed-summary
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pytest -q
uss run examples/thread_minimal.json --provider static --mode checkpoint --output-dir output/static-checkpoint
Copy-Item .env.example .env
```

Edit `.env` locally and add only the provider key you intend to test. Do not commit `.env`.

```powershell
# Example: Gemini
uss provider-status --env-file .env
uss provider-smoke --provider gemini --model gemini-2.5-flash --env-file .env
uss run examples/thread_minimal.json --provider gemini --model gemini-2.5-flash --mode checkpoint --output-dir output/gemini-checkpoint --env-file .env
Get-ChildItem output
```

## macOS or Linux

```bash
git clone https://github.com/DeeTorch/universal-seed-summary.git
cd universal-seed-summary
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pytest -q
uss run examples/thread_minimal.json --provider static --mode checkpoint --output-dir output/static-checkpoint
cp .env.example .env
```

Edit `.env` locally and add only the provider key you intend to test. Do not commit `.env`.

```bash
# Example: Gemini
uss provider-status --env-file .env
uss provider-smoke --provider gemini --model gemini-2.5-flash --env-file .env
uss run examples/thread_minimal.json --provider gemini --model gemini-2.5-flash --mode checkpoint --output-dir output/gemini-checkpoint --env-file .env
ls -la output
```

## What To Inspect

- Confirm tests pass before live provider work.
- Confirm static checkpoint artifacts are generated under `output/`.
- Confirm provider smoke test passes before a live checkpoint run.
- Inspect generated reports for inspection score, unsupported claims, and evidence validation.
- Keep `output/` local unless you intentionally promote sanitized examples.
