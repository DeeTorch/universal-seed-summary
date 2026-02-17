# Quick Start Guide

Get your first USS summary in under 5 minutes.

## Prerequisites

- An active LLM conversation (Claude, GPT-4, Perplexity, Grok, etc.)
- A thread you want to summarize (at least 3+ exchanges recommended)

## Step 1: Choose Your Mode

Determine which invocation mode matches your goal:

| Mode | When to Use | Token Budget | Trigger |
|------|-------------|--------------|---------|
| **Checkpoint** | Mid-development save point | 800-1200 | `USS-CHECKPOINT` |
| **Re-entry** | Coming back after time away | 1500-2500 | `USS-SUMMARIZE` |
| **Archive** | Completed or abandoned thread | 3000-5000 | `USS-ARCHIVE` |

### Decision Tree

```
Are you done with this thread?
├─ YES → Use USS-ARCHIVE (permanent record)
└─ NO → Is it your first summary of this thread?
    ├─ YES → Use USS-CHECKPOINT (save current state)
    └─ NO → Have you been away for a while?
        ├─ YES → Use USS-SUMMARIZE (full re-orientation)
        └─ NO → Use USS-CHECKPOINT (periodic save)
```

## Step 2: Copy the Invocation Prompt

### Basic Invocation (Inline Protocol)

Copy and paste this directly into your LLM conversation:

```
Execute the Universal Seed Summary Invoker protocol in CHECKPOINT mode.

Review this entire thread from first exchange to this point and generate a structured summary following these requirements:

Required Sections:
1. HEADER (Thread_Archetype, Ignition_Vector, Focus_Domains, Thread_Depth, Completion_State, Momentum_Indicator, Finalization_Beacon, Invoker)
2. FAILURE SEMANTICS & INTEGRITY FLAGS (Incoherence_Flags, Compression_Loss_Warnings, Inference_Boundary_Alerts, Resolution_Impossibility_Markers, Failure_Severity)
3. COSMIC CORE & EMERGENCE (Ontological_Constructs, Paradigm_Nodes, Emergent_Universals)
4. DECISIONS & GRAFTS (Architecture_Commits, Heuristic_Branches, Epistemic_Locks)
5. OPEN VECTORS & THRUST (Unresolved_Queries, Priority_Vectors, Risk_Surfaces)
6. INVOCATION LOCK (Final sealing paragraph)

Constraints:
- All content must be strictly derived from this thread only
- No external inference or assumptions permitted
- Explicitly declare all uncertainties and absences
- Target token budget: 800-1200
- Use markdown format with ### section headers and **Field**: value format

Begin USS-CHECKPOINT execution now.
```

**For RE-ENTRY mode**: Change "CHECKPOINT" to "SUMMARIZE" and token budget to "1500-2500"

**For ARCHIVE mode**: Change "CHECKPOINT" to "ARCHIVE", token budget to "3000-5000", and add:
```
Additional Sections for Archive:
7. THREAD TOPOLOGY (if applicable)
8. EXECUTION ARTIFACTS (Generated_Outputs, Tool_Usage_Patterns, Reusability_Index)
```

### Advanced: Reference Full Specification

For maximum compliance, reference the complete protocol:

```
Execute the Universal Seed Summary Invoker protocol v1.3 in CHECKPOINT mode.

Complete protocol specification: https://github.com/[username]/universal-seed-summary/blob/main/protocol/uss-v1.3.json

Requirements:
- Review entire thread from genesis to this invocation point
- Populate all required sections per protocol specification
- Follow enforcement rules strictly (truth-over-helpfulness, thread-derived-only, explicit uncertainty)
- Target token budget: 800-1200 tokens
- Use markdown format with YAML frontmatter

Begin execution now.
```

## Step 3: Paste and Execute

1. **Paste** the invocation prompt at the end of your conversation
2. **Send** the message
3. **Wait** for the LLM to generate the summary (typically 30-60 seconds)

## Step 4: Review the Output

Your summary should include:

✅ All required section headers  
✅ Populated fields (not "TODO" or placeholders)  
✅ Explicit declarations for absent information  
✅ Timestamp in correct format  
✅ Token count within target budget  

### Quick Validation

Check for these common issues:

❌ Missing sections  
❌ Vague failure semantics ("Some nuance may be lost")  
❌ Concepts not present in original thread  
❌ No timestamp or incorrect format  
❌ Empty fields without explicit null declaration  

## Step 5: Save the Summary

### File Naming Convention

Use this pattern for consistency:
```
{project}_{thread_archetype}_{YYYYMMDD}_{mode}.md
```

