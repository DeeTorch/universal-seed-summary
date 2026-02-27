# DIRP Protocol Registry Report

REPORT_ID:    DIRP-PROTOCOLS-20260226-0734
GENERATED:    2026-02-26T07:34:00-08:00
DIRP_VERSION: v1.1
SCOPE:        All registered protocols across ecosystem
TOTAL_COUNT:  14 identified
HEALTH:       74/100 (baseline)

---

## Protocol Registry (Session 1 Initial State)

| PROTOCOL_ID | NAME | VERSION | STATUS | L | OWNER_SPACE | GAPS | NOTES |
|-------------|------|---------|--------|---|-------------|------|-------|
| PRT-USS | Universal Seed Summary | v1.3 | ACTIVE | L5 | SPC-VAULT | 0 | Canon · Foundation layer |
| PRT-MUSS | Memory-Augmented USS | v1.0 | ACTIVE | L5 | SPC-VAULT | 0 | Canon · Successor to USS |
| PRT-DIRP | Directory Interaction Report Protocol | v1.1 | ACTIVE | L4 | SPC-VAULT | 1 | Active · 4+ runs |
| PRT-UCE | Universal Core Emission | v1.0.0 | ACTIVE | L4 | SPC-UCE | 3 | Production emission layer · 2 runs |
| PRT-UCPRP | Universal Core Protocol Review Panel | v1.0 | ACTIVE | L4 | SPC-VAULT | 2 | Active · 2 reviews completed |
| PRT-UABP | Universal Architecture Briefing Protocol | v1.0.0 | ACTIVE | L4 | SPC-UCE | 1 | Architecture layer · in use |
| PRT-VAULT | Vault Protocol | v1.0 | ACTIVE | L4 | SPC-VAULT | 0 | Archive standard · 33 artifacts |
| PRT-CPTMP | Cross-Project Topology Mapping | v1.0.0 | ACTIVE | L3 | SPC-APEX | 4 | Topology mapper · REVIEW PENDING |
| PRT-APF | APEX Persona Framework | v2.0 | ACTIVE | L3 | SPC-APEX | 2 | Authored · unreviewed |
| PRT-ERP | Evolutionary Reference Protocol | v1.0 | DESIGN | L2 | SPC-FORGE | 5 | Horizontal · not versioned |
| PRT-DTIE | Domain-Topology Integration Engine | v0.9 | DESIGN | L2 | SPC-DTIE | 3 | Horizontal · draft status |
| PRT-DDP | Domain Design Protocol | v1.0.0 | DESIGN | L2 | SPC-APEX | 1 | Co-authored w/ GEMINIKING |
| PRT-WUP | Workflow Unification Protocol | v0.x | DESIGN | L2 | SPC-FORGE | 4 | Versioning unresolved |
| PRT-PRAP | Persona Reference Architecture | v0.1 | DESIGN | L2 | PRJ-FNC | 6 | Draft · in use · not reviewed |

## Gap Summary by Protocol

**HIGH PRIORITY** (4+ gaps):
- PRT-ERP: 5 gaps
- PRT-PRAP: 6 gaps
- PRT-CPTMP: 4 gaps

**MEDIUM PRIORITY** (2-3 gaps):
- PRT-UCE: 3 gaps
- PRT-DTIE: 3 gaps
- PRT-APF: 2 gaps
- PRT-UCPRP: 2 gaps

**LOW PRIORITY** (0-1 gap):
- PRT-USS, PRT-MUSS, PRT-VAULT: 0 gaps (canon)
- PRT-DIRP, PRT-UABP, PRT-DDP, PRT-WUP: 1 gap each

## Key Findings

1. **Canon Protocols (L5)**: USS and MUSS form foundation. All dependencies healthy.
2. **Production Protocols (L4)**: 7 protocols actively deployed. CPTMP awaiting UCPRP review.
3. **L3-L2 Protocols**: 7 protocols in design/spec phase. APF needs formal review.
4. **GEMINIKING Co-Authorship**: PRT-DDP authored jointly - classification pending.
5. **Versioning Issues**: PRT-WUP version scheme unresolved - blocks promotion.

## Recommendations

- Schedule UCPRP review for PRT-CPTMP (critical for topology work)
- Classify GEMINIKING node (impacts DDP L-rating)
- Resolve PRT-WUP versioning before L3 promotion
- Audit PRT-PRAP against PRJ-FNC scope (6 gaps suggest scope misalignment)
