# Phase 13.6 — User Experience Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture and specification only (no UI frameworks, clients, databases, or runtime services)

---

## Objectives

Define what it should feel like to work with KORA:

- UX philosophy and trust/transparency contract
- User-facing interaction patterns
- Explainability without raw chain-of-thought
- Memory, knowledge, Council visibility, project, and task UX requirements

---

## Completed

### Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/User_Experience.md` | UX philosophy, principles, modes, surfaces |
| `Architecture/ai/Interaction_Model.md` | Conversational/project/task/research/decision/automation/notification flows |
| `Architecture/ai/Explainability.md` | Evidence/contributors/confidence/trade-offs/provenance model |
| `Documentation/Phase13/User_Experience_Model.md` | This report |

### Documents updated

| Document | Change |
| --- | --- |
| `Architecture/ai/KORA.md` | UX relationship; document map; future evolution |
| `Architecture/ai/README.md` | UX entry points and separation table |
| `Architecture/ai/Memory_Runtime.md` | UX pointer for user memory controls |
| `Architecture/ai/Context_Assembly.md` | Explainability hook / provenance preservation |
| `Architecture/ai/Council/README.md` | Council visibility modes pointer |
| `Architecture/ai/FuturePlans.md` | 13.6 complete; next = implementation architecture |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.6 complete |
| `Documentation/Phase13/README.md` | Link + status |
| `Architecture/standards/StandardsRoadmap.md` | Phase 13.6 status aligned |

---

## Architectural decisions

1. **KORA is the product UX identity** — not a generic chatbot brand.
2. **Council visibility modes:** Invisible / Advisory / Full — Dynamics owns reasoning; UX owns exposure level.
3. **Explainability = structured accountability** (evidence, contributors, factors, confidence, trade-offs, provenance)—**not raw CoT**.
4. **Memory UX:** view/correct/delete/approve; user controls personal memory.
5. **Knowledge UX:** search/browse/relationships/provenance/authority/freshness.
6. **Projects are first-class** interaction contexts.
7. **Task/approval UX** required for Execute/Administrative actions.
8. **No technology selection** in this phase.

---

## Deferred

| Item | Why deferred |
| --- | --- |
| UI framework / client apps (React, Flutter, Open WebUI, …) | Tech evaluation later |
| Notification vendors | Implementation |
| Concrete wireframes | Design implementation |
| Runtime memory editors / knowledge browsers | Build against this contract later |
| Agent/tool UIs | Implementation |

---

## Consistency checks

| Requirement | Status |
| --- | --- |
| Preserves Council ≠ Agents | Explicit |
| Preserves Memory ≠ Knowledge ≠ Tools | Explicit |
| No silent authority laundering in UX | Explicit via provenance/explainability |
| No raw CoT exposure | Explicit |
| No tech lock-in | Honored |

---

## Phase 13 architecture sequence status

| Sub-phase | Status |
| --- | --- |
| 13.0 Identity | ✅ |
| 13.1 Council ops | ✅ |
| 13.2 Knowledge | ✅ |
| 13.3 Agents | ✅ |
| 13.4 Tools | ✅ |
| 13.5 Memory/Knowledge runtime + context | ✅ |
| 13.6 User experience | ✅ |

---

## Next phase recommendation

**Recommended next step: Implementation Architecture & Technology Evaluation (post–Phase 13 docs)**

Suggested order:

1. ADR(s) for initial client surface(s) satisfying UX/Interaction/Explainability contracts
2. ADR(s) for memory/knowledge runtime stores (still governed by 13.5)
3. ADR(s) for MCP/tool runtimes (governed by 13.4)
4. Thin vertical slice: chat → context assembly → recommendation + explainability

Do not skip ADRs to “just install” a stack. Phase 13 exists so technology serves the architecture.
