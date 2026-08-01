# Phase 13.8 — Technology Evaluation ADR Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Technology evaluation ADRs only (no deploys, installs, compose, or final production stack)

---

## Objectives

Begin the implementation transition after Phase 13.0–13.7 by evaluating candidates against KORA architecture contracts:

- Does the technology fit KORA?
- Does it preserve Council boundaries?
- Does it preserve Memory ≠ Knowledge ≠ Tools ≠ Agents?
- Does it reduce implementation risk?
- Is adoption justified?

**Rule:** Architecture must not be rewritten to fit a tool.

---

## ADRs created

| ADR | File | Candidate | Layer |
| --- | --- | --- | --- |
| ADR-0004 | `Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md` | Hermes | Orchestration |
| ADR-0005 | `Architecture/decisions/ADR-0005-Memory-Runtime-Honcho.md` | Honcho | Memory Runtime |
| ADR-0006 | `Architecture/decisions/ADR-0006-Knowledge-Retrieval-ChromaDB.md` | ChromaDB | Knowledge Runtime |
| ADR-0007 | `Architecture/decisions/ADR-0007-Relationship-Layer-Graphify.md` | Graphify | Relationship Knowledge |
| ADR-0008 | `Architecture/decisions/ADR-0008-User-Interface-OpenWebUI.md` | Open WebUI | User Interface |

Template used: `Architecture/ai/Technology_Evaluation_ADR_Template.md`

Note: Relationship candidate is **Graphify** ([Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)). An interim mis-label as “Graphiti” was corrected; informal “Graphfy” spelling in earlier docs refers to the same intended product.

---

## Candidates evaluated

| Candidate | Role under evaluation |
| --- | --- |
| Hermes | Orchestration substrate for KORA conductor / agents / MCP path |
| Open WebUI | Chat interaction surface only |
| Honcho | User-modeling memory backend candidate |
| ChromaDB | Semantic retrieval index (not authority) |
| Graphify | Repo/docs → queryable relationship knowledge graph (local AST; no vector store) |

---

## Decisions

| ADR | Decision | Summary |
| --- | --- | --- |
| ADR-0004 Hermes | **Provisional Adopt** | Preferred orchestration substrate for a constrained spike; KORA identity + Council façade mandatory |
| ADR-0005 Honcho | **Spike** | Strong User Memory candidate; incomplete Memory_Runtime category/governance coverage |
| ADR-0006 ChromaDB | **Provisional Adopt** | Preferred retrieval store; repo/ADRs remain SoT |
| ADR-0007 Graphify | **Defer** | Preferred relationship candidate; deferred for thin-slice sequencing + skill-vs-runtime packaging validation |
| ADR-0008 Open WebUI | **Provisional Adopt** | Preferred UI candidate; not KORA; must route via orchestration façade |

No candidate was selected as a final production stack. No Reject outcomes in this wave.

---

## Deferred items

| Item | Why |
| --- | --- |
| Graphify implementation | Sequencing + validate skill vs durable KORA Relationship Knowledge runtime |
| Full Memory Runtime adoption | Honcho spike must prove category/governance mapping first |
| Docker / compose / installs | Explicitly out of scope for 13.8 |
| MCP server deployment | Later implementation |
| Final production cutover | Requires spikes + governance review |
| Models selection | Still deferred (`Models.md`) |
| Obsidian ingestion | External workflow only |

---

## Architecture consistency checks

| Requirement | Status |
| --- | --- |
| Technology fits architecture (not reverse) | ✅ ADRs gate on Architecture Fit / KORA Alignment |
| Council ≠ Agents preserved | ✅ ADR-0004 constraints; Council not generic workers |
| Memory ≠ Knowledge preserved | ✅ ADR-0005/0006 labeling & non-promotion rules |
| Tools ≠ decisions | ✅ MCP/tools remain later; Execute gated |
| Open WebUI ≠ KORA | ✅ ADR-0008 explicit |
| Hermes ≠ KORA identity | ✅ ADR-0004 branding/façade constraints |
| Databases ≠ SoT | ✅ Chroma/Graphify non-authority |
| Phase 12 infrastructure untouched | ✅ No compose/network changes |
| Required criteria covered | ✅ Fit, alignment, Council, boundaries, security, governance, maintenance, integration, migration, performance, community, ops, decision |

---

## Documents updated (references only)

- `Architecture/ai/KORA.md`
- `Architecture/ai/README.md`
- `Architecture/ai/FuturePlans.md`
- `Documentation/Phase13/Phase13_Roadmap.md`
- `Documentation/Phase13/README.md`
- `Architecture/standards/StandardsRoadmap.md`
- `Architecture/decisions/ADRIndex.md`

---

## Recommended next phase

**Thin vertical slice planning / constrained spike (post-13.8):**

1. Define KORA orchestration façade over Hermes (ADR-0004 constraints)
2. Route Open WebUI → façade (ADR-0008)
3. Prototype Chroma ingestion metadata contract (ADR-0006) against repo docs
4. Run Honcho spike mapping to Memory categories (ADR-0005)
5. Reopen Graphify (ADR-0007) only after retrieval path exists and packaging fit is clear

Still no unbounded automation; still no Phase 12 regression.
