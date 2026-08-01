# Council Deliberation Lifecycle

**Status:** Canonical operational specification (Phase 13.1)  
**Authority:** Extends `Dynamics.md`, `Selection.md`, and `Voting.md`.  
**Platform:** `../KORA.md`

This document answers: **How do Council members contribute?** and **How is a final response produced?**  
Selection details: `Selection.md`. Conflict synthesis: `Voting.md`.

---

## Operational Flow

```text
User Request
    ↓
KORA Classification
    ↓
Context Assembly
    ↓
Member Selection
    ↓
Individual Perspectives
    ↓
Cross Examination
    ↓
Synthesis
    ↓
Final Recommendation
    ↓
Memory / Knowledge Evaluation
```

KORA participates throughout as Chair/Conductor and as a reasoning member for coordination/coherence—not as a manager of employees.

---

## Stage Definitions

### 1. User Request

The requester presents a need, question, or decision. The Council exists to help this person.

### 2. KORA Classification

KORA determines objective, domain, complexity, constraints, time horizon, risk level, and required expertise.  
See `Selection.md` → Request Classification.

### 3. Context Assembly

KORA gathers minimum sufficient context from:

| Source | Role |
| --- | --- |
| Memory | Prior interactions and decisions |
| Knowledge | Reference information (repo, standards, inventories) |
| Tools | Live environment facts (when needed) |

Context assembly is a KORA platform responsibility, not a Council member role.  
See `../KORA.md` and `../Memory.md` / `../MCP.md`.

### 4. Member Selection

KORA invites the minimum viable Council and records deferrals and escalation triggers.  
See `Selection.md`.

### 5. Individual Perspectives

Each invited member contributes from specialty only.

### 6. Cross Examination

Members challenge, corroborate, or reframe one another where specialties intersect.  
KORA sequences productive challenge and discourages dominance contests.

### 7. Synthesis

KORA weaves convergent points, dimensional truths, and residual disagreement into one coherent structure.  
See `Voting.md` (Deliberative Synthesis).

### 8. Final Recommendation

KORA presents the user-facing recommendation: summary, rationale, risks, alternatives/conditions, next actions.  
Schema: `Schemas/recommendation.yaml`.

### 9. Memory / Knowledge Evaluation

After response (when appropriate under later governance):

- Decide what should persist as memory (decision traces, preferences, outcomes)
- Decide what should update knowledge (reference facts, corrected inventories)
- Do not persist noise or unverified speculation as authority

Detailed memory/knowledge governance remains Phase 13.2 / 13.5. This stage marks the lifecycle boundary only.

---

## Member Contribution Model

### Required contribution elements

Each active member’s contribution should include:

| Element | Meaning |
| --- | --- |
| **Perspective** | Specialty lens applied to this request |
| **Assumptions** | What the member takes as given |
| **Supporting reasoning** | Why the view follows from specialty + context |
| **Concerns** | Weak points, uncertainties, objections |
| **Risks** | Downsides visible from this specialty |
| **Recommendation** | Specialty-local recommended stance or action |
| **Confidence** | Honesty about certainty within specialty |

Schema: `Schemas/member_response.yaml`.

### Contribution rules

Members **should**:

- Stay within specialization
- Make assumptions explicit
- Challenge other dimensions respectfully when invited or when silence would create harm
- Distinguish facts, inferences, and preferences

Members **must not**:

- Impersonate other members
- Override their specialization to “solve everything”
- Attempt to cover every decision dimension alone
- Compete for victory over synthesis
- Treat confidence as authority over other specialties

### Specialty expectations (contribution focus)

| Member | Primary contribution focus |
| --- | --- |
| KORA | Relevance, pacing, fairness, coherence, user-facing clarity |
| NOVA | Strategic options and ranked path |
| IRIS | Missing information and contradictions |
| TALIA | Meaning, ethics, human interpretation |
| SOLA | Reception, motivation, communicable framing |
| LUMA | Precedent and continuity |
| ALUMA | Buildable mechanism and adaptation |
| NOMA | Consequence models and risk integrity |

---

## Producing the Final Response

The final response is KORA’s synthesis product for the user.

Minimum contents:

1. **Summary** — what to do (or what choice remains)
2. **Rationale** — why, in plain terms
3. **Risks** — material downsides
4. **Alternatives / conditions** — when to choose otherwise
5. **Next actions** — concrete steps when applicable
6. **Material dissent** — if unresolved disagreement would change action

Quality bar (from Dynamics): the strongest balance the user can act on—not the most elaborate internal debate.

---

## Session States (conceptual)

| State | Meaning |
| --- | --- |
| `classifying` | Request analysis in progress |
| `assembling_context` | Memory/knowledge/tools gather |
| `selecting` | Invite/defer decisions |
| `collecting` | Individual perspectives |
| `examining` | Cross examination |
| `synthesizing` | Deliberative synthesis |
| `recommending` | Final user-facing output |
| `evaluating_persistence` | Memory/knowledge evaluation |
| `closed` | Session complete |

These states are conceptual—not a runtime engine requirement.
