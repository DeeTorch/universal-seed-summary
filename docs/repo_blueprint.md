# USS Engine v0.4 Repository Blueprint

```text
uss-engine/
├── README.md
├── pyproject.toml
├── protocols/
│   └── uss_v1_3.protocol.json
├── schemas/
│   ├── uss_summary.schema.json
│   ├── normalized_thread.schema.json
│   ├── redaction_report.schema.json
│   ├── evidence_map.schema.json
│   └── artifact_inspection.schema.json
├── src/
│   └── uss_engine/
│       ├── schema.py
│       ├── validator.py
│       ├── transcript.py
│       ├── prompt_compiler.py
│       ├── generator.py
│       ├── redactor.py
│       ├── evidence.py
│       ├── inspector.py
│       ├── scoring.py
│       ├── cli.py
│       └── clients/
│           ├── base.py
│           ├── openai_client.py
│           ├── anthropic_client.py
│           └── ollama_client.py
├── examples/
│   ├── thread_minimal.json
│   ├── thread_with_secrets.json
│   ├── checkpoint_valid.md
│   ├── archive_valid.md
│   ├── invalid_missing_failure_semantics.md
│   └── summary_with_evidence.md
├── tests/
│   ├── test_validator.py
│   ├── test_transcript.py
│   ├── test_prompt_compiler.py
│   ├── test_generator.py
│   ├── test_redactor.py
│   ├── test_clients_static_contract.py
│   ├── test_evidence.py
│   └── test_inspector.py
└── docs/
    ├── product_definition.md
    ├── repo_blueprint.md
    ├── cli_contract.md
    ├── evidence_anchoring.md
    ├── release_notes_v0.3.md
    └── release_notes_v0.4.md
```

## Layer responsibilities

- `schema.py`: Pydantic validation spine for USS artifact structure.
- `validator.py`: Markdown/YAML structural validator.
- `transcript.py`: Transcript normalization into `NormalizedThread`.
- `redactor.py`: Local-first pre-generation redaction.
- `prompt_compiler.py`: Protocol-to-runtime prompt compiler.
- `generator.py`: Provider-agnostic generation and repair loop.
- `clients/`: Provider adapters behind a shared `LLMClient` contract.
- `evidence.py`: Claim extraction and source-message anchoring.
- `inspector.py`: Full artifact inspection bundle.
- `scoring.py`: MVP-readiness scoring.

---

## v0.5/v1.0 Additions

```text
src/uss_engine/run.py          # Full E2E orchestration
src/uss_engine/reports.py      # Generation run report models/writers
tests/test_e2e_static.py       # Static E2E proof
docs/e2e_generation.md         # End-to-end execution guide
schemas/generation_run_report.schema.json
.github/workflows/tests.yml
examples/e2e_output/           # Proof output bundle
```


## v1.0 Release Files

```text
CHANGELOG.md
LICENSE
docs/install.md
docs/provider_setup.md
docs/v1_mvp_acceptance.md
docs/release_notes_v1.0.md
examples/openai_run_example.md
examples/ollama_local_run_example.md
```

These files make the repository release-ready without changing the core runtime architecture.
