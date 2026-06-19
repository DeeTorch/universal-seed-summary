# USS Engine v0.4 Release Notes

## Mission

Add evidence anchoring and artifact inspection so the USS principle "thread-derived only" becomes measurable instead of merely declared.

## New modules

```text
src/uss_engine/evidence.py
src/uss_engine/inspector.py
src/uss_engine/scoring.py
```

## New tests

```text
tests/test_evidence.py
tests/test_inspector.py
```

## New examples and schemas

```text
examples/summary_with_evidence.md
schemas/evidence_map.schema.json
schemas/artifact_inspection.schema.json
docs/evidence_anchoring.md
```

## New CLI commands

```bash
uss evidence-map examples/summary_with_evidence.md examples/thread_minimal.json --json
uss inspect examples/summary_with_evidence.md --thread examples/thread_minimal.json --json
```

## Runtime prompt compiler change

The runtime compiler now tells the model to keep claims tightly grounded and optionally include `[evidence: msg_0001]` source hints when helpful.

## Validation status

The v0.4 test suite passes with 27 tests.
