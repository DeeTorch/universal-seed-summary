# Release Notes — USS Engine v1.0

USS Engine v1.0 is the first MVP-complete release.

## Release Focus

No new architecture was added in v1.0. This release hardens the package for real use:

- Install path.
- Provider setup path.
- License.
- Changelog.
- MVP acceptance checklist.
- Example provider run guides.
- Version metadata.
- Refreshed static E2E proof bundle.

## MVP Definition

The MVP is complete when the engine can run:

```bash
uss run examples/thread_minimal.json \
  --provider static \
  --mode checkpoint \
  --output-dir output/
```

And write:

```text
summary.md
validation_report.json
redaction_report.json
evidence_map.json
inspection_report.json
generation_report.json
```

## Remaining Post-MVP Opportunities

- Semantic entailment scoring beyond source-ID evidence anchoring.
- More robust provider retry strategies.
- Browser/export ingestion.
- SQLite or Obsidian archive storage.
- Web dashboard.
- Release publishing automation.
