# Phase 14 — KORA Production Runtime Implementation

**Status:** ✅ Phase 14 complete; **🟡 Phase 15 started** (Council foundation on `phase15-council` branch)

**Prerequisite:** Phase 13 complete (architecture through 13.15)  

**Deployment substrate:** Docker Compose under Homelab governance and Phase 12 production baseline  

**Primary goal:** Implement KORA production runtime in staged slices without rewriting Phase 13 architecture.

**Master roadmap entry:** `Architecture/standards/StandardsRoadmap.md`  
**Architecture blueprint:** `Architecture/ai/Production_Architecture.md`  
**Rollout companion:** `Architecture/ai/Rollout_Strategy.md`

---

## Phase 14 closeout — final architecture (Hermes/KORA migration)

**Status:** ✅ Complete (2026-08-11)

Phase 14 ended with a migration from the standalone KORA Runtime to KORA-as-Hermes-Agent.

| Decision | Detail |
| --- | --- |
| Hermes | v0.17.0 — the generic agent/runtime platform |
| KORA | A real **Hermes Agent** (head intelligence/governance agent hosted inside Hermes); no standalone container, no custom orchestration runtime, no Hermes fork |
| Runtime | Hermes api_server (`:8642`, model `KORA`) is the Open WebUI entry |
| Memory | **Honcho** (canonical, workspace `kora`, peer `user`, `pinUserPeer: true`) via the Hermes native honcho provider |
| Knowledge | **Chroma** external container (`kora-chromadb`) |
| Relationships | **Graphify** external container |
| Inference | **Ollama** (`http://ollama:11434/v1`) |
| Tools/MCP | Via Hermes tool runtime |
| KORA chat model | Controlled by Hermes `config.yaml model.default` (currently `qwen3:8b`) |
| Honcho models | Independently configured in Honcho's env (`DIALECTIC_*`, `DREAM_*`) — decoupled from KORA's chat model |
| User isolation | KORA visible to Trevor only; Tracy (partner) restricted to permitted Ollama models via Open WebUI model access control |
| Open WebUI | Cannot select KORA's underlying Hermes model per request (Hermes v0.17.0 api_server uses `model.default`) |

Retirement record: `Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md`.
Commits: `9ee4b59` (retirement), `367c783` (pre-retirement checkpoint).

---

## Phase overview

| Sub-phase | Title | Status |
| --- | --- | --- |
| 14.1 | Runtime Foundation (KORA + Hermes + Open WebUI + Ollama) | ✅ Complete (2026-08-01) |
| 14.2 Preflight | Memory Runtime Preflight | ✅ Complete (2026-08-01) |
| 14.2A | Event Bus + Memory Runtime Foundation | ✅ Complete (2026-08-03) |
| 14.2B | Approval integration + durable Memory adapter | ✅ Complete |
| 14.2C | Knowledge Ingestion Foundation | ✅ Complete |
| 14.2D | Production Validation | ✅ Complete |
| 14.3 | Knowledge Platform | ✅ Complete (2026-08-09) |
| 14.4 | Knowledge Graph | ✅ Complete (2026-08-09) |
| 14.5 | Tool Platform | ✅ Complete (2026-08-09) |
| 15 | Council & Intelligence | 🟡 Started (foundation, 2026-08-12) |
| 16 | Automation & Autonomous Workflows | ⏳ Planned |

---

## Hard rules (all sub-phases)

- KORA remains the sole user-facing product identity
- Technology adapts to Phase 13 contracts—not the reverse
- Memory ≠ Knowledge; Knowledge ≠ Tools; Council ≠ Agents; Tools ≠ Decisions
- Context Intelligence precedes retrieval
- Explainability and provenance preserved; no raw CoT exposure
- Graphify is an intentional component implemented in Phase 14.4 (Knowledge Graph); complementary to Chroma (ADR-0007)
- Obsidian remains an external workflow only
- No Phase 12 regression without explicit approval
- Solo Runtime is the initial production profile target

---

## Hardware-aware design principle

> KORA's architecture must not be coupled to the capabilities of the current inference hardware.

Current hardware may constrain model size, context size, number of concurrent models, inference parallelism, Council member count, and response latency. These are **deployment constraints, not architectural constraints**.

