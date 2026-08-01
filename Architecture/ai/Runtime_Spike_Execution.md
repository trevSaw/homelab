# KORA Runtime Spike Execution

**Status:** Canonical runtime-spike execution record (Phase 13.11)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Authorization:** Non-production disposable laboratory only  
**Lab root:** `/mnt/monarch/prototypes/kora-spike/` (outside git)

Companions: `Spike_Architecture.md`, `Spike_Acceptance_Criteria.md`, `Spike_Test_Plan.md`, `Vertical_Slice.md`, ADR-0004/0005/0006/0008.

---

## Spike Environment Boundaries

| Boundary | Rule |
| --- | --- |
| Location | `/mnt/monarch/prototypes/kora-spike/` only |
| Git | Runtime compose/code **not** committed to homelab repo |
| Networks | Dedicated `kora_spike_net` only — **no** `proxy` / `hotio` / `ai_*` |
| Secrets | None; no production secret reuse |
| Data | Spike fixtures + ephemeral chroma/memory_staging only |
| Phase 12 | Untouched |
| Graphify | Excluded |
| Obsidian | External only; unused |

---

## Runtime Isolation Model

```text
Host loopback 127.0.0.1:18000
        │
        ▼
┌───────────────────┐
│ kora-spike-chroma │  ← sole container in this spike
│ network:          │
│  kora_spike_net   │  ← not attached to Phase 12 fabric
└───────────────────┘

KORA façade (Python on host)
  ├─ Open WebUI adapter   (UI envelope / identity branding)
  ├─ Hermes adapter       (orchestration substrate contract)
  ├─ Honcho memory adapter (candidate staging; no durable write)
  └─ Chroma knowledge adapter (index reachability + fixture retrieval)
```

Isolation verification: container attached only to `kora_spike_net`; compose stopped and network removed after run.

---

## Service Responsibilities

| Component | Responsibility in 13.11 | Notes |
| --- | --- | --- |
| Open WebUI (adapter) | Capture envelope; force `presented_as=KORA` | Full Open WebUI container not required to validate UI identity boundary |
| Hermes (adapter) | Route to KORA; `is_kora=false`; `replaces_council=false` | Full Hermes Agent install deferred; contract enforced in adapter |
| KORA façade | Classify, select Council, assemble, synthesize, explain | Authoritative policy layer |
| Council simulation | Active/deferred members; deliberative synthesis | Members ≠ agents |
| Honcho (adapter) | Memory read + pending_user_approval candidates | No automatic persistence |
| ChromaDB (container) | Isolated retrieval service heartbeat + index role | Fixture search used for relevance; not SoT |
| Graphify | — | Excluded |

---

## Data Flow

Matches `Spike_Architecture.md`:

User → Open WebUI adapter → Hermes adapter → KORA → Council selection → Context Assembly → Memory/Knowledge retrieval → Explainable response.

What does **not** flow: secrets, raw CoT, durable Memory commits, Execute tools, Graphify payloads, Phase 12 service calls.

---

## Startup / Shutdown Lifecycle

| Step | Action |
| --- | --- |
| Start | `/mnt/monarch/prototypes/kora-spike/scripts/startup.sh` |
| Run tests | `python3 .../scripts/run_scenarios.py` |
| Stop | `.../scripts/shutdown.sh` |
| Cleanup | `.../scripts/cleanup.sh` (ephemeral data; fixtures retained) |

---

## Rollback Procedure

1. Stop compose (`shutdown.sh`)
2. Confirm `kora-spike-chroma` absent and `kora_spike_net` removed
3. Confirm Phase 12 networks/services unchanged
4. Discard spike results under lab `results/` if desired (copies live in `Validation/Phase13.11/`)
5. Architecture docs remain SoT — no production cutover to reverse

---

## Cleanup Procedure

1. `shutdown.sh`
2. Remove ephemeral `data/chroma/*`, `data/memory_staging/*`, lab `results/*` via `cleanup.sh`
3. Leave `/mnt/monarch/prototypes/kora-spike/` directory for future spikes or delete entirely if retiring the lab
4. Never copy lab secrets (none exist) into git

---

## Known Limitations

1. **Open WebUI / Hermes / Honcho** validated via **boundary adapters**, not full upstream product installs in this spike window.
2. Chroma was **reachable** in isolation; retrieval scoring used fixture keyword search with Chroma as the index service under test for isolation/heartbeat (full embedding upsert pipeline not mandatory for contract pass).
3. Council reasoning is **simulated** per Selection/Dynamics rules — not multi-model LLM deliberation.
4. Preference scenario can still **retrieve unrelated Knowledge** under naive keyword overlap — write boundaries held; retrieval scoping by classification is a follow-up improvement.
5. No MCP / Execute path by design.
6. Not production-ready UX or HA deployment.

---

## Document Map

| Document | Role |
| --- | --- |
| `Runtime_Spike_Execution.md` (this file) | Execution architecture & isolation |
| `Documentation/Phase13/Runtime_Spike_Report.md` | Outcomes report |
| `Validation/Phase13.11/` | Checklists and scored results |
