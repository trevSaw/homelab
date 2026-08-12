# Phase 15 — Council & Intelligence

**Status:** 🟡 **FOUNDATION COMPLETE — PAUSED** (checkpoint 2026-08-12)

**Branch:** `phase15-council` (foundation commit `468216e`)

## Purpose

Evolve KORA from a single head agent into the **head of a Council** of
specialized agents, using **Hermes as the runtime**. Council members are Hermes
agents/subagents — not standalone containers, runtimes, or orchestration.

Phase 15 is intentionally **paused** at its current foundation state. The
foundation is complete and documented; the full Council is **not** implemented,
**not** deployed, and **not** to be continued during this pause.

## Current architecture

```text
Open WebUI
    ↓
Hermes
    ↓
KORA HEAD AGENT
    ↓  Hermes-native delegate_task
Council member(s)
    ↓
KORA synthesis
```

External services (unchanged, KORA continues to use them):

```text
KORA
 ├── Memory        → Honcho
 ├── Knowledge     → Chroma
 ├── Relationships → Graphify
 ├── Inference     → Ollama
 ├── Tools         → MCP/services
 └── Council       → future Hermes agents
```

There is **no standalone KORA Runtime**, **no standalone Council Runtime**, **no
custom Council scheduler**, **no custom Council routing service**.

## What has been proven (completed foundation)

- [x] Hermes v0.17.0 provides native `delegate_task` delegation (toolset `delegation`).
- [x] `delegate_task` creates isolated child `AIAgent` subagents; the child's
      identity is defined by the delegated goal + context.
- [x] Council members can therefore be represented as Hermes agents using their
      canonical identity/personality content.
- [x] KORA can act as the head/orchestrator of the Council.
- [x] KORA can (theoretically) delegate to individual Council members via
      `delegate_task`.
- [x] Council member identity can be loaded from the existing canonical Council
      markdown files (verified: `kora.council_member("NOVA")` returns NOVA's
      canonical content).
- [x] Existing Council content remains intact (see below).
- [x] No Council runtime or additional container is required.
- [x] The KORA Hermes agent plugin is the only KORA-specific runtime code.
- [x] Hermes remains upstream/unmodified — no fork required.

## Council content — canonical (must remain)

The existing Council files are the **source of truth** and must **not** be
rewritten, consolidated, deleted, renamed, or replaced:

- All Council members + Originals: `Architecture/ai/Council/Members/`
- Council architecture/design: `Architecture/ai/Council/`
- KORA identity/About: `Architecture/ai/KORA.md`

Future Council implementation must **consume** this content rather than
recreating it in Python, embedded prompts, databases, or parallel
representations.

## Hermes capabilities used

- `delegate_task` (native subagent mechanism) — the intended invocation path.
- KORA plugin hooks + tool registration (no Hermes modification).
- `subagent_start`/`subagent_stop` hooks available for future explainability.

## Current limitations

1. **End-to-end Council delegation is NOT production-validated.**
2. Current `qwen3:8b` inference is **too slow on current hardware** for
   practical multi-agent Council interaction (baseline KORA turn ~300s on CPU).
3. The performance problem is an **inference/runtime configuration issue**, NOT
   a reason to redesign the Council architecture.
4. Hermes v0.17.0's API server does **not** provide per-request model routing
   for individual Council members.
5. Direct Open WebUI selection of individual Council members is therefore
   **not** currently part of the implementation.
6. The supported initial interaction model is:
   `User → KORA → delegate_task → Council member → KORA synthesis`.
7. Direct individual Council-member access may be investigated later using
   supported Hermes mechanisms (e.g., separate profiles), but must **not** be
   implemented during this pause.

## Production status

Production remains on the **Phase 14 baseline** — the Phase 15 foundation is
**not deployed**. Verified at checkpoint:

- Open WebUI healthy; Hermes healthy; KORA functioning; Ollama functioning;
  Honcho functioning; Chroma functioning; Graphify functioning;
  MCP/services functioning.
- Tracy's model access correct (`qwen3:8b`, `gpt-oss:20b-cloud` only).
- KORA remains isolated to Trevor (Tracy sees no KORA).
- Council production behavior unchanged (no Council features active).
- No `kora` runtime container; Hermes config/plugin at Phase 14 state.

## Why Phase 15 is paused

The foundation (architecture + minimal plugin/mount/delegation enablement) is
in place and component-verified, but the live end-to-end delegation test cannot
be completed practically because inference performance on the current hardware
makes multi-agent interaction too slow. This is a model/runtime configuration
decision (deferred from Phase 14), not an architecture blocker.

## Prerequisites for resuming

1. A practical inference configuration (GPU pass-through, or a faster/adequate
   model) that makes multi-turn agent + subagent interaction usable.
2. Confirmation Hermes still provides `delegate_task` with the intended
   behavior.
3. Confirmation the canonical Council files are unchanged.
4. Confirmation the Phase 14 baseline external services are unchanged.

## Resume procedure (exact order)

When Phase 15 is resumed:

1. Read this status document.
2. Verify current Hermes version and `delegate_task` behavior.
3. Verify current Council canonical files.
4. Verify KORA remains the Hermes head agent.
5. Verify Honcho/Chroma/Graphify/Ollama/MCP architecture unchanged.
6. Reassess inference performance and select an appropriate model config.
7. Create an **isolated staging environment**.
8. Perform an end-to-end test: `User → KORA → delegate_task → ONE Council member → KORA`.
9. Validate Council member identity/personality.
10. Validate KORA synthesis.
11. Only then investigate multi-member deliberation.
12. Only after that consider direct individual Council-member access.

Do **not** skip directly to multi-agent orchestration.

To deploy the existing foundation (once resumed and validated): apply
`services/hermes/compose.yaml` (Council read-only mount), copy the KORA plugin
(`Documentation/Phase14/Phase14-Migration/staging/plugins/kora/__init__.py` →
`/opt/data/plugins/kora/`), set `platform_toolsets.api_server: [kora, delegation]`
in Hermes `config.yaml`, and recreate Hermes.

## Resume prompt (reusable)

> Resume Phase 15 Council implementation from the documented
> **FOUNDATION COMPLETE — PAUSED** checkpoint.
>
> Do not redesign the architecture. KORA is the Hermes head agent. Council
> members are Hermes-native delegated agents using `delegate_task`. Existing
> Council markdown files are canonical and must not be rewritten. There is no
> standalone Council runtime. There is no custom scheduler/router/proxy. KORA
> continues using Honcho, Chroma, Graphify, Ollama, and MCP as external services.
>
> First reassess the current repository and Hermes version against the Phase 15
> checkpoint. Then address the current documented blocker: inference performance.
> Do not implement further Council functionality until a practical staging
> inference configuration is available. Once performance is acceptable, resume
> with the smallest possible end-to-end staging proof:
> `KORA → delegate_task → ONE Council member → KORA synthesis`.
> Do not proceed to multi-member deliberation or direct Open WebUI member access
> until that basic path is proven.

## References

- Canonical Council content: `Architecture/ai/Council/`, `Architecture/ai/KORA.md`
- Phase 14 baseline: `Documentation/Phase14/Phase14_Roadmap.md`
- Retirement record: `Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md`
