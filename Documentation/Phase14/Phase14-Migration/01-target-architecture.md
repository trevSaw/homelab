# Target Architecture — Hermes-Based KORA (Phase 14 Migration)

**Branch:** `phase14-hermes-runtime`
**Base:** `cf26e24` (Phase 14 final checkpoint)
**Status:** DESIGN — no implementation yet
**Date:** 2026-08-10

## 0. Decision summary

The migration targets:

```text
User → Open WebUI → Hermes → KORA → Memory / Knowledge / Tools → Ollama
```

Reconnaissance of the installed Hermes Agent v0.17.0 confirms the required
generic-runtime capabilities exist natively: an OpenAI-compatible API server
(`/v1/chat/completions`, `/v1/models`, sessions API, runs API) for Open WebUI;
MCP client/server; tool execution; subagent delegation to an arbitrary
OpenAI-compatible endpoint; and a Honcho memory provider hook.

**Key boundary decision (KORA identity preserved):** the Hermes API server will
advertise the model as `KORA` via `API_SERVER_MODEL_NAME` and carry KORA's
identity/governance instructions in its system prompt, but the *intelligence
turn* — classification, strategy selection, refusal, context assembly,
explainability — is delegated to the **KORA intelligence endpoint** (the
existing KORA Runtime OpenAI-compatible API) using Hermes subagent delegation
(`delegation.base_url`). Hermes therefore provides routing, sessions, tool/MCP
execution, and agent lifecycle mechanics. KORA remains the product identity,
governance, and decision layer. This prevents Hermes from claiming KORA identity
or becoming the Memory/Knowledge authority.

If delegation to the full KORA conductor proves too heavy per-turn, the fallback
design (documented, not implemented) is to serve KORA's classify/strategy/
knowledge/memory policy as MCP tools that the Hermes agent invokes, while KORA
identity remains prompt-owned. This fallback is NOT chosen as primary because it
blurs "who decides" and moves policy enforcement into prompt space.

## 1. Request flow

```text
User
 ↓  (chat UI)
Open WebUI  ── OPENAI_API_BASE_URL = http://hermes:8642/v1, key = API_SERVER_KEY
 ↓  POST /v1/chat/completions (model="KORA")
Hermes API server (gateway platform api_server, :8642)
 ↓  Hermes agent session created (system prompt = KORA identity + governance)
 ↓  per-turn: subagent delegation → KORA intelligence endpoint
KORA Runtime (intelligence): classify → strategy → assemble → (retrieve Memory/Knowledge/Tools) → explain
 ↓  returns OpenAI-compatible response (+ `kora` explainability object)
Hermes wraps/streams the answer back
 ↓
Open WebUI renders
```

## 2. Authentication flow

- Open WebUI → Hermes: `API_SERVER_KEY` bearer (HMAC-checked; Hermes refuses to
  start the API server without it).
- Hermes → KORA intelligence endpoint: existing KORA bearer model; KORA chat
  endpoint currently unauthenticated in Phase 14 — a token must be introduced at
  this boundary (do not expose KORA to the network beyond Hermes).
- KORA → Memory approval APIs: existing `KORA_MEMORY_*` scoped tokens retained.
- Tool execution inside Hermes: Hermes-native tool auth; consequential tools
  remain approval-gated (Hermes approval UI/hook) with KORA policy deciding.

## 3. KORA / Hermes boundary

- **Hermes owns:** request routing, sessions, agent loop, subagents, tool/MCP
  execution transport, model routing, gateway lifecycle, API surface.
- **KORA owns:** identity, product behavior, classification, intent, governance,
  policy enforcement, Council selection, Memory policy, Knowledge policy, context
  selection/assembly decisions, explainability, approval *requirements*.
- Hermes MUST NOT: claim KORA identity as its own, become Memory/Knowledge SoT,
  or bypass KORA policy. Enforced by configuration (model name, system prompt,
  delegation to KORA) and by the network boundary (KORA reachable only via Hermes
  or approved services).

## 4. Memory boundary

- KORA Memory Runtime + Approval Engine + Honcho adapter remain the Memory
  authority (unchanged from Phase 14).
- Hermes session history (`state.db`) is session/continuity state, NOT Memory.
- Hermes's Honcho provider hook (if enabled) must be scoped so it cannot write
  KORA Memory outside the approval workflow. Recommend: do NOT enable Hermes's
  external Honcho provider; keep Honcho writes exclusively via KORA's
  commit coordinator. (Confirmed decision at implementation; flag for review.)

## 5. Knowledge boundary

- KORA Knowledge Service (ingestion, chunking, embeddings, Chroma, retrieval,
  context assembly) remains KORA-owned, unchanged.
- Hermes may expose KORA Knowledge as MCP tools to the agent if helpful for
  tool-mediated retrieval, but Chroma remains infrastructure, not SoT.
- Sources (Obsidian/Markdown/ADRs/docs) unchanged; ingestion trigger remains a
  known Phase 14 gap (no production ingestion entry point) — unchanged by this
  migration.

