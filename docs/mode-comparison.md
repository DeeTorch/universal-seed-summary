# USS Mode Comparison

## Quick Reference Table

| Feature | Checkpoint | Re-entry | Archive |
|---------|-----------|----------|---------|
| **Trigger** | `USS-CHECKPOINT` | `USS-SUMMARIZE` | `USS-ARCHIVE` |
| **Token Budget** | 800-1200 | 1500-2500 | 3000-5000 |
| **Detail Level** | Medium | High | Maximum |
| **Use Case** | Active development | Return after absence | Permanent record |
| **Thread Status** | In progress | Dormant | Complete |
| **Execution Artifacts** | Optional | Optional | Required |
| **Thread Topology** | Optional | Optional | Optional |
| **Compression Priority** | Speed | Context | Completeness |

## When to Use Each Mode

### Checkpoint
**Scenario**: You're actively working on a project and want to save progress.

**Frequency**: Every 15-20 exchanges or at natural breakpoints

**Example**:
- End of coding session
- Before switching contexts
- After major decision point
- Daily/weekly development cycles

**Output Focus**: Current state, next steps, open questions

---

### Re-entry
**Scenario**: You're returning to a dormant thread after days or weeks.

**Frequency**: Once per return after extended absence

**Example**:
- Resuming project after vacation
- Picking up abandoned thread
- Context restoration after interruption
- Monthly project review

**Output Focus**: Full context, decision history, recommended re-entry point

---

### Archive
**Scenario**: Thread is complete or being permanently stored.

**Frequency**: Once at thread conclusion

**Example**:
- Project completion
- Research findings finalized
- Compliance documentation
- Knowledge base entry

**Output Focus**: Complete audit trail, all artifacts, reusability notes

## Detailed Comparison

### Token Budget Rationale

**Checkpoint (800-1200)**:
- Captures essential state
- Omits verbose details
- Focuses on momentum

**Re-entry (1500-2500)**:
- Provides full orientation
- Includes decision context
- Restores working memory

**Archive (3000-5000)**:
- Maximum detail preservation
- Complete artifact list
- Reusability documentation

### Section Requirements

| Section | Checkpoint | Re-entry | Archive |
|---------|-----------|----------|---------|
| HEADER | Required | Required | Required |
| FAILURE SEMANTICS | Required | Required | Required |
| COSMIC CORE | Required | Required | Required |
| DECISIONS & GRAFTS | Required | Required | Required |
| OPEN VECTORS | Required | Required | Required |
| THREAD TOPOLOGY | Optional | Optional | Optional |
| EXECUTION ARTIFACTS | Optional | Optional | **Required** |
| INVOCATION LOCK | Required | Required | Required |

## Mode Selection Decision Tree

```
Is the thread complete?
├─ YES → Archive
└─ NO → Is this your first summary?
    ├─ YES → Checkpoint
    └─ NO → Have you been away >1 week?
        ├─ YES → Re-entry
        └─ NO → Checkpoint
```

## Real-World Examples

### Checkpoint Example
**Project**: Building API service  
**Thread Depth**: 12 exchanges  
**Status**: 40% complete  
**Use**: Save current architecture decisions before weekend

### Re-entry Example
**Project**: AI persona design  
**Thread Depth**: 34 exchanges  
**Dormancy**: 18 days  
**Use**: Restore full context to resume implementation

### Archive Example
**Project**: Prompt engineering research  
**Thread Depth**: 47 exchanges  
**Status**: Complete  
**Use**: Permanent record with all tested prompts and findings

## Switching Between Modes

### Checkpoint → Re-entry
When returning after absence, create re-entry summary referencing previous checkpoint.

### Checkpoint → Archive
At completion, create archive summary that supersedes all checkpoints.

### Multiple Checkpoints → Archive
Archive can reference checkpoint history in Thread Topology section.
