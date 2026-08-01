# KORA Production Service Topology

**Status:** Canonical logical service topology (Phase 13.15)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** These logical services become Docker Compose services in Phase 14. This phase defines **what**, not compose **how**.

---

## How to Read Service Cards

Each logical service may be:

- A separate process/container later, or  
- Co-located inside another service for Solo  

Either way, responsibilities and contracts remain.

---

## 1. Open WebUI — UI Layer

| Field | Value |
| --- | --- |
| **Purpose** | User interaction surface |
| **Architectural responsibility** | Capture requests; render recommendations/explanations; present **KORA** identity |
| **Runtime Profile support** | Solo / Simulated / Distributed / Hybrid |
| **Persistent data ownership** | UI session/chat buffers only—not Memory SoT, not Knowledge SoT |
| **Dependencies** | KORA Runtime (Phase 14.1 Solo path) |
| **Required interfaces** | Chat request/response via KORA OpenAI-compatible API; auth (later); explainability display hooks |
| **Optional interfaces** | Voice/mobile later |
| **Startup order** | After orchestration reachable (or degraded “unavailable”) |
| **Shutdown order** | Early (drain users first) |
| **Health expectations** | Serves UI; can reach orchestration |
| **Scaling expectations** | Horizontal UI replicas later |
| **Related ADRs** | ADR-0008 |

---

## 2. Hermes — Orchestration Layer

| Field | Value |
| --- | --- |
| **Purpose** | Orchestration substrate |
| **Architectural responsibility** | Route turns into KORA; optional agent spawn hooks; MCP transport later |
| **Runtime Profile support** | Solo (thin/optional) · Simulated · Distributed (primary) · Hybrid |
| **Persistent data ownership** | Substrate state only—not product identity; not Knowledge SoT |
| **Dependencies** | KORA Runtime; models as configured in Phase 14 |
| **Required interfaces** | Invoke KORA conductor path |
| **Optional interfaces** | Multi-agent, channels |
| **Startup order** | Before UI traffic when used; after or with KORA. **Stage 1 Solo:** optional / not on primary chat path |
| **Shutdown order** | After UI drain; before tearing KORA mid-flight if possible |
| **Health expectations** | Accepts routed requests; does not claim to be KORA |
| **Scaling expectations** | Scale with care; session continuity |
| **Related ADRs** | ADR-0004 |

---

## 3. KORA Runtime

| Field | Value |
| --- | --- |
| **Purpose** | Product conductor / synthesis / identity |
| **Architectural responsibility** | Enforce Runtime Contracts; own Response identity |
| **Runtime Profile support** | All profiles |
| **Persistent data ownership** | Ephemeral request state; not Memory/Knowledge stores |
| **Dependencies** | Classification/CI/Assembly (co-located or separate); Memory; Knowledge; Tools; Council |
| **Required interfaces** | Full vertical-slice conductor API (conceptual) |
| **Optional interfaces** | Expansion loops; approval UX hooks |
| **Startup order** | Core—before accepting user work |
| **Shutdown order** | After in-flight synthesis completes or times out |
| **Health expectations** | Contracts enforceable; can classify and refuse safely |
| **Scaling expectations** | Prefer single conductor initially |
| **Related ADRs** | Architecture docs; ADR-0004 façade constraints |

---

## 4. Classification Engine

| Field | Value |
| --- | --- |
| **Purpose** | Request classification before retrieval |
| **Architectural responsibility** | `Runtime_Contracts` Classification; feeds strategies |
| **Runtime Profile support** | All (usually co-located in KORA for Solo) |
| **Persistent data ownership** | None required |
| **Dependencies** | KORA Runtime |
| **Required interfaces** | Request → classification record |
| **Optional interfaces** | Ambiguity/clarification signals |
| **Startup / Shutdown** | With KORA Runtime when co-located |
| **Health expectations** | Always classifies before retrieval |
| **Scaling expectations** | Scales with KORA |
| **Related ADRs** | — (architecture) |

---

## 5. Context Intelligence

| Field | Value |
| --- | --- |
| **Purpose** | Strategy selection, selective retrieval plan, ranking/budgets |
| **Architectural responsibility** | `Context_Intelligence.md` / `Retrieval_Strategies.md` / `Context_Ranking.md` |
| **Runtime Profile support** | All |
| **Persistent data ownership** | None |
| **Dependencies** | Classification; Memory/Knowledge/Tools read interfaces |
| **Required interfaces** | Plan + ranked candidates + skip logs |
| **Optional interfaces** | Mid-session expansion |
| **Startup / Shutdown** | With KORA when co-located |
| **Health expectations** | Never global-retrieves by default |
| **Scaling expectations** | With KORA |
| **Related ADRs** | ADR-0005/0006 as backends |

---

## 6. Context Assembly

| Field | Value |
| --- | --- |
| **Purpose** | Build provenance-labeled reasoning package |
| **Architectural responsibility** | `Context_Assembly.md` |
| **Runtime Profile support** | All |
| **Persistent data ownership** | None (ephemeral packages) |
| **Dependencies** | Ranked candidates; Council selection metadata |
| **Required interfaces** | Assembled context package |
| **Optional interfaces** | Re-assembly on expansion |
| **Startup / Shutdown** | With KORA when co-located |
| **Health expectations** | No laundering; provenance intact |
| **Scaling expectations** | With KORA |
| **Related ADRs** | — |

---

## 7. Council Runtime

