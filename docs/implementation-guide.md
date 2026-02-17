# USS Implementation Guide

Complete guide to implementing and using the Universal Seed Summary Invoker protocol.

## Section-by-Section Breakdown

### 1. HEADER (Thread Lock & Audit)

**Purpose**: Capture thread identity and metadata for indexing and retrieval.

#### Thread_Archetype
Categorize the conversation's dominant pattern:
- **Development_Forge**: Building software, systems, or technical solutions
- **Inquiry_Audit**: Research, investigation, or knowledge gathering
- **Conceptual_Synthesis**: Designing frameworks, theories, or abstractions
- **Adversarial_Design**: Stress-testing ideas through critique
- **Implementation_Debug**: Troubleshooting and problem-solving
- **Exploratory_Research**: Open-ended discovery without fixed goal

#### Ignition_Vector
The initial question or objective that started the thread. Keep to 2 sentences maximum.

#### Focus_Domains
Use `+` to show domain intersections: `AI_Architecture + Full_Stack_Development`

#### Thread_Depth
Count user-model exchange pairs (not individual messages).

#### Completion_State
- Exploratory (<25%)
- Development (25-75%)
- Stabilizing (75-95%)
- Complete (95-100%)

#### Momentum_Indicator
- Accelerating: Gaining speed and clarity
- Steady: Consistent progress
- Stalled: Blocked or waiting
- Pivoting: Changing direction
- Concluding: Wrapping up

---

### 2. FAILURE SEMANTICS & INTEGRITY FLAGS

**Purpose**: Explicit honesty about compression losses and uncertainties.

#### Incoherence_Flags
List actual contradictions found in the thread. If none: "None detected within thread bounds."

#### Compression_Loss_Warnings
What nuance was sacrificed? Be specific about what discussions were compressed.

#### Inference_Boundary_Alerts
Where did synthesis approach speculation? Mark these boundaries clearly.

#### Resolution_Impossibility_Markers
What cannot be decided without external data? Use bullet format.

#### Failure_Severity
- Low: Cosmetic loss only
- Medium: Meaningful nuance lost
- High: Decision-impacting uncertainty

---

### 3. COSMIC CORE & EMERGENCE

**Purpose**: Capture foundational concepts and paradigm shifts.

#### Ontological_Constructs
Core terms and principles explicitly defined in the thread.

#### Paradigm_Nodes
Moments where understanding shifted. Number them and note what changed.

#### Emergent_Universals
Principles that generalize beyond this thread while remaining grounded in it.

---

### 4. DECISIONS & GRAFTS

**Purpose**: Separate committed decisions from exploratory ideas.

#### Architecture_Commits
Locked decisions that are non-negotiable going forward.

#### Heuristic_Branches
Proposed paths that remain exploratory.

#### Epistemic_Locks
Non-negotiable truths or constraints established in the thread.

---

### 5. OPEN VECTORS & THRUST

**Purpose**: Capture forward momentum and unresolved tensions.

#### Unresolved_Queries
Open questions still pulling on the system.

#### Priority_Vectors
Next actions ranked by urgency.

#### Risk_Surfaces
Ambiguities or edge cases requiring future attention.

---

### 6. INVOCATION LOCK

**Purpose**: Seal the artifact as complete.

Write 2-4 sentences declaring the summary complete and ready for use.

---

## Optional Sections

### Thread Topology
Use only when thread has explicit relationships to other threads.

### Execution Artifacts
Required for archive mode. Document all generated outputs.

---

## Best Practices

### Do
- Be specific about compression losses
- Explicitly declare absences
- Use thread-derived content only
- Maintain epistemic boundaries

### Don't
- Add external information
- Smooth over contradictions
- Use vague language in failure semantics
- Introduce concepts not in thread

---

## Mode Selection Guide

**Checkpoint**: Active work, need periodic save  
**Re-entry**: Returning after absence  
**Archive**: Thread complete or abandoned