The architecture supports a progression from:

```text
Small local model
      ↓
Sequential Council
      ↓
Limited members
```

to:

```text
Larger local models
      ↓
Multiple specialist models
      ↓
Parallel Council
```

without architectural redesign. Do not add hardware requirements to the roadmap; hardware limits affect deployment configuration and model selection only.

---

## Capability ladder

The remaining roadmap is best understood as a progression of user-visible capabilities:

```text
Phase 14.2
KORA can safely store knowledge.
        ↓
Phase 14.3
KORA can understand and retrieve knowledge.
        ↓
Phase 14.4
KORA can understand relationships between knowledge.
        ↓
Phase 14.5
KORA can interact with the world.
        ↓
Phase 15
KORA can reason through the Council.
        ↓
Phase 16
KORA can perform autonomous workflows.
```

---

## Architectural dependency

The roadmap follows a capability progression:

```text
Knowledge Platform
       ↓
Knowledge Graph
       ↓
Tool Platform
       ↓
Council & Intelligence
       ↓
Automation & Autonomous Workflows
```

This is a **capability progression**, not necessarily a strict implementation dependency for every individual feature. In particular:

- Council may be developed using smaller models.
- Council does not require maximum hardware.
- Automation depends on mature Tool and Council governance.
- Graphify is complementary to vector retrieval.
- Open WebUI remains the UI layer.

---

## Roadmap simplification rule

Do not create additional numbered phases for embeddings, RAG, vector databases, ChromaDB, Graphify, MCP, Context Assembly, individual Council members, or autonomous agents. These are capabilities/components **within** the existing phases. This prevents roadmap fragmentation.

---

## Phase 14.1 — Runtime Foundation

**Objective:** Stand up the minimum production path: inference + orchestration substrate + UI + KORA conductor façade.

**Status:** ✅ Complete (2026-08-01)

> **Superseded note (closeout).** This phase's "KORA Runtime (Solo conductor façade)" was
> the original integration. The **final architecture** replaces the standalone runtime
> with **KORA-as-Hermes-Agent**; `services/kora` is retired. KORA integration itself is
> retained and is now hosted inside Hermes.

**Includes:**

- Ollama (local inference; models preserved at `/hive/ollama`)
- Hermes (thin execution layer; not identity; not on primary Solo chat path)
- Open WebUI (UI only; ADR-0008; wired to KORA)
- KORA Runtime (Solo: classify → strategy → assemble → synthesize → explain)

**Maps to:** Rollout Stage 1 (Solo Runtime)

**Implemented path:** `User → Open WebUI → KORA → Ollama → Response`

**Acceptance:**

- User talks to **KORA**, not Hermes/Open WebUI/Ollama as product identity
- End-to-end chat path works under Stage 1 Runtime Contracts
- Execute/Administrative refused by default
- Phase 12 fabric untouched except governed AI attachments

**Artifacts:** `AI/`, `services/{kora,ollama,open-webui,hermes}/`, `Validation/Phase14.1/`, `Documentation/Phase14/Phase14.1/`

---

## Phase 14.2 — Foundation

**Capability:** **KORA can safely store knowledge.** (Complete)

> **Superseded note (closeout).** The custom Memory Runtime / Event Bus / Approval Engine
> described below (14.2A–14.2D) were **implemented, evaluated, and retired** in the final
> architecture. **Honcho is now the canonical memory backend**, integrated via the
> **Hermes native honcho provider** — no separate KORA Memory Service is required. The
> historical implementation remains in Git history and the Phase 14 backup.

**Objective:** Enable governed continuity Memory (Honcho candidate per ADR-0005) and the Knowledge ingestion foundation. This phase established:

- Knowledge domain
- Knowledge ingestion
- `KnowledgeDocument`
- `KnowledgeStore` abstraction
- Memory foundation
- Approval-gated durable memory
- Runtime / EventBus foundation
- Production validation

**Preflight (2026-08-01):** ✅ Complete — see `Phase14.2/` (Ollama/Hermes ownership aligned; Open WebUI SoT boundaries confirmed; Memory approval UX designed). Durable Honcho writes **not** enabled in preflight.

### Phase 14.2A — Foundation

**Status:** ✅ Complete (2026-08-03)

