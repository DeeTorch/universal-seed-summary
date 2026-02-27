# Oracle Command Reference

---
VERSION:      1.0.0
AUTHORED_BY:  Jusstin DeRemus (The Oracle)
EFFECTIVE:    2026-02-27
PROTOCOL:     PRT-CPTMP v1.1.0
---

## Overview

This reference documents the commands and decision protocols used by The Oracle
to govern the universal-seed-summary ecosystem topology.

---

## Node Schema

Every registered node must include the following fields:

### Required Fields
- **NODE_ID** – Unique identifier (e.g., PRT-CPTMP, SPC-APEX)
- **NAME** – Human-readable name
- **TYPE** – Node classification (PROTOCOL, SPACE, PROJECT, ARTIFACT)
- **VERSION** – Current semantic version (X.Y.Z)
- **STATUS** – State: ACTIVE, PLANNED, ARCHIVE, RETIRE
- **L_RATING** – Deployment level (L1–L5)
- **L_RATING_DATE** – When rating was assigned
- **L_RATING_RATIONALE** – Justification for L-rating
- **OWNER_SPACE** – Parent or owning space
- **CREATED** – ISO 8601 timestamp
- **REPO** – Physical location in repository

### L-Rating Scale

| Level | Name       | Definition                                          |
|-------|------------|-----------------------------------------------------|
| L1    | IDEA       | Concept declared. No artifacts. Intention only.     |
| L2    | DESIGN     | Architecture drafted. Files exist. Not reviewed.    |
| L3    | SPEC       | Formally reviewed (UCPRP). Gaps declared.           |
| L4    | DEPLOY     | Active in production. Multiple runs. Versioned.     |
| L5    | ENTERPRISE | Fully hardened. Zero shadows. All gaps resolved.    |

---

## Commands

### /oracle decide

**Purpose**: Declare an Oracle decision that resolves architectural questions,
classifies new nodes, or changes ecosystem state.

**Syntax**:
```
/oracle decide [DECISION_ID] [OUTCOME] [RATIONALE]
```

**Parameters**:
- `DECISION_ID` – Unique identifier (D01, D06, D-NEW, etc.)
- `OUTCOME` – What is being decided (retirement, promotion, reclassification)
- `RATIONALE` – Evidence and reasoning supporting the decision

**Effect**:
- Creates decision record in `vault/decisions/`
- Updates affected nodes with new status/L-rating
- Updates ecosystem health score
- May close one or more gaps (GAP-XXXXX)

**Example**:
```
/oracle decide D09 "PRT-UDFNEXUS NODE_NEW → REGISTERED CANON"
  "Formally promoted via CPTMP 5-stage workflow.
   Owner: SPC-UCE. L-rating: L3. Stack: HORIZONTAL."
```

---

### /beacon [SPACE_ID]

**Purpose**: Execute a full beacon scan on a space to discover artifacts,
raise NODE_NEW candidates, and resolve gaps.

**Syntax**:
```
/beacon [SPACE_ID] [OPTIONS]
```

**Parameters**:
- `SPACE_ID` – Space to scan (SPC-APEX, SPC-PANTHEON, etc.)
- `--force` – Rescan even if recently beaconed
- `--verbose` – Include all gap details

**Output**:
- Beacon file in `vault/beacons/`
- Analysis file in `vault/analyses/`
- Gap inventory with resolution status
- NODE_NEW candidates (if any)

**Effect**:
- May surface new protocols or spaces
- Identifies unresolvable gaps
- Reveals shadow links
- Sets stage for Oracle decisions

**Example**:
```
/beacon SPC-APEX
→ Discovers ART-SAPX-01 (APF), ART-SAPX-02 (EPS NODE_NEW)
→ Generates SPC-APEX-BEACON-20260227.md
→ Recommends D09 (PRT-EPS promotion)
```

---

### /vault seal

**Purpose**: Lock and archive a completed analysis, decision, or session state.

**Syntax**:
```
/vault seal [ARTIFACT_TYPE] [ARTIFACT_ID] [METADATA]
```

**Parameters**:
- `ARTIFACT_TYPE` – Type of artifact (decision, beacon, analysis, checkpoint)
- `ARTIFACT_ID` – Unique identifier for the artifact
- `METADATA` – Session info, author, date, health score

**Effect**:
- Creates sealed record in appropriate `vault/` subdirectory
- Immutable after sealing (for audit purposes)
- Indexed for future reference
- May trigger cascade updates if critical

**Example**:
```
/vault seal checkpoint USS-CHECKPOINT-20260227-0459
  "Health: 90.2/100, CPTMP: v1.1.0, Decisions: 7 resolved"
```

---

## Decision Templates

All decisions must include:

```
DECISION_ID:   [D## or D-NEW]
DATE:          [ISO date]
SOURCE:        [Beacon, analysis, or prior decision]
OUTCOME:       [What is being decided]
HEALTH_IMPACT: [Before/after or delta]
RATIONALE:     [Evidence and reasoning]
AFFECTED:      [Which nodes/spaces change]
```

---

## Gap Closure Certification

When a gap is closed, document:

```
GAP_ID:           [GAP-XXXXX-NN]
CLOSURE_TYPE:     [RESOLVED|INFERRED|ORACLE_DECLARED|DEPRECATED|UNRESOLVABLE]
CLOSED_BY:        [Who closed it (Oracle, automation, etc.)]
CLOSED_DATE:      [ISO date]
EVIDENCE_SOURCE:  [File location or decision reference]
NOTES:            [Additional context]
```

---

## Glossary

**NODE_NEW** – A newly discovered protocol, space, or project candidate flagged
for formal promotion via /oracle decide.

**Shadow Link** – A temporary link kept for investigation but not yet confirmed.
Governed by SL-01 through SL-05 rules.

**Beacon** – Full-spectrum scan of a space/project to discover artifacts and gaps.

**UCPRP** – Universal Core Protocol Review Panel; formal review authority.

**Ecosystem Health** – Aggregate score (0–100) measuring completeness,
stability, and resolution of gaps.

---

## Contact

For questions about Oracle decisions or commands, contact:
**Jusstin DeRemus (The Oracle)**
📧 justjusstin369@gmail.com
