# Universal Seed Summary Invoker (USS)

> **Enterprise-grade conversation thread distillation protocol for LLM memory continuity**

[![Version](https://img.shields.io/badge/version-1.3-blue.svg)](https://github.com/DeeTorch/universal-seed-summary)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()

---

## What Is USS?

**Universal Seed Summary Invoker** is a deterministic, LLM-agnostic protocol that transforms any conversation thread into a **compressed, signal-dominant continuity kernel**. It preserves architectural decisions, tracks epistemic boundaries, and maintains audit-grade integrity across session boundaries—without hallucination or semantic drift.

Think of it as a **reasoning checksum** for your AI conversations.

### The Problem

Modern LLM workflows suffer from four critical failures:

- **Context Decay** – Long threads exceed context windows, forcing lossy truncation
- **Semantic Drift** – Traditional summaries introduce inference, reinterpretation, or bias
- **Decision Amnesia** – Prior commitments and constraints are forgotten or violated
- **Non-Portability** – Thread understanding cannot reliably transfer across models or sessions

### The Solution

USS provides **audit-grade distillation** that achieves **15:1 to 30:1 compression ratios** while maintaining signal integrity through:

✅ **Truth-over-helpfulness bias** – Accuracy over narrative convenience  
✅ **Thread-derived-only constraint** – No hallucinated context or external assumptions  
✅ **Explicit uncertainty tracking** – Epistemic boundaries clearly marked  
✅ **Failure semantics** – Compression losses and contradictions explicitly declared  
✅ **Decision audit trails** – Architectural commits vs exploratory branches distinguished  

---

## Core Guarantees

USS enforces five non-negotiable principles:

| Principle | Guarantee |
|-----------|-----------|
| **Thread Sovereignty** | All content explicitly derivable from the conversation |
| **Inference Containment** | Synthesis approaches, but never crosses, speculation boundaries |
| **Explicit Uncertainty** | Unresolved tensions preserved, not smoothed over |
| **Deterministic Structure** | Fixed sections enforce completeness and comparability |
| **Forward Thrust** | Every artifact encodes next pressures, not just past state |

---

## Use Cases

### 🔄 Checkpoint (Active Development)
**When**: Mid-thread save point during active work  
**Token Budget**: 800-1200  
**Best For**: Daily/weekly development cycles, rapid iteration  
**Invoke With**: `USS-CHECKPOINT`

**Example**: Pausing an active code generation session to capture current architectural decisions and next steps.

### 🧭 Re-entry (Return After Absence)
**When**: Returning to dormant thread after days/weeks away  
**Token Budget**: 1500-2500  
**Best For**: Context restoration, full orientation brief  
**Invoke With**: `USS-SUMMARIZE`

**Example**: Resuming a persona design project after a month—need full context on decisions made and open questions.

### 📦 Archive (Permanent Record)
**When**: Thread completion or long-term storage  
**Token Budget**: 3000-5000  
**Best For**: Project completion, compliance records, knowledge bases  
**Invoke With**: `USS-ARCHIVE`

**Example**: Finalizing a research thread—need comprehensive record with all artifacts, decisions, and findings.

---

## Quick Start

### 1. Choose Your Mode

Determine which invocation fits your need:
- **Active work, need periodic save?** → Checkpoint
- **Returning after time away?** → Re-entry
- **Thread complete, need permanent record?** → Archive

### 2. Copy Invocation Prompt

Get the template from [`templates/invocation-prompts/`](templates/invocation-prompts/):

```bash
# Checkpoint mode
cat templates/invocation-prompts/checkpoint-invocation.txt

# Re-entry mode
cat templates/invocation-prompts/reentry-invocation.txt

# Archive mode
cat templates/invocation-prompts/archive-invocation.txt
```

### 3. Paste Into Your LLM Conversation

Works with:
- ✅ Claude (3.5 Sonnet, 4, Opus)
- ✅ GPT-4 (Turbo, 4.5)
- ✅ Perplexity AI
- ✅ Grok (2, 3)
- ✅ Gemini Pro/Ultra
- ✅ Most instruction-following models

### 4. Receive Structured Summary

The LLM generates a markdown artifact following USS protocol:

```markdown
---
mode: checkpoint
version: 1.3
protocol: USS
timestamp: 2026-02-07 10:45:00 PST
---

### HEADER (THREAD LOCK & AUDIT)

**Thread_Archetype**: Development_Forge
**Ignition_Vector**: User initiated full-stack development...
**Focus_Domains**: AI_Architecture + Full_Stack_Development
...
```

### 5. Save and Index

Store using naming convention:

```
{project}_{archetype}_{YYYYMMDD}_{mode}.md
```

**Example**: `Erosforge_Development_20260207_checkpoint.md`

---

## Protocol Structure

### Required Sections

Every USS summary contains six mandatory sections:

#### 1. HEADER (Thread Lock & Audit)
Metadata capturing thread identity, domains, depth, completion state, and momentum.

**Key Fields**: Thread_Archetype, Ignition_Vector, Focus_Domains, Thread_Depth, Completion_State, Momentum_Indicator, Finalization_Beacon, Invoker

#### 2. FAILURE SEMANTICS & INTEGRITY FLAGS
Explicit tracking of contradictions, compression losses, and unresolved tensions.

**Key Fields**: Incoherence_Flags, Compression_Loss_Warnings, Inference_Boundary_Alerts, Resolution_Impossibility_Markers, Failure_Severity

#### 3. COSMIC CORE & EMERGENCE
Foundational concepts, paradigm shifts, and emergent principles.

**Key Fields**: Ontological_Constructs, Paradigm_Nodes, Emergent_Universals

#### 4. DECISIONS & GRAFTS
Architectural commitments, exploratory branches, and epistemic locks.

**Key Fields**: Architecture_Commits, Heuristic_Branches, Epistemic_Locks

#### 5. OPEN VECTORS & THRUST
Unresolved queries, priority actions, and risk surfaces.

**Key Fields**: Unresolved_Queries, Priority_Vectors, Risk_Surfaces

#### 6. INVOCATION LOCK
Final seal declaring artifact complete and ready for use.

### Optional Sections

**Thread Topology** – Cross-thread relationships and dependencies (for multi-project tracking)  
**Execution Artifacts** – Generated outputs, tool usage, reusability notes (required in archive mode)

---

## Features

### 🎯 Signal Preservation Over Noise
Maintains decision context, architectural reasoning, and epistemic boundaries while compressing narrative details.

### 🚨 Failure Semantics Transparency
Explicitly tracks:
- **Incoherence flags** – Contradictions in the thread
- **Compression loss warnings** – What nuance was sacrificed
- **Inference boundary alerts** – Where synthesis approached speculation
- **Resolution impossibility markers** – What can't be decided yet

### 🔄 Paradigm Node Detection
Identifies moments where thread framing shifted, enabling phase transition tracking across long projects.

### 📋 Decision Audit Trails
Separates committed architectures from exploratory branches, preventing confusion about what's locked vs flexible.

### 🌐 Cross-Thread Knowledge Graphs
Optional topology mapping enables multi-thread project management with parent/child/sibling relationships.

### 🔧 Complete Tool Suite
Three production-ready utilities for working with summaries:
- **validator.py** – Protocol compliance checker
- **indexer.py** – Archive indexer and searcher
- **converter.py** – Format converter (MD ↔ JSON ↔ YAML)

---

## Repository Structure

```
universal-seed-summary/
├── README.md                   # This file
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── .gitignore                  # Repository ignore patterns
├── requirements.txt            # Python dependencies
│
├── protocol/
│   └── uss-v1.3.json          # Complete protocol specification
│
├── docs/
│   ├── quickstart.md          # 5-minute getting started guide
│   └── TOOLS_README.md        # Complete tools documentation
│
├── examples/
│   ├── checkpoint/
│   │   └── checkpoint_example.md    # Erosforge project checkpoint
│   ├── re-entry/
│   │   └── reentry_example.md       # UVB project re-entry
│   └── archive/
│       └── archive_example.md       # Research archive
│
├── templates/
│   └── invocation-prompts/
│       ├── checkpoint-invocation.txt
│       ├── reentry-invocation.txt
│       └── archive-invocation.txt
│
└── tools/
    ├── validator.py           # Protocol compliance checker
    ├── indexer.py             # Archive indexer and searcher
    └── converter.py           # Format converter
```

---

## Tools

### Validator (`tools/validator.py`)

Checks USS output for protocol compliance.

**Features**:
- Verifies all required sections and fields present
- Validates formatting standards (###, **, -, ---)
- Checks token budgets per mode
- Detects vague failure semantics language
- Validates INVOCATION LOCK completeness

**Usage**:
```bash
# Basic validation
python tools/validator.py my-summary.md

# Verbose output with details
python tools/validator.py my-summary.md -v

# Strict mode (treat warnings as errors)
python tools/validator.py my-summary.md --strict
```

### Indexer (`tools/indexer.py`)

Builds searchable index of USS summary archives.

**Features**:
- Scans directories for USS summaries
- Extracts metadata (mode, archetype, project, domains)
- Creates JSON index for fast lookup
- Search by project, mode, archetype, or keywords
- Statistics reporting

**Usage**:
```bash
# Index directory
python tools/indexer.py ./summaries/ -v

# Search indexed summaries
python tools/indexer.py ./summaries/ --search "Erosforge"
python tools/indexer.py ./summaries/ --mode checkpoint
python tools/indexer.py ./summaries/ --archetype "Development_Forge"

# Combined filters
python tools/indexer.py ./summaries/ --mode archive --project "UVB"
```

### Converter (`tools/converter.py`)

Converts USS summaries between formats.

**Features**:
- Auto-detects input format
- Converts Markdown ↔ JSON ↔ YAML
- Preserves structure and metadata

**Usage**:
```bash
# Convert to JSON
python tools/converter.py my-summary.md --to json

# Convert to YAML
python tools/converter.py my-summary.md --to yaml

# Convert JSON back to Markdown
python tools/converter.py my-summary.json --to markdown
```

**See [docs/TOOLS_README.md](docs/TOOLS_README.md) for complete tool documentation.**

---

## Installation

### Requirements
- Python 3.9+
- No external dependencies for core functionality

### Setup

```bash
# Clone repository
git clone https://github.com/DeeTorch/universal-seed-summary.git
cd universal-seed-summary

# Optional: Install enhanced dependencies
pip install -r requirements.txt

# Verify tools work
python tools/validator.py examples/checkpoint/checkpoint_example.md
python tools/indexer.py examples/
python tools/converter.py examples/checkpoint/checkpoint_example.md --to json
```

---

## Integration Examples

### AI Persona Memory Systems
USS provides the distillation layer for persona continuity across sessions. Use checkpoint mode for persona evolution tracking.

**Example Projects**:
- Ultimate Voice Bridge (UVB) – AI persona memory architecture
- Erosforge – Code generation platform
- Fólkvangr Neural Core – AI system orchestration

### Research Knowledge Bases
Archive mode creates permanent records of exploratory threads with explicit uncertainty tracking.

### Development Project Management
Thread topology mapping enables multi-thread dependency tracking across complex projects.

### LLM Prompt Engineering
Decision audit trails document what prompt structures worked, failed, or remain exploratory.

---

## Real-World Examples

### Checkpoint: Erosforge Development Session
**Project**: Full-stack code generation platform  
**Thread Depth**: 12 exchanges  
**Completion**: 40%  
**Key Decision**: Locked Kotlin + Bash architecture  
**Next Step**: Implement validation layer  

[View full example →](examples/checkpoint/checkpoint_example.md)

### Re-entry: UVB Persona Architecture
**Project**: AI persona with memory persistence  
**Thread Depth**: 18 exchanges  
**Dormancy**: 3 weeks  
**Context Restored**: Persona design principles, voice profile decisions, integration architecture  
**Priority**: Resume voice processing pipeline implementation  

[View full example →](examples/re-entry/reentry_example.md)

### Archive: Prompt Engineering Research
**Project**: Multi-platform prompt optimization study  
**Thread Depth**: 24 exchanges  
**Status**: Complete  
**Artifacts**: 15 tested prompts, cross-platform analysis, reusability framework  
**Outcome**: Production-ready prompt library  

[View full example →](examples/archive/archive_example.md)

---

## Documentation

- **[Quick Start Guide](docs/quickstart.md)** – Get started in 5 minutes
- **[Tools Documentation](docs/TOOLS_README.md)** – Complete guide to validator, indexer, converter
- **[Protocol Specification](protocol/uss-v1.3.json)** – Complete technical specification

---

## Contributing

Contributions welcome! We're especially interested in:

- 📝 Real-world usage examples from your projects
- 🔧 Tool enhancements (semantic search, auto-indexing, visualization)
- 🧪 Cross-platform testing and optimization notes
- 🔌 Integration adapters for note-taking systems (Obsidian, Notion, etc.)
- 📚 Documentation improvements and translations

**See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.**

---

## Roadmap

### v1.3 (Current) – Production Ready
✅ Complete protocol specification  
✅ Three invocation modes with token budgets  
✅ Working examples for all modes  
✅ Three utility tools (validator, indexer, converter)  
✅ Professional documentation  

### v1.4 (Planned) – Enhanced Tooling
- Enhanced validator with auto-fix mode
- Indexer with semantic search
- Converter with XML support
- Cross-platform validation reports

### v2.0 (Future) – Enterprise Edition
- Formal white paper and governance documentation
- Compliance framework mapping (SOC2, ISO 27001)
- Advanced topology visualization
- Multi-thread stitching capabilities

**See [CHANGELOG.md](CHANGELOG.md) for complete version history.**

---

## FAQ

### How is USS different from regular summarization?

USS is **audit-grade distillation**, not narrative summarization. It preserves:
- Architectural decisions and their reasoning
- Explicit contradictions and uncertainties
- Epistemic boundaries (what's known vs speculated)
- Compression losses and failure semantics

Traditional summaries optimize for brevity; USS optimizes for **continuity without drift**.

### Which LLMs work best with USS?

USS is **model-agnostic** and works with any instruction-following model. Tested extensively on:
- Claude (3.5 Sonnet, 4, Opus) – Excellent
- GPT-4 (Turbo, 4.5) – Excellent
- Perplexity AI – Excellent
- Grok (2, 3) – Very Good
- Gemini Pro/Ultra – Good

### Can I modify the protocol for my needs?

Yes! USS is MIT licensed. You can:
- Add custom fields to sections
- Create new invocation modes
- Extend tool functionality
- Fork for proprietary use

We encourage sharing improvements back to the community.

### How do I handle very long threads (100+ exchanges)?

For threads exceeding 50+ exchanges:
1. Use **checkpoint mode** every 15-20 exchanges
2. Create **parent-child thread relationships** using Thread Topology
3. Use **re-entry mode** when resuming
4. Final **archive mode** captures full journey with references to checkpoints

### What if my LLM doesn't follow the format perfectly?

Use the validator:
```bash
python tools/validator.py output.md -v
```

Common issues:
- Missing fields → Add manually
- Formatting errors → Run with `--strict` to catch
- Token budget exceeded → Acceptable in archive mode

### How do I search across many archived summaries?

Use the indexer:
```bash
# Build index
python tools/indexer.py ./summaries/ -o my-index.json

# Search
python tools/indexer.py ./summaries/ --search "machine learning" --mode archive
```

Creates searchable JSON index with metadata from all summaries.

---

## License

MIT License – See [LICENSE](LICENSE) for details.

You are free to:
- ✅ Use USS commercially
- ✅ Modify and distribute
- ✅ Use in proprietary projects
- ✅ Create derivative works

---

## Author

**Jusstin DeRemus (The Oracle)**  
AI Systems Architect | Prompt Engineer | Full-Stack Developer  

Part of the **Fólkvangr Systems Neural Core** architecture initiative.

- 🌐 Website: https://github.com/DeeTorch
- 🐦 Twitter: [@Jusstin_DeTorch](https://x.com/Jusstin_DeTorch)
- 💼 LinkedIn: [Jusstin DeRemus](https://www.linkedin.com/in/jusstin-deremus-abb965257/)
- 📧 Contact: justjusstin369@gmail.com

---

## Acknowledgments

Developed through iterative testing across Claude, GPT-4, Perplexity, and Grok platforms. Special thanks to:

- The AI systems community for epistemic engineering principles
- Early testers and contributors
- Anthropic, OpenAI, Perplexity, and xAI for powerful LLM platforms
- The open-source community for inspiration and feedback

---

## Citation

If you use USS in research or commercial projects, please cite:

```bibtex
@software{deremus2026uss,
  title={Universal Seed Summary Invoker: Audit-Grade Thread Distillation Protocol},
  author={DeRemus, Jusstin},
  year={2025},
  version={1.3},
  url={https://github.com/DeeTorch/universal-seed-summary}
}
```

---

## Status

**🚀 Production Ready**  
**Version**: 1.3  
**Last Updated**: February 7, 2025  
**Stability**: Stable  
**Maintenance**: Active  

---

**Ready to preserve your conversation context without losing signal?**

[Get Started →](docs/quickstart.md) | [View Examples →](examples/) | [Read the Docs →](docs/)

---

*USS Protocol – Where conversation continuity meets epistemic integrity.*
