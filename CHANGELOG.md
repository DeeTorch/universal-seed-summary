# Changelog

All notable changes to the Universal Seed Summary Invoker protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [MUSS v1.0] - 2026-02-27

### Added

- **MUSS Protocol**: Memory-Augmented Universal Seed System - blended protocol combining USS v1.3 with MARM v1.4
- **Live Session Governance**: Real-time accuracy enforcement, anti-drift management, safeguard checks
- **Session Log System**: Running ledger with categories (DECISION, INSIGHT, OPEN, RISK, ARTIFACT, DIRECTIVE)
- **Notebook System**: Persistent key-value store for session data
- **Drift Management**: Automatic DRIFT_FLAG at exchange thresholds (LOW/MEDIUM/HIGH)
- **Lifecycle Engine**: Full ACTIVE -> SEED -> ARCHIVE -> RESURRECT transitions
- **9-Layer Artifact Schema**: HEADER, LIVE MEMORY SNAPSHOT, FAILURE SEMANTICS, COSMIC CORE, DECISIONS, OPEN VECTORS, THREAD TOPOLOGY, EXECUTION ARTIFACTS, INVOCATION LOCK
- **Model Profiles**: Delivery wrappers for Claude, ChatGPT, Grok, Gemini, Perplexity
- **Toolchain Integration**: muss_validator.py, converter.py (--upgrade/--downgrade), indexer.py
- **Resurrection Hook**: Standardized format for thread resumption

### Changed

- **Protocol Versioning**: MUSS v1.0 runs alongside USS v1.3 (not replacing)
- **Artifact Format**: Added LIVE MEMORY SNAPSHOT section (MUSS-native)
- **YAML Frontmatter**: Added session_id, exchange_count, drift_risk fields
- **Validation**: MUSS validator extends USS validator with MUSS-specific checks

### Documentation

- Full MUSS protocol in protocols/MUSS_v1.0_protocol.xml
- Protocol directory documentation in protocols/README.md
- Test suite in test/test_muss_protocol.py

### Upgrade Path

- USS v1.3 -> MUSS v1.0: Use `python tools/converter.py --upgrade <artifact.md>`
- MUSS v1.0 -> USS v1.3: Use `python tools/converter.py --downgrade <artifact.md>`

## [1.3.0] - 2025-02-07

### Added

- **Output Specification Section**: Defined format standards, token budgets per mode, and encoding requirements
- **Progress Metrics**: Added `Thread_Depth`, `Completion_State`, and `Momentum_Indicator` fields to HEADER section
- **Invocation Modes System**: Standardized trigger phrases (`USS-CHECKPOINT`, `USS-SUMMARIZE`, `USS-ARCHIVE`)
- **Thread Topology Section**: Optional section for cross-thread relationship mapping (parent/child/sibling threads)
- **Execution Artifacts Section**: Required for archive mode, documents generated outputs and tool usage
- **Validation Checklist**: Built-in compliance verification requirements
- **Implementation Notes**: Platform compatibility, token efficiency, storage recommendations
- **Comprehensive Documentation**: README, Quick Start guide, example outputs, invocation templates
- **Validator Tool**: Python script for automated protocol compliance checking

### Changed

- **Renamed "Quantum Fractures"** → **"Open Vectors & Thrust"** for operational clarity
- **Renamed field "Entangled_Queries"** → **"Unresolved_Queries"**
- **Renamed field "Gravitational_Pull"** → **"Priority_Vectors"**
- **Renamed field "Speculative_Vortices"** → **"Risk_Surfaces"**
- **Enhanced Token Budget Specification**: Mode-specific targets (checkpoint: 800-1200, re-entry: 1500-2500, archive: 3000-5000)
- **Improved Formatting Standards**: Explicit requirements for headers, field format, lists, separators

### Fixed

- Ambiguous section naming that caused semantic drift
- Missing output format specification led to inconsistent implementations
- Lack of token budget guidance caused unpredictable compression
- No standardized invocation syntax created usability friction

### Documentation

- Added comprehensive README with use cases and features
- Created Quick Start guide with decision trees and examples
- Provided 3 complete example outputs (checkpoint, re-entry, archive)
- Included copy-paste ready invocation prompts for each mode
- Built validator tool with CLI interface

## [1.2.0] - 2025-01-15 (Conceptual)

### Added

- Core protocol structure with 6 required sections
- FAILURE SEMANTICS & INTEGRITY FLAGS section
- Truth-over-helpfulness enforcement rule
- Thread-derived-only constraint
- Explicit uncertainty requirements
- Ontological constructs and paradigm node tracking
- Decision audit trails (Architecture Commits vs Heuristic Branches)
- Epistemic locks for non-negotiable truths
- Invocation lock for sealing artifacts

### Initial Design

- Established foundational philosophy: audit-grade distillation
- Defined enforcement rules preventing hallucination
- Created structure for capturing thread evolution
- Separated committed decisions from exploratory branches
- Mandated explicit failure declaration

## [1.0.0] - 2025-01-01 (Theoretical)

### Initial Concept

- Basic summarization protocol concept
- Thread distillation framework
- Memory artifact generation approach

---

## Version Numbering

**MAJOR.MINOR.PATCH**

- **MAJOR**: Incompatible protocol changes (breaking changes to section structure)
- **MINOR**: New features, sections, or fields (backward compatible)
- **PATCH**: Bug fixes, documentation updates, clarifications (no protocol changes)

## Upgrade Path

### From v1.2 to v1.3

**Breaking Changes**: None (v1.3 is backward compatible)

**Recommended Actions**:
1. Update invocation prompts to include new progress metrics
2. Rename "Quantum Fractures" references to "Open Vectors" in documentation
3. Add mode specification to invocation (checkpoint/re_entry/archive)
4. Include token budget targets in prompts
5. Use validator.py to check compliance with new standards

**Optional Enhancements**:
- Add Thread Topology section for multi-thread projects
- Include Execution Artifacts for archive mode
- Specify output format explicitly in invocations

### From v1.0 to v1.2

Major architectural changes required full re-implementation.

---

## Roadmap

### v1.4.0 (Planned)

**Potential Features**:
- Automated checkpoint triggering system
- Summary-of-summaries for long-running projects
- Vector embedding support for semantic search
- Multi-thread visualization tools
- Cross-platform optimization notes (Claude, GPT-4, Grok, etc.)
- Integration adapters for note-taking systems (Obsidian, Notion, Roam)
- Performance metrics tracking over time

### v2.0.0 (Future)

**Possible Major Changes**:
- AI-assisted compression optimization
- Dynamic token budget allocation
- Real-time thread analysis
- Collaborative thread synthesis
- Multi-modal thread support (images, audio, video artifacts)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on proposing changes, reporting issues, and submitting improvements.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

**Maintained by**: Jusstin DeRemus (The Oracle)  
**Repository**: https://github.com/DeeTorch/universal-seed-summary  
**Status**: Production Ready (v1.3)