**Includes:**

- General internal Event Bus abstraction (ADR-14.2A-001)
- JSON-serializable event envelopes and in-process adapter
- Logical Memory Runtime and Approval Engine services in the KORA process
- Ephemeral proposal model, eligibility, deduplication, expiry, and audit state
- Read-only proposal status APIs
- No durable storage or event replay

**Artifacts:** `AI/KORA/Runtime/app/`, `services/{event-bus,memory-runtime}/`,
`Documentation/Phase14/Phase14.2A/`, `Validation/Phase14.2A/`

### Phase 14.2B — Approval and durable Memory

**Status:** ✅ Complete

**Includes (completed):**

- Approval surface and authenticated transition APIs
- Approval-gated durable adapter (per `Phase14.2/Memory_Approval_UX.md`)
- Memory proposal status APIs and approval workflow APIs (read-only status access; durable Memory retrieval deferred)

**Maps to:** Rollout Stage 3

**Acceptance (14.2B completed):**

- Memory proposal status APIs are available (read‑only)
- Approval workflow APIs are available (read‑only status access)
- No silent durable writes (writes only after explicit approval)
- Durable Memory retrieval is deferred to a later phase
- Explicit approve/reject UX before commit

---

### Phase 14.2C — Knowledge Ingestion Foundation

**Status:** ✅ Complete

**Objective:** Establish the governed ingestion boundary for Knowledge (what exists), isolated from Memory (what KORA remembers).

**Includes (completed):**

- `KnowledgeDocument` immutable model with deterministic `doc_id`
- `KnowledgeIngestionEvent` on the shared EventBus (`knowledge.*` namespace)
- Local-file ingestion processor (read, normalize, extract metadata)
- Pluggable `KnowledgeStore` abstraction + in-memory implementation
- Internal `KnowledgeIngestionService` (no HTTP endpoints; deferred to later phases)

**Boundaries preserved:**

- Knowledge never imports Memory; Memory never imports Knowledge
- Ingestion does not create Memory proposals automatically
- Chat retrieval of Knowledge remains disabled (Phase 14.3)

---

### Phase 14.2D — Production Validation

**Status:** ✅ Complete

**Objective:** Validate the production readiness of the KORA foundation (Runtime, Memory, Knowledge) without redesigning or expanding it.

**Includes (completed):**

- Baseline regression: 41 tests (Runtime 31 + Knowledge 10) all passing
- Added 14 production-readiness tests (55 total): config loading, health endpoint, graceful degradation, chat-path store isolation, Knowledge↔Memory isolation
- Architecture compliance audit (boundaries, write paths, namespaces, deferred tech)
- Docker build + compose up + health + restart validation
- Documentation: Phase 14.2D docs, roadmap reconciliation

**Validation artifacts:** `Documentation/Phase14/Phase14.2D/`, `Validation/Phase14.2D/`

---

## Phase 14.3 — Knowledge Platform

**Capability:** **KORA can understand and retrieve knowledge.**

**Status:** ✅ Implemented and validated (2026-08-09)

> **Superseded note (closeout).** The Knowledge Platform's in-runtime Python implementation
> was retired with the standalone runtime. In the final architecture, Knowledge is an
> **external service** — **Chroma** (`kora-chromadb`) — that the KORA Hermes Agent accesses
> as an external service.

**Purpose:** Transform Knowledge from passive storage into a production knowledge platform.

The Knowledge Service owns document ingestion, indexing, retrieval, and knowledge enrichment. ChromaDB provides vector indexing and retrieval; these are infrastructure components owned by the Knowledge Service, not peer services.

**Implemented capabilities:**

- Knowledge Service
- Embedding generation
- ChromaDB integration
- Incremental indexing
- Retrieval APIs
- Basic RAG
- Knowledge context construction
- Event-driven indexing
- Provenance-aware retrieval
- Production validation

**Goal:** The outcome is a meaningful user-visible capability — **KORA can answer questions using its indexed Knowledge**. Phase 14.3 should not become an advanced RAG research phase.

**Canonical architecture:** [Phase 14.3 Knowledge Platform Architecture](Phase14.3/Knowledge_Platform_Architecture.md) — the ratified Phase 14.3 implementation contract (service boundaries, embedding strategy, index lifecycle, retrieval/RAG boundary, Memory and Open WebUI boundaries, phase ownership).

