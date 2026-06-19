# USS Engine v0.4 Product Definition

## Product identity

USS Engine is a local-first continuity engine that converts AI conversation transcripts into validated, audit-safe, reusable Universal Seed Summary artifacts.

## v0.4 mission

Make **thread-derived only** measurable by adding deterministic evidence anchoring and artifact inspection.

## MVP definition

100% MVP means the tool can:

1. Ingest raw or JSON transcript input.
2. Normalize it into a canonical thread object.
3. Redact secrets and selected PII before generation.
4. Compile the USS v1.3 protocol into a runtime prompt.
5. Generate a USS Markdown artifact through a provider adapter.
6. Validate required structure and failure semantics.
7. Map generated claims back to source-thread messages.
8. Inspect score, risk, support coverage, and MVP readiness.
9. Export Markdown plus JSON reports.

## v0.4 status

v0.4 completes item 7 and adds item 8 in local deterministic form. Live provider execution proof was added in v0.5 through static E2E and provider contracts; v1.0 completes release packaging and MVP documentation.

## Non-goals for v0.4

- No embedding model dependency.
- No external database.
- No required cloud provider.
- No claim that lexical matching is semantic proof.
- No browser scraping.

## Acceptance criteria

- Evidence map schema exists.
- Inspector schema exists.
- `uss evidence-map` command exists.
- `uss inspect` command exists.
- Claims can be extracted from USS fields.
- Explicit `[evidence: msg_id]` references are validated against source thread.
- Unsupported claims are measurable.
- Tests pass.

---

## v0.5/v1.0 MVP Delta

v0.5 upgrades the engine from individual components into one executable MVP loop. The new `uss run` command writes the canonical six-artifact output bundle: summary, validation report, redaction report, evidence map, inspection report, and generation report.

The product is now suitable for local smoke tests, CI validation, provider adapter testing, and repository handoff. Live provider execution requires configured API credentials or a local Ollama server.


## v1.0 Release Definition

v1.0 completes MVP release polish. The product now includes install documentation, provider setup documentation, a formal MVP acceptance checklist, changelog, license file, provider examples, version metadata, and a refreshed static E2E proof bundle.