| Field | Value |
| --- | --- |
| **Purpose** | Realize Council Dynamics under the active Runtime Profile |
| **Architectural responsibility** | Selection/Deliberation/Voting semantics; contributions |
| **Runtime Profile support** | Solo (conceptual) · Simulated · Distributed · Hybrid |
| **Persistent data ownership** | Contribution records ephemeral unless audited |
| **Dependencies** | Assembled context; KORA facilitation |
| **Required interfaces** | Contributions → KORA synthesis |
| **Optional interfaces** | Independent member runtimes (Distributed) |
| **Startup order** | With/after KORA |
| **Shutdown order** | Drain contributions; no orphan Execute |
| **Health expectations** | Members ≠ agents; disagreement preservable |
| **Scaling expectations** | Member scale only in Distributed |
| **Related ADRs** | ADR-0004 when Distributed |

---

## 8. Memory Runtime (Honcho candidate)

| Field | Value |
| --- | --- |
| **Purpose** | Continuity Memory under governance |
| **Architectural responsibility** | `Memory_Runtime.md`; ADR-0005 constraints |
| **Runtime Profile support** | All |
| **Persistent data ownership** | User/Project/Operational Memory (governed); **no secrets** |
| **Dependencies** | KORA/Context Intelligence read path; approval UX |
| **Required interfaces** | Query; candidate propose; approve/delete/correct |
| **Optional interfaces** | Dialectic features only if gated |
| **Startup order** | Before preference/personal traffic depends on it |
| **Shutdown order** | Flush safely; no auto-commit on crash |
| **Health expectations** | Empty Memory valid; no silent durable writes |
| **Scaling expectations** | Single store initially |
| **Related ADRs** | ADR-0005 |

---

## 9. Knowledge Runtime (ChromaDB candidate)

| Field | Value |
| --- | --- |
| **Purpose** | Semantic retrieval index over governed sources |
| **Architectural responsibility** | `Knowledge_Runtime.md`; non-SoT |
| **Runtime Profile support** | All |
| **Persistent data ownership** | Index/embeddings—**rebuildable**; SoT remains repo/ADRs |
| **Dependencies** | Ingestion from governed docs (Phase 14 process) |
| **Required interfaces** | Query with provenance/authority/freshness metadata |
| **Optional interfaces** | Reindex jobs |
| **Startup order** | Before architecture/knowledge-heavy traffic |
| **Shutdown order** | Quiesce queries; index consistent |
| **Health expectations** | Degrade with gaps; never invent SoT |
| **Scaling expectations** | Single index initially |
| **Related ADRs** | ADR-0006 |

---

## 10. Tool Runtime

| Field | Value |
| --- | --- |
| **Purpose** | Live environment evidence |
| **Architectural responsibility** | `Tools.md`; Tools ≠ Decisions |
| **Runtime Profile support** | All (may be stubbed early) |
| **Persistent data ownership** | Ephemeral evidence; audit optional |
| **Dependencies** | MCP Gateway; permission model |
| **Required interfaces** | Read tools; gated Execute |
| **Optional interfaces** | Broader MCP toolsets later |
| **Startup order** | After MCP Gateway if used |
| **Shutdown order** | Cancel in-flight; never leave Execute hanging |
| **Health expectations** | Unavailable → uncertainty |
| **Scaling expectations** | Constrain Execute; scale Read cautiously |
| **Related ADRs** | Later tool ADRs; MCP architecture |

---

## 11. MCP Gateway

| Field | Value |
| --- | --- |
| **Purpose** | Protocol gateway to external/homelab systems |
| **Architectural responsibility** | `MCP.md` conceptual → concrete in Phase 14 |
| **Runtime Profile support** | All when Tools enabled |
| **Persistent data ownership** | Config only—not Knowledge |
| **Dependencies** | Tool Runtime; Phase 12 systems (least privilege) |
| **Required interfaces** | Tool discovery/invoke under permissions |
| **Optional interfaces** | Multiple MCP servers |
| **Startup / Shutdown** | With Tool Runtime |
| **Health expectations** | Gateway up ≠ Execute allowed |
| **Scaling expectations** | Controlled |
| **Related ADRs** | Future MCP ADRs |

---

## 12. Explainability Service

| Field | Value |
| --- | --- |
| **Purpose** | Structure explanation objects |
| **Architectural responsibility** | `Explainability.md` |
| **Runtime Profile support** | All (co-locate in KORA for Solo) |
| **Persistent data ownership** | None required |
| **Dependencies** | Classification/strategy/evidence/contributors from KORA path |
| **Required interfaces** | Explanation object for UI |
| **Optional interfaces** | Standalone service later |
| **Startup / Shutdown** | With KORA when co-located |
| **Health expectations** | No raw CoT |
| **Scaling expectations** | With KORA |
| **Related ADRs** | — |

---

## 13. Relationship Runtime (Graphify — future)

| Field | Value |
| --- | --- |
| **Purpose** | Relationship knowledge graph |
| **Architectural responsibility** | Optional complement to Knowledge |
| **Runtime Profile support** | Hybrid/later |
| **Persistent data ownership** | Rebuildable graph; not SoT |
| **Dependencies** | ADR-0007 adoption |
| **Required interfaces** | None until adopted |
| **Optional interfaces** | Graph query |
| **Startup / Shutdown** | N/A until Stage 7 |
| **Health expectations** | Off by default |
| **Scaling expectations** | Deferred |
| **Related ADRs** | ADR-0007 (Defer) |

---

## Solo Initial Pack (Phase 14 Stage 1 intent)

Logical minimum often co-located:

- Open WebUI  
- Hermes (thin) and/or direct KORA entry  
- KORA Runtime (includes Classification, Context Intelligence, Assembly, Council Solo, Explainability)  

Memory, Knowledge, Tools, MCP, Relationship: enable per `Rollout_Strategy.md`.

---

## Document Map

| Document | Role |
| --- | --- |
| `Production_Service_Topology.md` (this file) | Service cards |
| `Deployment_Topology.md` | End-to-end layout |
| `Rollout_Strategy.md` | When to enable each domain |