**Explicitly defer:**

- Graph reasoning
- Graph retrieval
- Agentic retrieval
- Autonomous search loops
- Council (Phase 15)
- Tool execution (Phase 14.5)
- Autonomous workflows (Phase 16)

**Acceptance (planned):**

- Architecture questions retrieve Knowledge with provenance
- Index ≠ SoT (repo/ADRs remain authority)
- Preference paths keep Knowledge budget at zero
- Conflicts dual-cite; no silent authority pick

---

## Phase 14.4 — Knowledge Graph

**Capability:** **KORA can understand relationships between knowledge.**

**Status:** ✅ Implemented and validated (2026-08-09)

> **Superseded note (closeout).** Graphify remains an **external relationship/graph
> service** that the KORA Hermes Agent accesses as an external service. The retired runtime
> was the in-process graph exporter; the Graphify container is unchanged.

**Purpose:** Add graph-based understanding to complement vector retrieval.

Graphify is an intentional architectural component. Its purpose is NOT to replace vector search; it provides relationship modeling, traversal, and visualization. ChromaDB provides semantic/vector retrieval; Graphify provides relationship modeling, traversal, and visualization. Graphify does NOT become the authoritative Knowledge source. The Knowledge Service remains the architectural owner of the capability.

**Implemented capabilities:**

- Graphify integration (Docker Compose MCP HTTP server)
- Entity extraction (deterministic rule-based)
- Relationship extraction (markdown headings, links, wikilinks)
- Graph synchronization (event-driven via EventBus)
- Graph queries (get_node, get_neighbors, shortest_path, graph_stats)
- Graph visualization (graph.json served by Graphify)
- Hybrid vector/graph retrieval (CombinedRetrievalService)

**Out of scope:**

- Replacing ChromaDB vector retrieval
- MCP (Tool Platform, Phase 14.5)
- Tool Runtime
- Council (Phase 15)
- Autonomous agents (Phase 16)

---

## Phase 14.5 — Tool Platform

**Capability:** **KORA can interact with the world.**

**Status:** ✅ Implemented and validated (2026-08-09)

> **Superseded note (closeout).** The in-runtime Tool Platform Python was retired with the
> standalone runtime. In the final architecture, **Hermes provides the runtime/tool
> execution**; MCP/tool capability is external to KORA and delivered through Hermes' tool
> runtime.

**Purpose:** Introduce runtime interaction with live systems.

**Implemented capabilities:**

- Tool Service (ToolPlatform facade)
- MCP integration (generic MCP Streamable HTTP client + provider)
- Local tools (read-only Ollama tools)
- Tool registry
- Tool permissions / authorization (risk + approval governance)
- Runtime integration (operational queries select tools; read-only auto-invoked)

**Design note:** The Tool Platform provides **controlled access** to live system state and actions. Do not introduce autonomous behavior into Phase 14.5. Tools provide capabilities; the Council (Phase 15) and Automation (Phase 16) phases determine how those capabilities are reasoned about and eventually automated. Graphify's MCP integration is a Knowledge Graph integration, not the Tool Platform.

**Out of scope:**

- Council (Phase 15)
- Autonomous agents (Phase 16)

---

## Phase 15 — Council & Intelligence

**Capability:** **KORA can reason through the Council.**

**Status:** 🟡 Started (foundation, 2026-08-12). The smallest correct foundation is
implemented on branch `phase15-council`: KORA remains the head agent; Council members
are Hermes-native subagents invoked via `delegate_task` (delegation toolset enabled for
KORA); canonical member content (`Architecture/ai/Council/`) is mounted read-only and
loaded via the `kora.council_member` tool. No new containers/runtime/framework.
See `Documentation/Phase15/README.md`.

**Purpose:** Establish Council orchestration and reasoning. Phase 15 is explicitly **hardware-agnostic**: the goal is the Council architecture, NOT large models or expensive parallel inference.

**Hardware-agnostic design.** The Council is designed so it can operate with smaller local models, sequential inference, configurable member count, configurable model assignment, configurable parallelism, and future larger or heterogeneous models. The architecture must not assume every Council member runs a large model simultaneously.

