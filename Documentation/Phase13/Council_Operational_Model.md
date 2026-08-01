# Phase 13.1 — Council Operational Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no software, Docker, frameworks, agents, or Hermes/LangGraph workflows)

---

## Objective

Define the operational mechanics of the KORA Council:

- How KORA decides who participates
- How members contribute
- How disagreements are handled
- How KORA synthesizes recommendations
- How a final response is produced

Built on Phase 13.0 authority: `Architecture/ai/KORA.md`, `Council/Dynamics.md`, and member specifications.

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Council/Selection.md` | Request classification and member selection model |
| `Architecture/ai/Council/Deliberation.md` | Session lifecycle and contribution model |
| `Architecture/ai/Council/Schemas/README.md` | Schema index |
| `Architecture/ai/Council/Schemas/request.yaml` | Conceptual request/selection shape |
| `Architecture/ai/Council/Schemas/member_response.yaml` | Conceptual member contribution shape |
| `Architecture/ai/Council/Schemas/deliberation.yaml` | Conceptual deliberation record |
| `Architecture/ai/Council/Schemas/recommendation.yaml` | Conceptual final recommendation shape |
| `Architecture/ai/Council/Prompts/README.md` | Prompt architecture (purpose/constraints only) |
| `Architecture/ai/Council/Members/TEMPLATE.md` | Canonical member spec section order |
| `Documentation/Phase13/Council_Operational_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/Council/Voting.md` | Replaced stub with deliberative synthesis model (explicitly not majority voting) |
| `Architecture/ai/Council/README.md` | Index of operational docs |
| `Architecture/ai/Council/Dynamics.md` | Pointers to Selection / Deliberation / Voting / Schemas / Prompts |
| `Architecture/ai/Council/council.yaml` | Conceptual config stub linking authoritative docs |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.1 marked complete |
| `Documentation/Phase13/README.md` | Link to this report |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.1 status aligned |

---

## Architectural decisions made

### Selection approach

- **Minimum viable Council** is the default.
- KORA classifies objective, domain, complexity, constraints, time horizon, risk, and required expertise before inviting members.
- Deferred members remain available; expansion is trigger-based mid-discussion.
- Full Council participation is exceptional.
- Goal: *the smallest group capable of producing a strong recommendation.*

### Deliberation lifecycle

Normalized flow:

`User Request → Classification → Context Assembly → Member Selection → Individual Perspectives → Cross Examination → Synthesis → Final Recommendation → Memory/Knowledge Evaluation`

Stage definitions and contribution rules live in `Deliberation.md`.

### Conflict resolution philosophy

- **No simple majority voting** as the decision mechanism.
- **Deliberative synthesis** captures majority position, minority concerns, evidence, risks, trade-offs, and conditions for alternatives.
- KORA does not declare winners; KORA produces a coherent user-facing recommendation.
- Informed disagreement beats artificial unanimity (`Voting.md`, consistent with `Dynamics.md`).

### Decision framework

- Multi-axial structured reasoning (strategy, feasibility, risk, history, missing info, human impact, meaning/values, synthesis).
- **No rigid scoring** unless a future ADR justifies it.
- Dimensions are weighted by request class, not by fixed mathematics.

### Schema boundaries

- Schemas are **conceptual contracts** for session artifacts.
- They are not tied to a database, API framework, or prompt runtime.
- Member lore docs (`Members/*.md`) remain separate from session contribution schemas.

### Prompt architecture boundaries

- Define classes, required inputs, enforced behaviors, and constraints only.
- **No production prompt text** in Phase 13.1.
- Prompts must not redefine Dynamics or convert members into generic agents.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| Runtime implementation | Explicitly out of scope |
| Agent framework selection | Phase 13.3+; must not conflate agents with Council members |
| Model routing | Models concern; no tech selection in 13.1 |
| Hermes / LangGraph / automation workflows | Implementation track |
| Production prompts | Prompt architecture only |
| Memory/knowledge write governors | Phase 13.2 / 13.5 |
| MCP tool wiring | Phase 13.4 |
| UX / explainability surfaces | Phase 13.6 |
| Automated schema validation tooling | Implementation detail |

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| KORA remains a Council member / Chair / Conductor | Preserved |
| Dynamics.md remains authoritative for philosophy | Preserved; extended by operational docs |
| No hierarchy conflict (KORA not above Council) | Preserved |
| No majority-vote decision system | Explicit in Voting.md |
| No member→generic-agent conversion | Explicit in Deliberation / Prompts |
| No Docker / code / framework selection | Honored |

---

## Next Phase recommendation

**Recommended next step: Phase 13.2 — Knowledge Architecture**

### Dependency rationale

1. Selection and deliberation now assume **context assembly** from memory and knowledge; those substrates lack a dedicated architecture doc.
2. The lifecycle’s final stage (**Memory / Knowledge Evaluation**) cannot be specified safely without knowledge vs memory boundaries.
3. Agent orchestration (13.3) and MCP integrations (13.4) should consume a defined knowledge/memory model rather than inventing ad hoc retrieval.
4. Council operational mechanics are sufficiently specified to proceed without waiting on runtime code.

### Suggested 13.2 kickoff artifacts

- `Architecture/ai/Knowledge.md`
- Memory/knowledge lifecycle and governance principles (still no tech lock-in)
- How Council context assembly reads from each store
