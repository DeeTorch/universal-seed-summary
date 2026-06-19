# USS Engine v0.4 Evidence Anchoring

USS Engine v0.4 makes the USS v1.3 rule **thread-derived only** measurable.
The engine now parses generated USS Markdown artifacts into evidence-checkable claims and attempts to anchor each claim to source message IDs from the normalized thread.

## Why this matters

The USS protocol already requires that summary output remain strictly derived from the thread, declare uncertainty, and avoid external assumptions. The v0.4 evidence layer turns that principle into an inspectable data structure:

```text
summary field -> extracted claim -> source message anchor -> support status -> score
```

## Evidence statuses

| Status | Meaning |
|---|---|
| `supported` | The claim has an explicit message reference or strong deterministic lexical match. |
| `weakly_supported` | The claim has a weak lexical match and should be reviewed. |
| `unsupported` | The claim was not anchored to the supplied thread. |
| `absent_claim` | The claim is a declared absence/null state, such as "None detected within thread bounds." |

## Evidence syntax

Generated summaries may include optional inline source hints:

```markdown
**Architecture_Commits**:
- Build a validator-backed USS Engine. [evidence: msg_002]
```

The inspector validates that referenced IDs exist in the normalized source thread.

## Commands

Build an evidence map:

```bash
uss evidence-map examples/summary_with_evidence.md examples/thread_minimal.json --output evidence_map.json
```

Inspect a summary with source-thread anchoring:

```bash
uss inspect examples/summary_with_evidence.md --thread examples/thread_minimal.json --output inspection_report.json
```

Inspect structure only:

```bash
uss inspect examples/checkpoint_valid.md
```

## Current limitations

The deterministic anchorer is not a semantic proof engine. It combines explicit message references with lexical overlap. That means it is strict, reproducible, and local-first, but it may under-score valid paraphrases. Future versions can add embeddings, retrieval, or an LLM evidence judge while preserving this baseline.