## 6. Graph boundary

- KORA-owned local graph (SQLite) + extraction + retrieval + export unchanged.
- Graphify remains the graph serve/visualization layer, not SoT, not on the
  retrieval answer path (unchanged known behavior).

## 7. Tool / MCP boundary

- Generic MCP transport + tool execution move to Hermes (mature, native).
- KORA decides whether a tool is appropriate, whether policy allows it, what
  context it gets, and whether approval is required (KORA strategy/classification).
- Hermes executes approved operations. `Config/tools.yaml` MCP servers list and
  the KORA Tool Platform remain authoritative for *which* tools exist; their
  execution may be delegated to Hermes-provided tools in the target state.

## 8. Ollama boundary

- Hermes uses Ollama as its model runtime (already configured: provider custom,
  `http://ollama:11434/v1`, default `qwen3:8b`).
- KORA retains embedding model policy (`nomic-embed-text`) for Knowledge.
- Single inference backend; no duplicate model pools.

## 9. Council boundary

- Council remains Phase 15 (future, not implemented).
- KORA remains Council chair/conductor identity.
- Target future: KORA → Council Manager → NOVA/IRIS/TALIA/SOLA/LUMA/ALUMA/NOMA →
  Hermes agent runtimes (Hermes provides member runtimes/orchestration substrate;
  KORA owns selection/synthesis). Not built in this migration.

## 10. Error handling

- Hermes API server is the entry; KORA failures must degrade honestly (Hermes
  surfaces KORA's `status: degraded`/gap semantics, never fabricates).
- Ollama down → Hermes provider error → surfaced to Open WebUI.
- KORA unreachable → Hermes must fail explicitly (no silent fallback that
  bypasses KORA identity/governance).

## 11. Observability

- Preserve KORA explainability (`kora` object) on the response path end-to-end.
- Hermes lifecycle events (sessions, tool calls, approvals) logged via Hermes.
- KORA health endpoint retained for the KORA-owned subsystems; Open WebUI health
  probes target Hermes (entry) with KORA reachability surfaced inside.

## 12. Governance

- Execute / Administrative refusal remains KORA logic, not Hermes config.
- Durable Memory writes remain approval-only, enforced by KORA's approval engine.
- Tool blast radius governed by KORA policy + Hermes execution limits.
- No silent identity handoff: model name, persona, and delegation are the ONLY
  places Hermes appears KORA-branded, and they are explicitly configured.

## 13. Security

- `API_SERVER_KEY` required (Hermes refuses to start API server without it).
- KORA is NOT exposed to the proxy network; only Hermes (and approved services)
  may reach KORA.
- No secrets committed; `.env` values (API_SERVER_KEY, KORA tokens) supplied at
  deploy time from `.env.example` templates.
- Existing Hermes dashboard basic-auth retained on its own hostname.

## 14. Data ownership

- KORA Memory: KORA-owned, Honcho-backed, approval-gated (unchanged).
- KORA Knowledge: KORA-owned, Chroma-indexed, repo/ADRs SoT (unchanged).
- Graph: KORA-owned derived graph; Graphify serve layer (unchanged).
- Hermes sessions: Hermes-owned continuity store; NOT Memory/Knowledge.
- Ollama: model runtime; no ownership of Memory/Knowledge.

## 15. Lifecycle

- Startup order: ollama → honcho/chroma/graphify (stores) → kora (intelligence +
  subsystems) → hermes (entry) → open-webui.
- Shutdown: reverse; KORA never shuts down before Hermes stops routing to it.
- Rollback to Phase 14: `git checkout cf26e24` + restore backup; Hermes API
  server disabled; Open WebUI re-pointed to `http://kora:8080/v1`.

## 16. Future Distributed Council architecture

```text
Open WebUI → Hermes (entry/routing/sessions) → KORA (conductor)
                                              ↓
                                        Council Manager (KORA-owned)
                                              ↓
                          NOVA / IRIS / TALIA / SOLA / LUMA / ALUMA / NOMA
                                              ↓
                               Hermes agent runtimes (per-member)
```

KORA owns Council selection, deliberation, and synthesis. Hermes provides member
runtime/orchestration substrate (agent lifecycle, isolation, transport). Not
implemented in this migration; design only.

## 17. Open risks / decisions required before implementation

1. Per-turn delegation (Hermes → KORA) adds latency vs. the direct Phase 14 path;
   must be benchmarked. Mitigation: stream; consider KORA as the delegate for the
   intelligence turn only.
2. KORA chat endpoint currently has NO auth; a shared token must be added at the
   Hermes→KORA boundary (would be a small KORA change — flagged, not assumed).
3. Hermes memory provider: keep Hermes's built-in MEMORY.md (session memory)
   enabled, but do NOT enable its external Honcho provider, to avoid a second,
   ungated Honcho writer. This is the recommended default.
4. Whether Open WebUI should disable its own RAG/knowledge features (as it did
   for the KORA path) to preserve KORA as the only knowledge authority.