**Examples**:
```
Erosforge_Development_Forge_20260206_checkpoint.md
UVB_Conceptual_Synthesis_20260115_archive.md
PromptOptimization_Inquiry_Audit_20260203_summarize.md
```

### Storage Structure

Organize summaries by project:
```
summaries/
├── erosforge/
│   ├── 20260206_checkpoint.md
│   └── 20260115_archive.md
├── uvb/
│   └── 20260203_checkpoint.md
└── folvangr/
    └── 20260120_archive.md
```

Or by date for chronological view:
```
summaries/
├── 2026-02/
│   ├── 06_erosforge_checkpoint.md
│   ├── 03_uvb_checkpoint.md
│   └── 01_research_archive.md
└── 2026-01/
    └── 15_erosforge_archive.md
```

## Step 6: Index (Optional)

Build a searchable index:

```bash
python tools/indexer.py --scan ./summaries/ --output index.json
```

This creates a JSON index enabling fast searches across all your archived threads.

## Example: Your First Checkpoint

Let's do a real example. Assume you're working on a project called "VoiceAI" and you've had 8 exchanges about system architecture.

**Your invocation**:
```
USS-CHECKPOINT
```

**Expected output** (abbreviated):
```markdown
---
mode: checkpoint
version: 1.3
timestamp: 2026-02-06 19:00:00 PST
---

### HEADER (THREAD LOCK & AUDIT)

**Thread_Archetype**: Development_Forge

**Ignition_Vector**: User requested architecture design for VoiceAI 
system with real-time transcription, speaker diarization, and 
emotion detection capabilities.

**Focus_Domains**: Audio_Processing + AI_Architecture + Real_Time_Systems

**Thread_Depth**: 8 exchanges

**Completion_State**: Development (35%)

**Momentum_Indicator**: Accelerating

**Finalization_Beacon**: 2026-02-06 19:00:00 PST

**Invoker**: Jusstin DeRemus via Claude

---

### FAILURE SEMANTICS & INTEGRITY FLAGS

**Incoherence_Flags**: None detected within thread bounds.

**Compression_Loss_Warnings**: Detailed discussion of WebSocket vs 
HTTP polling trade-offs compressed. Original thread included 
performance benchmarks and edge case analysis not captured here.

**Inference_Boundary_Alerts**: No inference boundary approached.

**Resolution_Impossibility_Markers**:
- Final API framework selection (FastAPI vs Flask) requires 
  performance testing
- Emotion detection model accuracy not yet validated
- Deployment infrastructure (cloud vs on-prem) undecided

**Failure_Severity**: Medium (deployment decisions pending)

[... rest of output ...]
```

**You save as**: `VoiceAI_Development_Forge_20260206_checkpoint.md`

## Next Steps

### Continue Development
Return to your thread and keep working. Create another checkpoint when:
- You've made significant progress (50+ exchanges)
- You're switching contexts (end of day/week)
- You've reached a decision point or milestone

### Re-enter Later
When you return to the thread after time away:
1. Read your saved checkpoint
2. Resume conversation
3. When ready to save again, use `USS-SUMMARIZE` for full context

### Archive Completion
When thread is complete:
1. Run `USS-ARCHIVE` for permanent record
2. Extract reusable patterns to your knowledge base
3. Link to related threads using Thread Topology section

## Troubleshooting

### "My output is missing sections"
→ The LLM may need clearer instructions. Use the "Advanced" invocation method with full protocol reference.

### "Token count is way over budget"
→ For very long threads, the LLM may struggle to compress effectively. Try breaking into multiple checkpoints or use archive mode.

### "Failure Semantics section is vague"
→ Explicitly instruct: "Be specific about what compression losses occurred. Don't use generic phrases."

### "Output doesn't follow format"
→ Add: "Use exactly this format: **Field_Name**: value with ### for headers and - for bullets."

## Advanced Usage

### Automated Checkpoints
Create a wrapper script that triggers USS-CHECKPOINT every N exchanges or M minutes.

### Multi-Thread Projects
Use Thread Topology section to link related conversations across different platforms or sessions.

### Knowledge Graph
Build a visualization of your project history by parsing Thread Topology relationships.

### Semantic Search
Convert summaries to embeddings and enable natural language search across all archived threads.

## Resources

- **[Implementation Guide](implementation-guide.md)** – Deep dive into each section
- **[Mode Comparison](mode-comparison.md)** – Detailed comparison table
- **[Example Outputs](../examples/)** – Real summaries for reference
- **[Design Philosophy](design-philosophy.md)** – Why USS works this way

## Questions?

See **[FAQ](faq.md)** or open an issue on GitHub.

---

**You're ready!** Go create your first USS summary. Start with checkpoint mode and experiment from there.
