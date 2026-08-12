# Phase 15 — Council & Intelligence

**Status:** 🟡 Started (foundation)

**Branch:** `phase15-council`

## Purpose

Evolve KORA from a single head agent into the **head of a Council** of
specialized agents, using **Hermes as the runtime**. Council members are Hermes
agents/subagents — not standalone containers, runtimes, or orchestration.

```text
Open WebUI → Hermes → KORA HEAD AGENT → delegate_task → Council member(s) → KORA synthesis
```

## Ownership

| Concern | Owner |
| --- | --- |
| Runtime / agent execution / lifecycle / tools / MCP / sessions | **Hermes** (v0.17.0, unchanged) |
| Council selection, deliberation strategy, governance, final synthesis | **KORA** (head agent) |
| Council member identity / personality / role / relationships | **Canonical content** (`Architecture/ai/Council/`) |
| Personal memory | **Honcho** (native Hermes provider) |
| Knowledge | **Chroma** (external) |
| Relationships | **Graphify** (external) |
| Inference | **Ollama** (`model.default` on Hermes) |
| Tools/MCP | Hermes tool runtime |

## Architecture

```text
                    Open WebUI
                        │
                     Hermes
                        │
               KORA HEAD AGENT
                        │  delegate_task (Hermes-native subagents)
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
      NOVA            IRIS             TALIA
        │               │                │
      SOLA            LUMA             ALUMA
                        │
                       NOMA
```

- **KORA-mediated:** `User → KORA → selected member(s) → KORA synthesis`.
- **Direct member request:** `User → KORA → single member → KORA synthesis`
  (the selected member speaks as itself; no full Council summon).
- KORA remains the head in all modes and retains final response authority.

## Implementation (foundation)

The foundation uses **Hermes-native capabilities only** — no custom runtime,
no new containers, no custom framework:

1. **Hermes native `delegate_task`** (toolset `delegation`) enabled for the
   api_server (KORA) agent: `platform_toolsets.api_server = [kora, delegation]`
   in Hermes `config.yaml`. `delegate_task` spawns a child `AIAgent` subagent
   whose identity is defined by the delegated goal/context.
2. **Canonical Council content** mounted read-only into Hermes:
   `Architecture/ai/Council` → `/opt/data/council` (compose). Members are
   **not** recreated or rewritten — they are read from the canonical files.
3. **KORA plugin** (`Documentation/Phase14/Phase14-Migration/staging/plugins/kora/`,
   production copy `/opt/data/plugins/kora`) adds:
   - `kora.council_list` — lists the canonical members.
   - `kora.council_member(<NAME>)` — loads a member's canonical
     identity/personality/role from the read-only mount.
   - A Council directive injected into KORA's context telling it how to invoke
     a member (`council_member` → `delegate_task`) and that a direct member
     request must not summon the whole Council.
4. KORA invokes a member by `delegate_task(goal="You are <NAME>, <role>.
   Answer as <NAME>: <request>", context=<member content>)`, then synthesizes.

## Current implementation status

- [x] KORA remains the head agent (Hermes-hosted).
- [x] Council member content preserved + mount declared in compose (`Architecture/ai/Council` → `/opt/data/council:ro`).
- [x] KORA plugin loads canonical member content (`kora.council_member` — verified returns NOVA's canonical identity).
- [x] Hermes `delegation` toolset (native `delegate_task`) — confirmed available and loadable for KORA.
- [x] No new runtime/container/custom framework introduced.
- [ ] **End-to-end live delegation: not yet verified.** Blocked by baseline
      KORA turn latency (~300s for a trivial turn on CPU-bound `qwen3:8b`),
      the pre-existing model/runtime performance issue (deferred decision from
      Phase 14), not a Phase 15 defect. Re-verify once inference is faster
      (GPU pass-through or a faster model).

## Deployment note (production safety)

Per Phase 15 production-safety rules, the foundation lives on branch
`phase15-council` and is **not deployed to production yet** (production remains
at the Phase 14 baseline until the end-to-end path is proven on acceptable
inference). To deploy the foundation later:

1. Apply `services/hermes/compose.yaml` (Council read-only mount).
2. Copy `Documentation/Phase14/Phase14-Migration/staging/plugins/kora/__init__.py`
   → `/opt/data/plugins/kora/__init__.py`.
3. Set `platform_toolsets.api_server: [kora, delegation]` in Hermes `config.yaml`.
4. Recreate Hermes.

## Known limitations

- **Performance:** multi-step delegation on `qwen3:8b` (CPU-bound in Ollama) is
  slow; a single delegate chain can exceed client timeouts. Same known
  limitation as Honcho dialectic (Phase 14). Not a Phase 15 defect.
- **Direct per-member model routing:** Hermes v0.17.0 api_server cannot route
  to per-member agents by request model (one agent per gateway, model from
  `config.yaml model.default`). Direct member invocation is currently
  **KORA-mediated**. Future option: separate Hermes profile per member
  (each with its own api_server) if direct model-level access is required.
- **Member-specific models/tools:** Hermes delegation supports per-call
  model/toolset selection; Council member model/tool assignment is a
  configuration concern, not yet tuned.

## Next steps

1. Verify live delegation end-to-end (larger timeout / faster model).
2. Decide member model/tool assignment (config, not code).
3. Consider direct member exposure via Hermes profiles if required.
4. Council deliberation policy (when to deliberate vs direct vs KORA-only) —
   to be designed, not hardcoded prematurely.

## References

- Canonical Council content: `Architecture/ai/Council/`, `Architecture/ai/KORA.md`
- Phase 14 baseline: `Documentation/Phase14/Phase14_Roadmap.md`
- Retirement record: `Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md`