For example, the initial implementation may use:

```text
Council
 ├── NOVA
 ├── IRIS
 ├── TALIA
 └── ALUMA
       │
       ▼
Sequential local inference
       │
       ▼
Council synthesis
```

using a small local model. A future deployment may instead use:

```text
Council
 ├── specialist model
 ├── specialist model
 ├── specialist model
 └── synthesis model
```

The architecture supports both without redesign. Council members do not inherently require separate models; multiple Council archetypes may initially use the same local model with different role/system prompts. Hardware limitations affect deployment configuration and model selection, not the fundamental Council architecture.

**Phase 15 should establish:**

- Council member definitions
- Archetypes
- Council orchestration
- Deliberation protocol
- Context boundaries
- Model/member configuration
- Sequential vs parallel execution configuration
- Synthesis
- Failure handling
- Observability
- Governance boundaries

**Explicitly avoid assuming:**

- Large models
- Multiple GPUs
- Parallel inference
- Seven simultaneous models
- Cloud inference
- High-end hardware

The architecture should remain portable to stronger future hardware.

**Acceptance (planned):**

- Council members ≠ agents
- Disagreement preservable
- UX identity remains KORA
- Dynamics semantics held

---

## Phase 16 — Automation & Autonomous Workflows

**Capability:** **KORA can perform autonomous workflows.**

**Purpose:** Enable governed autonomous workflows. Phase 16 comes AFTER the Knowledge (14.3), Graph (14.4), Tool (14.5), and Council (Phase 15) foundations.

**Planned capabilities may include:**

- Autonomous planning
- Workflow execution
- Tool orchestration
- Approval policies
- Execution boundaries
- Monitoring
- Rollback / recovery
- Self-healing proposals
- Pull request generation
- Automated audits
- Long-running workflows

**Governance:** Automation must remain governed. Council does not automatically grant permission to execute actions. **Reasoning and execution remain separate capabilities.**

**Acceptance (planned):**

- Agents are workers, not Council seats
- Tools ≠ Decisions still holds
- Human approval for Administrative/Execute class actions
- Rollback disables workflows without collapsing KORA identity

---

## Relationship to Rollout_Strategy.md

| Phase | Rollout_Strategy stage |
| --- | --- |
| 14.1 | Stage 1 Solo (+ inference foundation) |
| 14.2A/B | Stage 3 Memory |
| 14.2C | Knowledge Ingestion Foundation (Stage 4 prep) |
| 14.2D | Production Validation (cross-cutting) |
| 14.3 | Stage 4 Knowledge |
| 14.4 | Knowledge Graph (complements Stage 4 vector retrieval) |
| 14.5 | Stage 5 Tools |
| 15 | Stage 2 Simulated Council (+ Context Intelligence hardening) |
| 16 | Agents / workflows (beyond core rollout stages 1–6) |

Order differs slightly from numeric Rollout stages where foundation and context hardening must precede Memory/Knowledge production cutover. **Phase 14 numbering is the implementation schedule; Rollout_Strategy remains the capability-enablement model.**

---

## Explicit non-goals (until scheduled)

- Graphify / Relationship Runtime: intentional component, scheduled for Phase 14.4 (ADR-0007 Planned; not yet implemented)
- Rewriting Phase 13 architecture for vendor convenience
- Ungoverned automation of Phase 12 infrastructure
- Treating Phase 14 as the long-term “AI Automation” governance program (that remains a later phase)

---

## Success criteria (Phase 14 overall)

Phase 14 is complete when:

- Solo (then Simulated) production path is live under contracts
- Memory and Knowledge runtimes are governed and separable
- Knowledge Platform (ingestion, embeddings, vector retrieval) is validated in production
- Knowledge Graph complements vector retrieval (Phase 14.4)
- Tools/MCP Read path exists with gated Execute
- Phase 12 baseline remains intact

---

## Next after Phase 14

- **Phase 15 — Council & Intelligence**: simulated Council fidelity and Context Intelligence hardening.
- **Phase 16 — Automation & Autonomous Workflows**: governed agent workflows.
- Longer-term **AI Automation** (governance assistant workflows across the homelab) remains a subsequent program phase—not a substitute for finishing the roadmap.
