# Release Notes — USS Engine v0.5

## Mission

Prove the full MVP execution loop:

```text
transcript → redaction → runtime prompt → provider → summary → validation → evidence → inspection → reports
```

## Added

- `src/uss_engine/run.py`
- `src/uss_engine/reports.py`
- `tests/test_e2e_static.py`
- Expanded provider contract tests in `tests/test_clients_static_contract.py`
- `examples/e2e_output/` with all six expected output artifacts
- `docs/e2e_generation.md`
- `.github/workflows/tests.yml`

## CLI

New command:

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/
```

## Output Artifacts

```text
summary.md
validation_report.json
redaction_report.json
evidence_map.json
inspection_report.json
generation_report.json
```

## Test Result

```text
33 passed
```

## Status

v0.5 reaches approximately 95% MVP completion. The remaining work for v1.0 is release polish: packaging cleanup, final README pass, install instructions, expanded examples, and tagged release preparation.
