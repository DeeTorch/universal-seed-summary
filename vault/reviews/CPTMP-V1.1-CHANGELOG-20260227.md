# CPTMP v1.0.0 → v1.1.0 Changelog

DATE:       2026-02-27
DECISIONS:  D06 (P0) · D07 (P1)
UCPRP:      4.64/5.0 (v1.0) → est 4.82/5.0 (v1.1)

## Changes

### P0 Patches (D06)
- F01: Protocol version gate added to header
- F02: SIB link type added (link types: 4 → 5)
  Migration: SHR links used for Space siblings → reclassify as SIB

### P1 Patches (D07)
- F03: Gap closure criteria table (5 closure types defined)
- F04: Health score formula published (BASE + 5 components - penalties)
- F05: Shadow link lifecycle rules SL-01 through SL-05
- F06: NODE_NEW promotion workflow (5 stages · D09 as template case)
