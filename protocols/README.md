# Protocols Directory

This directory contains the protocol definitions for the Universal Seed Summary system.

## Available Protocols

| Protocol | Version | Description |
|----------|---------|-------------|
| USS | 1.3 | Universal Seed Summary - core archival and resurrection protocol |
| MUSS | 1.0 | Memory-Augmented Universal Seed System - blended USS + MARM protocol |

## Protocol Files

- `MUSS_v1.0_protocol.xml` - Full MUSS v1.0 specification with 6-layer architecture
- `uss-v1.3.json` - USS v1.3 protocol definition (JSON format)

## Usage

### MUSS Protocol

1. Copy `MUSS_v1.0_protocol.xml` content into your LLM session
2. Type `/muss start` to activate MUSS governance
3. Use `/muss seed` for mid-session snapshots
4. Use `/muss archive` for final sealed artifacts

### USS Protocol

See main `README.md` for USS usage instructions.

## Toolchain

- **Validator**: `tools/muss_validator.py` - Validates MUSS artifacts
- **Converter**: `tools/converter.py` - Converts between USS and MUSS formats
  - `--upgrade`: USS v1.3 → MUSS v1.0
  - `--downgrade`: MUSS v1.0 → USS v1.3
- **Indexer**: `tools/indexer.py` - Indexes artifacts for semantic search
