# Cross-Project Topology Mapping Protocol

---
PROTOCOL_ID:       PRT-CPTMP
PROTOCOL_VERSION:  v1.1.0
PRIOR_VERSION:     v1.0.0 (sealed: vault/reviews/UCPRP-CPTMP-REVIEW-20260226.md)
EFFECTIVE_DATE:    2026-02-27
AUTHORED_BY:       Jusstin DeRemus (The Oracle)
REVIEWED_BY:       UCPRP v1.0 (score: 4.64/5.0 on v1.0)
STATUS:            ACTIVE
L_RATING:          L4
REPO:              protocols/CPTMP_v1.1_protocol.md
---

## Purpose
Maps all nodes, links, and topological relationships across
the Oracle ecosystem. Governs how gaps are declared, tracked,
and closed across all projects, protocols, spaces, and agents.

## Link Types — Formal Registry

| CODE | NAME     | DEFINITION                                        |
|------|----------|---------------------------------------------------|
| DEP  | Dependency | Node A requires Node B to function correctly.   |
| SHR  | Shared     | A and B co-own or jointly produce an artifact.  |
| PRD  | Produced   | A is an output artifact produced by B.          |
| ANC  | Ancestor   | B is the prior version or origin of A.          |
| SIB  | Sibling    | A and B are peer nodes in the same cluster.     |

Migration note (v1.0 → v1.1):
All prior SHR links used for Space siblings must be reviewed
and reclassified as SIB where applicable.

## Gap Closure Criteria

A gap is formally CLOSED when ONE of the following is met:

| CLOSURE TYPE    | CONDITION                                      |
|-----------------|------------------------------------------------|
| RESOLVED ✅     | Direct file evidence confirms the gap answer.  |
| INFERRED ⚠      | Oracle declares working hypothesis.            |
| ORACLE DECLARED | Oracle issues /oracle decide command.          |
| DEPRECATED ✗    | Gap made irrelevant by upstream decision.      |
| UNRESOLVABLE ✗  | Cannot resolve from available files.           |

Gap record must include:
GAP_ID · SPACE · OPENED_DATE · CLOSED_DATE · CLOSURE_TYPE
EVIDENCE_SOURCE · CLOSED_BY

## Ecosystem Health Score — Formula v1.0

HEALTH = BASE(50)
       + NODE_SCORE      [(registered/known) × 15]
       + LINK_SCORE      [(confirmed/total) × 10]
       + SPACE_SCORE     [(beaconed/core) × 10]
       + PROTOCOL_SCORE  [(L4+L5/total) × 10, weighted]
       + DECISION_SCORE  [(resolved/total) × 10]
       - PENALTY_SCORE   [ghosts×3 + unversioned×1
                          + shadows×0.5 + P0_open×3]

Score range: 0–100. Target: ≥ 90 = ENTERPRISE READY.

## Shadow Link Lifecycle — Rules SL-01 through SL-05

SL-01  Shadow link must declare resolution path at creation.
SL-02  Shadow link surviving 3 sessions → force-retired.
SL-03  Oracle may promote shadow → INFERRED (MEDIUM) by decree.
SL-04  Oracle may retire a shadow at any time by decree.
SL-05  Zero shadow links = prerequisite for L5 rating.

## NODE_NEW Promotion Workflow — 5 Stages

STAGE 1  NODE_NEW raised in beacon analysis
STAGE 2  Conflict check against registry
STAGE 3  Classification (type · L_rating · stack position)
STAGE 4  Oracle decision issued (/oracle decide)
STAGE 5  Registered canon — NODE_ID · repo path · version tag

Template case: PRT-UDFNEXUS (D09 · first formal promotion)

## Node Schema

Every node registration must include:
  NODE_ID · NAME · TYPE · VERSION · STATUS
  L_RATING · L_RATING_DATE · L_RATING_RATIONALE
  OWNER_SPACE · CREATED · REPO
