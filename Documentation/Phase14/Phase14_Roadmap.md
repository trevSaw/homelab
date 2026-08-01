# Phase 14 — KORA Production Runtime Implementation

**Status:** 🟡 Planned (roadmap defined; implementation not started)  

**Prerequisite:** Phase 13 complete (architecture through 13.15)  

**Deployment substrate:** Docker Compose under Homelab governance and Phase 12 production baseline  

**Primary goal:** Implement KORA production runtime in staged slices without rewriting Phase 13 architecture.

**Master roadmap entry:** `Architecture/standards/StandardsRoadmap.md`  
**Architecture blueprint:** `Architecture/ai/Production_Architecture.md`  
**Rollout companion:** `Architecture/ai/Rollout_Strategy.md`

---

## Phase overview

| Sub-phase | Title | Status |
| --- | --- | --- |
| 14.1 | Runtime Foundation (KORA + Hermes + Open WebUI + Ollama) | ✅ Complete (2026-08-01) |
| 14.2 | Memory Runtime | 🟡 Planned |
| 14.3 | Knowledge Runtime (RAG) | 🟡 Planned |
| 14.4 | Context Assembly Engine | 🟡 Planned |
| 14.5 | Tool & MCP Runtime | 🟡 Planned |
| 14.6 | Council Integration | 🟡 Planned |
| 14.7 | Autonomous Workflows & Agent Orchestration | 🟡 Planned |

---

## Hard rules (all sub-phases)

- KORA remains the sole user-facing product identity
- Technology adapts to Phase 13 contracts—not the reverse
- Memory ≠ Knowledge; Knowledge ≠ Tools; Council ≠ Agents; Tools ≠ Decisions
- Context Intelligence precedes retrieval
- Explainability and provenance preserved; no raw CoT exposure
- Graphify remains deferred until ADR-0007 changes
- Obsidian remains an external workflow only
- No Phase 12 regression without explicit approval
- Solo Runtime is the initial production profile target

---

## Phase 14.1 — Runtime Foundation

**Objective:** Stand up the minimum production path: inference + orchestration substrate + UI + KORA conductor façade.

**Status:** ✅ Complete (2026-08-01)

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

## Phase 14.2 — Memory Runtime

**Objective:** Enable governed continuity Memory (Honcho candidate per ADR-0005).

**Includes (planned):**

- Memory Runtime service
- Approval-gated durable writes
- Preference / personal / project Memory read paths

**Maps to:** Rollout Stage 3

**Acceptance (planned):**

- Preference strategies query Memory only
- No silent durable writes
- Empty Memory valid
- Memory never labeled as Knowledge

---

## Phase 14.3 — Knowledge Runtime (RAG)

**Objective:** Enable Knowledge retrieval index over governed sources (ChromaDB candidate per ADR-0006).

**Includes (planned):**

- Knowledge Runtime / RAG index
- Ingestion from repo/ADRs/standards
- Provenance, authority, freshness metadata

**Maps to:** Rollout Stage 4

**Acceptance (planned):**

- Architecture questions retrieve Knowledge with provenance
- Index ≠ SoT (repo/ADRs remain authority)
- Preference paths keep Knowledge budget at zero
- Conflicts dual-cite; no silent authority pick

---

## Phase 14.4 — Context Assembly Engine

**Objective:** Productionize Context Intelligence + ranking + assembly as first-class runtime behavior (may already be co-located in 14.1; this phase hardens and validates it).

**Includes (planned):**

- Classification-driven retrieval strategies
- Ranking, budgets, pruning
- Provenance-labeled Context Assembly packages
- Explainability fields for strategy / stores / pruning

**Maps to:** Phase 13.12–13.13 contracts in production

**Acceptance (planned):**

- Re-run Phase 13.13 scenario set against production path
- No global retrieval by default
- Assembly receives only allowed, ranked, budgeted context

---

## Phase 14.5 — Tool & MCP Runtime

**Objective:** Enable live environment evidence via Tool Runtime and MCP Gateway.

**Includes (planned):**

- Tool Runtime
- MCP Gateway
- Read tools first; Execute gated by approval UX

**Maps to:** Rollout Stage 5

**Acceptance (planned):**

- Operational questions are Tools-first
- Missing tools → uncertainty, not fabrication
- No ungated Execute; no Phase 12 blast-radius surprises

---

## Phase 14.6 — Council Integration

**Objective:** Raise Council fidelity from Solo conceptual → Simulated (and prepare Distributed later).

**Includes (planned):**

- Simulated Council structured prompting
- Selection / deliberation / synthesis wiring to Dynamics
- Contributor explainability
- Optional path toward Distributed member runtimes (not required to close 14.6)

**Maps to:** Rollout Stages 2 and (prep) 6

**Acceptance (planned):**

- Council members ≠ agents
- Disagreement preservable
- UX identity remains KORA
- Dynamics semantics held

---

## Phase 14.7 — Autonomous Workflows & Agent Orchestration

**Objective:** Enable temporary agents and governed autonomous workflows **after** foundation, memory, knowledge, context, tools, and council paths are stable.

**Includes (planned):**

- Agent create/evaluate/terminate lifecycle
- Workflow orchestration under KORA / Hermes
- Strict permission and audit boundaries
- No unbounded self-modification of production

**Maps to:** Agents.md + Tools governance; not a substitute for Council

**Acceptance (planned):**

- Agents are workers, not Council seats
- Tools ≠ Decisions still holds
- Human approval for Administrative/Execute class actions
- Rollback disables workflows without collapsing KORA identity

---

## Relationship to Rollout_Strategy.md

| Phase 14 | Rollout_Strategy stage |
| --- | --- |
| 14.1 | Stage 1 Solo (+ inference foundation) |
| 14.2 | Stage 3 Memory |
| 14.3 | Stage 4 Knowledge |
| 14.4 | Cross-cutting Context Intelligence / Assembly hardening |
| 14.5 | Stage 5 Tools |
| 14.6 | Stage 2 Simulated (+ Distributed prep) |
| 14.7 | Agents / workflows (beyond core rollout stages 1–6) |

Order differs slightly from numeric Rollout stages where foundation and context hardening must precede Memory/Knowledge production cutover. **Phase 14 numbering is the implementation schedule; Rollout_Strategy remains the capability-enablement model.**

---

## Explicit non-goals (until scheduled)

- Graphify / Relationship Runtime (ADR-0007 Defer)
- Rewriting Phase 13 architecture for vendor convenience
- Ungoverned automation of Phase 12 infrastructure
- Treating Phase 14 as the long-term “AI Automation” governance program (that remains a later phase)

---

## Success criteria (Phase 14 overall)

Phase 14 is complete when:

- Solo (then Simulated) production path is live under contracts
- Memory and Knowledge runtimes are governed and separable
- Context Intelligence/Assembly is validated in production
- Tools/MCP Read path exists with gated Execute
- Council integration preserves Dynamics and identity
- Agent workflows (if enabled) remain bounded and auditable
- Phase 12 baseline remains intact

---

## Next after Phase 14

Longer-term **AI Automation** (governance assistant workflows across the homelab) remains a subsequent program phase—not a substitute for finishing 14.1–14.7.
