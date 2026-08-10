# KORA-as-Hermes-Agent — Architecture Assessment

**Branch:** `phase14-hermes-runtime`
**Base:** `cf26e24` (Phase 14 final checkpoint)
**Date:** 2026-08-10
**Type:** Investigation / design assessment. **No production change, no migration, no implementation.**
**Evidence base:** live Hermes Agent v0.17.0 source (read from the running container), the Phase 14 KORA repository, and the completed staging proof (`03-staging-proof-report.md`).

---

## 1. Executive Summary

The previous migration premise — *Hermes sits in front of a standalone KORA
composer* (`Open WebUI → Hermes → KORA Runtime`) — was **empirically rejected**
by the staging proof: Hermes generates its own agent responses, has no
passthrough to KORA's composer, and does not emit KORA's structured `kora`
explainability object.

The new hypothesis is that **KORA should instead be a highly specialized,
structurally governed agent running inside Hermes** (`Open WebUI → Hermes →
KORA Agent`), with Hermes as the generic agent runtime and KORA's
architectural responsibilities enforced through supported Hermes mechanisms
plus KORA-owned components.

**Assessment verdict: CONDITIONAL GO — viable in principle, with hard
prerequisites and one genuine structural gap.**

Hermes v0.17.0 is not a "prompt-only" runtime. It ships a supported **plugin
system** (Python, `plugin.yaml`, opt-in), **behavior-changing middleware**
(tool/LLM request+execution), a **context-engine registry**, per-turn hook
events, tool-blocking hooks, and an OpenAI-compatible API server that runs the
same agent loop. These are genuine, upstream-supported structural mechanisms —
KORA can be implemented as a Hermes plugin, not as a personality prompt.

However, three facts constrain the design:

1. **No native pre-LLM veto on the OpenAI-API path.** `pre_gateway_dispatch`
   (the only skip/rewrite/allow pre-turn hook) fires on the messaging-gateway
   path, not on `/v1/chat/completions`. `pre_llm_call` injects context only;
   `LLM_REQUEST_MIDDLEWARE` rewrites the request only. KORA's current
   "refuse Execute/Admin **without calling Ollama**" guarantee therefore
   cannot be reproduced as a pre-inference veto with stock hooks on the API
   path. It can be reproduced **post-inference** via `transform_llm_output`
   (model output is discarded/replaced), which is structural but consumes an
   inference call.
2. **Explainability cannot ride inside the OpenAI response object.**
   `transform_llm_output` changes text only; no upstream hook adds arbitrary
   top-level fields (like the current `kora` object) to the OpenAI JSON.
   Structured explainability can be preserved **out-of-band**: a KORA plugin
   writes a canonical explainability record (JSON) per turn to a KORA-owned
   store/API. This is a contract change vs. today (explainability currently
   embedded in the response).
3. **A KORA plugin is custom, upstream-tracked code.** It is a *supported
   extension point* (like a VS Code extension), not a fork — but it is a
   maintenance surface that must track Hermes plugin-API evolution.

Long-term maintainability is **improved relative to the current custom
runtime**: a plugin rides upstream Hermes releases, MCP/tooling, security
fixes, and community work, while KORA keeps its own services (Memory Runtime,
Knowledge Platform, Approval Engine, Event Bus) as external, KORA-owned
components the plugin calls. The upgrade boundary is "KORA maintains a
plugin + its own services," not "KORA maintains an entire conductor runtime."

**Recommendation (detailed in §27): proceed to a small isolated staging
prototype that proves the four gating mechanisms (`pre_llm_call` context
injection, `pre_tool_call` blocking, `transform_llm_output` response
shaping/refusal, out-of-band explainability records) before any migration.
Do not migrate production.**

---

## 2. Original Migration Premise and Why It Was Rejected

Original target: `Open WebUI → Hermes → KORA Runtime` where Hermes routes and
KORA (existing composer) generates the governed, explainable response.

Rejected by the staging proof (empirically, Hermes v0.17.0):

- Hermes serves Open WebUI via its OpenAI-compatible API and can advertise
  model `KORA`. ✅
- Hermes accepts a KORA system prompt (exact-echo probe passed). ✅
- Hermes generates responses through its **own `AIAgent` loop**; there is no
  passthrough/proxy mode to an external composer. ❌
- Responses contain **no `kora` explainability object** (top-level keys were
  `choices/created/id/model/object/usage`). ❌
- Prompt-only KORA identity is not structurally reliable (a cold-start
  response identified as "Qwen" despite the KORA prompt). ❌
- A custom relay/plugin to force Hermes in front of the KORA composer would
  reintroduce the custom maintenance the migration was meant to eliminate. ❌

Conclusion: the "Hermes in front of KORA composer" arrangement is not
supported by Hermes and would require custom plumbing that defeats the
purpose. Rejected.

---

## 3. New KORA-as-Hermes-Agent Hypothesis

Target: `Open WebUI → Hermes Runtime → KORA Agent`, where:

- Hermes provides generic agent runtime: request ingestion, sessions, agent
  loop, tool/MCP execution, subagents, lifecycle, model plumbing.
- KORA is a **first-class, structurally governed agent** implemented as a
  Hermes plugin/configuration that enforces KORA's pipeline — classification,
  governance, retrieval decisions, memory decisions, tool authorization,
  response composition, explainability — via supported structural mechanisms
  and KORA-owned external services.

The hypothesis is testable and is NOT "KORA as a personality prompt." The
verification in §6/§8 establishes which structural mechanisms exist.

---

## 4. Current KORA Architecture (source of truth)

From the repository (`AI/KORA`, Phase 14 checkpoint `cf26e24`), the current
request/response flow (`Runtime/app/main.py`):

```
POST /v1/chat/completions
 → classify()            heuristic regex → execute_forbidden | administrative_forbidden |
                         identity | preference | architecture | relationship | operational | general
 → select_strategy()     label → query_knowledge/query_graph/query_tools/query_memory + budgets
 → assemble_context()    provenance note (conversation)
 → refused?              execute/admin → REFUSE, return _refusal_message() WITHOUT calling Ollama
 → _retrieve_knowledge_context()   architecture/relationship → Knowledge (Chroma + local graph)
 → _retrieve_tool_context()        operational → Tool Platform (read-only tools)
 → system prompt = solo_system.txt + explainability JSON + knowledge + tool context
 → ollama_chat()         POST to Ollama /api/chat
 → _openai_response()    OpenAI envelope + `kora` explainability object
```

**KORA-owned subsystems (all in-repo, all preserved by this assessment):**

| Subsystem | Files | Responsibility |
|---|---|---|
| Event Bus | `Runtime/app/event_bus.py` | in-process envelope pub/sub |
| Memory Runtime | `Runtime/app/memory_runtime.py` | event→proposal lifecycle |
| Approval Engine | `Runtime/app/approval_engine.py` | proposal state transitions |
| Proposal repository | `Runtime/app/proposal_repository.py` | SQLite/in-memory state + redaction |
| Commit coordinator | `Runtime/app/commit_coordinator.py` | approval→persistence workflow |
| Honcho adapter | `Runtime/app/honcho_adapter.py` | durable memory backend |
| Memory auth | `Runtime/app/auth.py` | bearer scopes (memory:read/approve/operate) |
| Knowledge facade | `Knowledge/service.py` + subpackages | ingestion/chunk/embed/Chroma/retrieval/context |
| Graph | `Knowledge/graph/` | extraction, SQLite store, retrieval, export→Graphify |
| Tools | `Tools/` | registry, authorizer, executor, MCP client, Ollama tools |
| Config | `Config/*.yaml` | runtime, memory, knowledge, tools, council, hermes |
| Prompts | `Prompts/solo_system.txt` | identity/governance text |
| API | `Runtime/app/main.py` | all routes incl. memory proposal API |

**Governance contract (docs + code):** KORA sole identity; structured
explainability (`kora` object); no raw CoT; refusal before inference for
Execute/Admin; Memory ≠ Knowledge ≠ Tools; approval-gated durable Memory;
Context Intelligence before retrieval; provenance survives every hop;
anti-laundering of Memory+Knowledge.

---

## 5. Hermes Runtime Architecture (verified, v0.17.0)

From the running container source:

- **Agent loop:** `run_agent.AIAgent` + `agent/conversation_loop.py` —
  session message list → system prompt (built ONCE per session, cached,
  byte-stable) → provider call → tool dispatch → memory manager → turn
  finalizer.
- **API server:** `gateway/platforms/api_server.py` — OpenAI-compatible
  `/v1/chat/completions`, `/v1/models`, `/v1/responses`, sessions API, runs
  API (SSE lifecycle events), `/health`. Auth via `API_SERVER_KEY`. Runs the
  same `AIAgent` loop. No passthrough/proxy mode.
- **Tools:** built-in toolsets + MCP tools (`hermes mcp add`) + tool
  authorization/approval (`tools/approval.py`, `agent/tool_guardrails.py`).
- **Memory:** built-in `MEMORY.md`/`USER.md` + external provider system
  (exclusive kind) incl. **honcho**.
- **Sessions:** SQLite session store + HTTP sessions API.
- **Subagents/delegation:** `delegate_task` tool, orchestrator roles,
  per-subagent model/base_url (incl. arbitrary OpenAI-compatible endpoint),
  spawn depth/concurrency limits.
- **Lifecycle:** sessions, checkpoints, cron, kanban, skills, plugins,
  hooks, middleware.

## 6. Verified Hermes Extension Points (source-verified, v0.17.0)

All of the following were confirmed by reading the installed source (not
inferred from names).

**A. Plugin system** (`hermes_cli/plugins.py`)
- Manifest: `plugin.yaml` (name, version, provides_tools, provides_hooks,
  kind: standalone/backend/exclusive/platform/model-provider).
- Install: user plugins at `$HERMES_HOME/plugins/<name>/`; opt-in via
  `plugins.enabled` config; also entry-point group `hermes_agent.plugins`.
- `PluginContext.register()` gives each plugin: `register_tool`,
  `inject_message`, `register_command`, `dispatch_tool`,
  `register_context_engine`, `register_hook`, `register_middleware`, an `llm`
  facade, and provider registries (web search, browser, image gen, TTS, …).

**B. Hooks** (`hermes_cli/plugins.py` `VALID_HOOKS`, dispatched in
`agent/conversation_loop.py` / `agent/agent_runtime_helpers.py`):
- `pre_tool_call` — **can BLOCK** (`{"decision":"block", ...}`).
- `post_tool_call`, `transform_tool_result`.
- `pre_llm_call` — **context injection only** (returns `{"context": ...}` /
  string, injected into the current user message; ephemeral, never persisted).
- `post_llm_call`.
- `transform_llm_output` — **replaces/rewrites the final response text**
  (first non-None string wins).
- `pre_api_request`, `post_api_request`, `api_request_error`.
- `on_session_start`, `on_session_end`, `on_session_finalize`,
  `on_session_reset`.
- `subagent_start`, `subagent_stop`.
- `pre_gateway_dispatch` — **skip/rewrite/allow**, fired per incoming
  MessageEvent on the messaging-gateway path (NOT the api_server path).
- `pre_approval_request`, `post_approval_response` — observers on tool
  approval lifecycle.

**C. Middleware** (`hermes_cli/middleware.py`):
- `LLM_REQUEST_MIDDLEWARE` — may replace the effective provider request
  payload (`{"request": {...}}`).
- `TOOL_REQUEST_MIDDLEWARE` — may replace tool arguments before
  hooks/guardrails/approvals/execution.
- `LLM_EXECUTION_MIDDLEWARE`, `TOOL_EXECUTION_MIDDLEWARE` — may wrap
  execution.

**D. Context engine** (`agent/context_engine.py` `ContextEngine` ABC):
- A plugin may `register_context_engine(...)`; the engine provides `name()`,
  `update_from_response()`, `should_compress()`, `compress()`,
  `get_tool_schemas()`, `handle_tool_call()`, `get_status()`,
  `on_session_start/end/reset()`.

**E. System-prompt invariant:** the system prompt is built once per session,
cached, and byte-stable (for prompt caching). Plugin pre_llm_call context and
external-memory prefetch are injected into the **user message** per turn —
never into the system prompt.

**F. API-server path:** `api_server` instantiates `AIAgent` from
`run_agent.py`, so plugins, hooks, and middleware fire on the OpenAI-compatible
path (verified at `gateway/platforms/api_server.py:1045-1068`).

**G. What does NOT exist:** any upstream pre-LLM veto on the api_server path;
any hook that adds arbitrary top-level fields to the OpenAI response object;
any passthrough/proxy mode to an external composer.

---

## 7. KORA Responsibilities

Canonical list of KORA's architectural responsibilities (from the repository):

1. Product identity (KORA / Brainiac; never Hermes/Open WebUI/Ollama).
2. Request classification.
3. Strategy selection (which stores to query).
4. Context assembly decisions + provenance.
5. Governance / policy enforcement (Execute + Administrative refusal).
6. Memory policy (approval-gated durable memory; eligibility/dedup/capacity/
   expiry/audit).
7. Knowledge policy (what is Knowledge, when to retrieve, provenance,
   non-SoT).
8. Tool policy (which tools are appropriate/allowed, approval requirements).
9. Council selection/behavior (Phase 15, conceptual today).
10. Explainability (structured `kora` object; no raw CoT).
11. API contracts (OpenAI-compatible chat; memory proposal APIs).

---

## 8. Responsibility Mapping: KORA → Hermes

| KORA responsibility | Hermes mechanism (verified) | Structural? |
|---|---|---|
| Request ingestion (OpenAI API) | Hermes `api_server` `/v1/chat/completions` | ✅ runtime |
| Sessions / continuity | Hermes session store + sessions API | ✅ runtime |
| Agent loop / inference plumbing | Hermes `AIAgent` + provider → Ollama | ✅ runtime |
| Tool/MCP execution transport | Hermes tools + MCP client + `pre_tool_call` block | ✅ runtime |
| Subagents (future Council members) | Hermes `delegate_task` + `subagent_start/stop` hooks | ✅ runtime |
| **Classification** | KORA plugin `pre_llm_call` (Python code runs classification and injects the resulting strategy/context structurally) | ✅ structural (plugin code, not prompt) |
| **Strategy selection** | KORA plugin code in `pre_llm_call`/`LLM_REQUEST_MIDDLEWARE` | ✅ structural |
| **Context assembly (memory/knowledge/tool evidence)** | KORA `ContextEngine` (`register_context_engine`) + `pre_llm_call` injection + `inject_message` | ✅ structural |
| **Tool authorization decisions** | KORA policy in `pre_tool_call` (block) + `TOOL_REQUEST_MIDDLEWARE` + approval hooks | ✅ structural |
| **Memory write approval** | KORA plugin calls KORA Memory Runtime API (approval-gated); Hermes honcho provider NOT enabled | ✅ structural (KORA-owned) |
| **Execute/Admin refusal BEFORE inference** | ⚠️ **NO native pre-LLM veto on API path.** Achievable post-inference via `transform_llm_output` (replace output) — structural but model already ran | ⚠️ PARTIAL |
| **Response composition** | Hermes agent + `transform_llm_output` | ✅ structural (text-level) |
| **Canonical `kora` explainability object** | ⚠️ Not embeddable in OpenAI response. Achievable out-of-band: plugin writes structured JSON per turn to KORA explainability store/API | ⚠️ CONTRACT CHANGE |
| Identity as a hard guarantee | Model name `KORA` (config) + KORA plugin `pre_llm_call` injecting identity context structurally | ✅ mostly (not model-enforced) |

## 9. Structural Enforcement Analysis

**What can be enforced structurally (no prompt reliance):**

1. **Mandatory per-turn KORA context injection** — a KORA plugin's
   `pre_llm_call` hook runs *Python code* every LLM call and injects
   classification + strategy + selected evidence into the user message. This
   is executed by Hermes deterministically (every turn), independent of model
   compliance.
2. **Tool authorization** — `pre_tool_call` can hard-block any tool before it
   executes (`{"decision":"block"}`); `TOOL_REQUEST_MIDDLEWARE` can rewrite
   args. KORA policy can be the block decision-maker.
3. **Approval lifecycle visibility** — `pre_approval_request` /
   `post_approval_response` let KORA observe (not veto) approvals.
4. **Response shaping / post-hoc refusal** — `transform_llm_output` replaces
   the final text; KORA can structurally substitute a refusal or append
   explainability text.
5. **Session lifecycle** — `on_session_start/end/finalize/reset` let KORA
   run setup/teardown, recovery, and out-of-band explainability finalization.
6. **Subagent governance** — `subagent_start/stop` hooks + delegation limits
   bound Council member behavior later.

**What cannot be enforced with stock hooks (API path):**

1. **Pre-inference veto** (refuse without calling the model). On the
   messaging-gateway path `pre_gateway_dispatch` can skip; on the
   OpenAI-compatible API path there is no equivalent. KORA's current
   "refuse without Ollama" property becomes "refuse by replacing the model
   output" (`transform_llm_output`), which still consumes one inference call.
   A KORA plugin could *also* make the veto visible earlier (e.g., short-
   circuit via its own store), but Hermes itself will still execute the loop
   unless the plugin can force termination — which no hook supports today.
2. **Structured response metadata** — no hook adds JSON fields to the OpenAI
   envelope; explainability must go out-of-band or as text.

**Summary:** roughly 10 of 11 KORA pipeline stages can be structurally
enforced. The two exceptions are both resolvable with contract changes, not
with "ask the model nicely":
- refusal: post-inference structural substitution (accept the inference cost)
  or pre-dispatch interception on gateway surfaces;
- explainability: out-of-band canonical JSON records + (optionally) a compact
  text digest in the response.

---

## 10. Memory Integration

- **Keep the existing Phase 14.2 architecture as-is and KORA-owned:** Memory
  Runtime, Approval Engine, proposal repository, commit coordinator, Honcho
  adapter, Event Bus, memory proposal API, bearer scopes.
- **Hermes's role:** KORA's plugin uses `pre_llm_call`/`ContextEngine` to
  inject *read* context from KORA Memory into the turn; a registered KORA tool
  (`kora.propose_memory`) lets the agent propose a memory, which goes through
  the **existing approval-gated pipeline** (proposal → approve/reject → commit
  to Honcho). Memory writes remain ungated only through KORA's API.
- **Hermes's own Honcho provider MUST stay disabled** — enabling it would
  create a second, ungated Honcho writer and violate the approval-gated
  memory contract. Hermes built-in `MEMORY.md`/`USER.md` (session memory) can
  stay for continuity but must be explicitly categorized as session state, not
  KORA Memory.

---

## 11. Knowledge Integration

- **Keep the Phase 14.3 Knowledge Platform KORA-owned and unchanged:** service
  facade, ingestion, chunking, Ollama embeddings, Chroma adapter, index
  metadata, indexing coordinator, retrieval service, context assembler.
- **Hermes integration:** KORA plugin registers a `kora.knowledge_query` tool
  and/or uses its `ContextEngine` to retrieve and inject knowledge context
  into the turn with provenance labels (source, document_id, version,
  content_hash) — preserving the "Knowledge = what exists" boundary.
- Boundary unchanged: Memory ≠ Knowledge ≠ Tools; Chroma is infrastructure,
  not SoT; repo/ADRs remain SoT. Ingestion remains a known gap (no production
  trigger) — unchanged by this design.

---

## 12. Graph Integration

- Keep Phase 14.4 graph architecture KORA-owned: extraction, SQLite graph
  store, graph retrieval, combined retrieval, `graph.json` export.
- Graphify stays the graph serve/visualization layer; not on the answer path.
- Hermes integration is optional: a `kora.graph_query` tool / context-engine
  hook exposing relationship evidence with provenance. No premature Graphify
  changes.

---

## 13. Tool/MCP Integration

- **Hermes provides** the underlying tool/MCP execution runtime (mature,
  native): built-in toolsets, MCP client (`hermes mcp add`), tool dispatch,
  tool results normalization, approvals.
- **KORA retains control:** KORA's `pre_tool_call` hook implements the
  authorization decision (allowed? risk class? approval required? context to
  pass?). KORA's Tool Platform (registry + authorizer) remains the policy
  authority; execution may be delegated to Hermes's runtime.
- **Explainability of tool use:** KORA's plugin records each tool invocation
  (name, arguments, result summary, authorization decision, timestamps) into
  the out-of-band explainability record from `post_tool_call` /
  `transform_tool_result` — preserving "tools used / governance decisions"
  structurally.
- MCP servers remain unconfigured today; no functional loss.

---

## 14. Explainability/Provenance Architecture

**Requirement (governance contract):** canonical structured result including
classification, strategy, stores queried, stores skipped, retrieval decisions,
tools used, provenance, governance decisions, refusal/restriction decisions —
produced structurally, not by prompting the model to output fields.

**Viable design (structural):**
- A KORA plugin maintains a per-turn **explainability record** (Python
  dataclass → JSON) in KORA-owned storage (SQLite or the existing Event
  Bus/KORA services).
- Populated at each structural stage:
  - `pre_llm_call` → classification, strategy, stores queried/skipped,
    retrieval decisions;
  - `pre_tool_call`/`post_tool_call` → tool authorization decisions + tool
    use;
  - `transform_llm_output` → final content + refusal flag;
  - `on_session_finalize` → finalize + persist the record.
- Exposed via a KORA Explainability API (`GET /v1/explainability/{turn_id}`)
  and/or a compact human-readable digest appended to the response text.
- Provenance labels (source_class/source_ref/authority) attached at retrieval
  by the KORA-owned Knowledge/Memory code — preserved structurally.

**Contract change vs. today:** the current `kora` object is embedded in the
OpenAI response envelope. Under Hermes it becomes an out-of-band artifact
(+ optional text digest). Any consumer (Open WebUI plugin, KORA UI) must be
updated. This is a deliberate, documented contract change — not a loss of
explainability, but a relocation.

## 15. Council/Agent Implications (Phase 15)

- Long-term target: KORA orchestrates specialized Council intelligence
  (NOVA/IRIS/TALIA/SOLA/LUMA/ALUMA/NOMA) with Hermes providing member runtimes.
- Verified Hermes primitives that support this: `delegate_task` subagents
  (per-member model/base_url, spawn depth, concurrency limits), `subagent_start`
  /`subagent_stop` hooks (lifecycle governance), sessions per member,
  `transform_llm_output` (member contribution shaping).
- KORA retains selection/deliberation/synthesis ownership; Hermes provides
  isolation + transport. This is DESIGN ONLY — not implemented in this phase.
- Caveat: Hermes subagents are generic workers by default; the
  "members ≠ agents" rule must be enforced by KORA's plugin (selection logic +
  subagent lifecycle hooks), i.e., policy in KORA code, substrate in Hermes.

---

## 16. Upgrade/Maintenance Boundary

**Question: can KORA track upstream Hermes releases without a fork or
permanent custom patch?**

- **No fork required.** The KORA integration is a user plugin
  (`$HERMES_HOME/plugins/kora/`) using documented, upstream-supported
  mechanisms: `plugin.yaml`, `PluginContext.register_*`, `VALID_HOOKS`,
  middleware, context engine. Plugins are an explicit, stable extension
  surface (entry-point group + manifest dir), the same category as a VS Code
  extension.
- **Upgrade risk is real but bounded:** the plugin API surface (hook names,
  `PluginContext` methods, middleware contract) is upstream-controlled and can
  change between Hermes releases. KORA's plugin must be re-validated per
  upgrade. This is the same kind of maintenance as any dependency — but it is
  a *small* surface compared to maintaining an entire conductor runtime.
- **KORA-owned services (Memory Runtime, Knowledge Platform, Approval Engine,
  Event Bus, explainability store) are NOT Hermes-bound** — they are external
  components the plugin calls over HTTP/DB, so they upgrade independently of
  Hermes.
- Recommended mitigation: pin Hermes image tags (currently `:latest` in
  `services/hermes/compose.yaml` — flagged as an existing risk), run the KORA
  plugin validation suite (see §26) on each Hermes upgrade before promoting.

**Boundary verdict:** acceptable — KORA becomes "a normal Hermes
plugin/configuration + KORA-owned services," upgradable without forking Hermes.
The maintenance burden shifts from "KORA conductor runtime" to "KORA plugin +
KORA services," which is smaller but still nonzero.

---

## 17. Community/Upstream Benefits

Legitimate benefits IF KORA is a normal plugin/config (not a fork):

- Upstream bug fixes, security patches, and release cadence for the agent
  runtime, HTTP server, tool/MCP stack, and model providers.
- MCP ecosystem improvements (new servers, protocol updates) land in Hermes
  and flow to KORA automatically.
- Agent/runtime features (context compression, streaming, sessions, provider
  adapters) are maintained by the community, not by us.
- Shared knowledge/docs for Hermes tooling.

Caveats (do not overstate):

- These benefits apply only to the *generic runtime* surface. KORA's own
  intelligence/governance code (plugin logic + services) is still ours to
  maintain.
- `:latest` image tracking currently forfeits some of these benefits
  (non-reproducible builds); tag pinning is a precondition.
- Upstream velocity can also mean breaking plugin-API changes (see §16).

Net: **yes, a real advantage, conditional on tag pinning and the §26
validation suite.**

---

## 18. Risks

1. **Plugin-API drift** — hook names/`PluginContext`/middleware change across
   Hermes releases → KORA plugin breaks on upgrade. Mitigation: pin tags,
   validation suite, minimal API surface.
2. **Pre-inference refusal gap** — Execute/Admin refusal becomes
   post-inference on the API path (model still runs). Cost/behavioral change
   vs. today. Mitigation: `transform_llm_output` substitution + optional
   gateway-surface `pre_gateway_dispatch` where available; document the
   semantic change.
3. **Explainability contract change** — `kora` object moves out-of-band.
   Consumers (Open WebUI/KORA UI) must be updated; risk of "explainability
   lost" perception. Mitigation: explicit API + text digest + docs.
4. **Identity is config+plugin, not intrinsic** — a misconfiguration (model
   name, disabled plugin) silently weakens identity. Mitigation: health check
   asserting plugin loaded + model name = KORA + `plugins.enabled` contains
   kora.
5. **Custom code inside Hermes** — the KORA plugin is ours to maintain.
   Mitigation: keep plugin thin (policy + orchestration of KORA services), put
   heavy logic in KORA services.
6. **Second memory writer** — enabling Hermes's Honcho provider would break
   approval gating. Mitigation: keep it disabled; test that it stays disabled.
7. **Dual control planes** — KORA services + Hermes runtime both emit
   lifecycle state; reconciliation needed (e.g., session ↔ explainability
   record IDs).
8. **64K context minimum** — Hermes requires large context models or
   `model.context_length`/`ollama_num_ctx` overrides (staging confirmed).
   Homelab models (qwen3:8b/14b) need overrides; larger models increase VRAM.

---

## 19. Failure Modes

| Failure | Detection | Behavior |
|---|---|---|
| KORA plugin fails to load | `plugins.enabled` check + startup log + health check | Hermes starts without governance → MUST fail closed (do not serve chat) |
| KORA Memory/Knowledge service down | health checks | ContextEngine returns empty; agent must degrade honestly (no fabrication) |
| `pre_tool_call` block logic bug | audit log | tool runs without KORA authorization → fail closed default (deny unless allow) |
| Hermes upgrade breaks plugin | §26 validation suite | do not promote; pin back |
| Explainability record write fails | on_session_finalize | degrade to text digest; log |
| Model identity slip ("I am Qwen") | identity probe test | mitigation: structural `pre_llm_call` injection + response digest asserting KORA |
| Ollama down | provider error | Hermes surfaces error; no silent fallback to a different provider |

---

## 20. Option A/B/C/D Comparison

| | A. Standalone KORA Runtime (status quo) | B. KORA as Hermes Agent (full in-process) | C. Hybrid (Hermes + KORA-owned services) | D. Custom Hermes fork/extension |
|---|---|---|---|---|
| Governance enforcement | ✅ structural (own code) | ⚠️ structural via plugin, minus pre-LLM veto | ✅ structural via plugin + KORA services | ✅ max control |
| Explainability | ✅ in-response `kora` object | ⚠️ out-of-band/contract change | ⚠️ out-of-band/contract change | ✅ could embed |
| Custom runtime maintenance | **HIGH** (full conductor maintained) | LOW–MEDIUM (plugin only) | MEDIUM (plugin + services) | **VERY HIGH** (fork) |
| Tracks upstream Hermes | n/a (no Hermes dependency) | ✅ | ✅ | ❌ fork must rebase |
| MCP/tool ecosystem reuse | low | high | high | high |
| Migration risk to existing Phase 14 | none (stays) | high (contract changes) | medium | very high |
| Long-term benefit | stable but costly | best runtime leverage | balanced | unjustified |

**Verdict:** Option **B** and **C** are the viable contenders; **D** is
unjustified (a fork permanently breaks the upstream/maintainability benefit —
rejected unless B/C prove impossible, which they have not). Option **C**
(recommended): KORA as a Hermes plugin that orchestrates KORA-owned services
(Memory Runtime, Knowledge Platform, Approval Engine, Event Bus, explainability
store). Option B differs only in whether those services are in-process vs
external; external (C) keeps upgrade boundaries clean and is recommended.
Option A remains the fallback if the staging prototype fails.

---

## 21. Recommended Architecture

```text
Open WebUI
   │  OPENAI_API_BASE_URL = http://hermes:8642/v1  (API_SERVER_KEY)
   ▼
Hermes Runtime (api_server :8642, model "KORA", plugin "kora" enabled)
   │  AIAgent loop
   │   ├── KORA plugin: pre_llm_call  → classify / strategy / context injection
   │   ├── KORA plugin: ContextEngine → memory+knowledge evidence (provenance)
   │   ├── KORA plugin: pre_tool_call → tool authorization (block/allow)
   │   ├── KORA plugin: post_tool_call→ record tool use in explainability record
   │   ├── KORA plugin: transform_llm_output → refusal shaping / text digest
   │   └── KORA plugin: session hooks → explainability finalize + lifecycle
   ▼
KORA-owned services (external, unchanged)
   ├── KORA Memory Runtime / Approval Engine / Honcho (approval-gated)
   ├── KORA Knowledge Platform (Chroma, embeddings, retrieval) + Graph store
   ├── KORA Tool Platform policy (risk/approval)   ← decisions only
   ├── KORA Event Bus
   └── KORA Explainability store + API
   ▼
Ollama (inference + embeddings)
```

Recommended posture: **Conditional Go on Option C (Hybrid)** — KORA as a thin,
upstream-supported Hermes plugin that structurally enforces its pipeline via
verified hooks/middleware/context-engine, with all KORA-owned services remaining
external and unchanged.

## 22. What Must Remain KORA-Owned

- Product identity and identity guarantees (model name `KORA` + plugin-enforced
  identity context; health check asserting it).
- Classification and strategy selection (KORA plugin code).
- Governance / policy enforcement (refusal logic, Execute/Admin rules).
- Memory policy + Memory Runtime + Approval Engine + Honcho adapter + memory
  proposal API (unchanged, external).
- Knowledge policy + Knowledge Platform + Chroma + graph store + retrieval
  (unchanged, external).
- Tool authorization decisions (which tools, risk class, approval required).
- Council selection/synthesis (Phase 15) — KORA code.
- Explainability record generation + storage + API.
- Memory/Knowledge SoT boundaries; repository/ADRs as SoT.

## 23. What Can Be Delegated to Hermes

- Request ingestion and OpenAI-compatible API surface.
- Session store and continuity.
- Agent loop execution and model/provider plumbing (Ollama).
- Generic tool/MCP execution transport.
- Subagent/member runtimes (future Council).
- Lifecycle mechanics (sessions, checkpoints, cron, kanban, skills).
- Context compression, streaming, provider adapters.
- MCP ecosystem reuse and upstream maintenance of all of the above.

## 24. What Hermes Must NOT Own

- KORA identity as its own brand (must never present as Hermes the product).
- KORA Memory authority / ungated Honcho writes (its Honcho provider must stay
  disabled).
- KORA Knowledge SoT or promotion authority.
- KORA governance/refusal decisions (KORA plugin decides; Hermes only executes).
- KORA explainability provenance authority (KORA writes the canonical record).
- Council seat definitions (members ≠ Hermes workers by default).

## 25. Migration Preconditions

1. **Staging prototype passes §26 tests** (esp. 1, 2, 4, 5, 7, 9, 12).
2. **Decision on the refusal semantics:** accept post-inference refusal
   (`transform_llm_output`) on the API path, or restrict "hard refusal"
   guarantees to gateway surfaces. Documented, not assumed.
3. **Decision on explainability contract:** out-of-band canonical records +
   text digest; Open WebUI/KORA UI consumer update. Documented, not assumed.
4. **Tag pinning:** replace `nousresearch/hermes-agent:latest` with a pinned
   digest (also closes an existing repo risk).
5. **KORA chat auth token** for the plugin→KORA service boundary (KORA chat
   endpoint currently unauthenticated; a scoped token must be introduced).
6. **KORA Memory API tokens** configured (currently unset in production).
7. **Backup/rollback:** Phase 14 checkpoint `cf26e24` + backup
   `PHASE14-KORA-RUNTIME-FINAL-BACKUP-20260810` remain the rollback path; the
   Hermes plugin work stays on `phase14-hermes-runtime`.

## 26. Proposed Validation Plan (staging tests with PASS/FAIL)

All tests run against an isolated staging Hermes (own container/data, port
bound to localhost), same method as the completed proof. "KORA" = the plugin
under test.

| # | Test | PASS criteria | FAIL criteria |
|---|---|---|---|
| 1 | Open WebUI-style request reaches the KORA plugin | `POST /v1/chat/completions` triggers `pre_llm_call` (plugin log) and returns 200 OpenAI response | no plugin invocation; non-OpenAI response |
| 2 | Structural identity | Health/`/v1/models` reports model `KORA`; plugin loaded assert (`plugins.enabled` + log); identity probe (`Reply exactly KORA-IDENTITY-TEST`) returns the token across 5 consecutive cold-start turns | any turn returns non-KORA or a different model |
| 3 | Mandatory classification executes | Every turn's `pre_llm_call` writes a classification record (label/confidence/rationale) to the explainability store | any turn lacks a classification record |
| 4 | Governance refusal (Execute/Admin) | A "wipe the zfs dataset" turn returns the KORA refusal text and records `refused=true` + the authorization decision | refusal absent or record missing |
| 5 | Correct knowledge/memory/tool path selection | Classification "architecture" → explainability record shows `stores_queried=[knowledge]`; "operational" → tools invoked with KORA authorization; "preference" → memory skipped | wrong store selection |
| 6 | Approval-gated memory | Agent proposes a memory → record stays `pending_review`; only after approval API call does it commit to Honcho; Hermes Honcho provider is disabled (assert config) | memory committed without approval, or Hermes Honcho provider enabled |
| 7 | Canonical explainability record | `GET /v1/explainability/{turn_id}` returns classification, strategy, stores queried/skipped, retrieval decisions, tools used, governance decisions, refusal flag | missing/empty record |
| 8 | Provenance preserved | A knowledge-grounded turn's record contains document_id/version/content_hash/source for each chunk | provenance absent |
| 9 | Cold start survival | Restart staging Hermes; identity, plugin load, classification, and refusal still pass (tests 2-4) | any test fails after restart |
| 10 | Model cannot bypass KORA processing | Direct model probe outside the agent loop returns no `kora`-governed fields; agent-loop response always reflects KORA plugin record | bypass yields governed output without a record |
| 11 | No fork | All behavior implemented as `$HERMES_HOME/plugins/kora/` plugin using only `VALID_HOOKS`/middleware/ContextEngine/`register_tool`/`register_context_engine`; no modified upstream files | any patched upstream file |
| 12 | Upstream-release compatibility (proxy) | Plugin loads on the pinned Hermes release and passes `hermes plugins list`/`hermes hooks doctor` | plugin fails to load |

## 27. Explicit Go/No-Go Decision

**Conclusion: CONDITIONAL GO — Option C (Hybrid: KORA as a thin, structurally
governed Hermes plugin orchestrating external KORA-owned services).**

Conditions (exact prerequisites before any production migration):

- P1: Staging prototype passes §26 tests 1, 2, 4, 5, 7, 9, 12.
- P2: Refusal semantics decision (post-inference on API path) accepted and
  documented.
- P3: Explainability contract change (out-of-band records + text digest)
  accepted and consumers updated.
- P4: Hermes image pinned; plugin API surface frozen at that release.
- P5: Scoped auth token added at the plugin→KORA boundary; KORA Memory tokens
  configured.

If P1 fails or P2/P3 are rejected → **NO-GO**, keep the current KORA Runtime
architecture (`cf26e24`) intact (Option A remains the production architecture).

---

## Concise Recommendation

- **Should KORA become a Hermes Agent?** Conditionally yes — as a *structural
  Hermes plugin* (Option C), not as a persona prompt. The hypothesis is
  architecturally sound: Hermes provides genuine structural hooks/middleware/
  context-engine/tool-blocking, and KORA keeps its pipeline in code.
- **What KORA should continue to own:** identity, classification/strategy,
  governance/refusal policy, Memory Runtime + approval, Knowledge Platform,
  graph, tool authorization decisions, Council selection, explainability
  records.
- **What Hermes should own:** generic runtime — API surface, sessions, agent
  loop, tool/MCP execution transport, subagent/member runtimes, model plumbing,
  upstream maintenance of all of the above.
- **Long-term maintainability:** improved. KORA's maintenance surface shrinks
  from a full conductor runtime to a thin plugin + its own services; upstream
  Hermes releases carry the generic runtime forward.
- **Is upstream/community support a legitimate advantage?** Yes — for the
  generic runtime, MCP/tooling, security, and model-provider work — provided
  Hermes is tag-pinned and the plugin validation suite gates upgrades. It does
  not apply to KORA's own intelligence code.
- **What must be proven before implementation:** the §26 staging tests,
  especially structural refusal (4), canonical explainability out-of-band (7),
  cold-start identity (9), and no-fork (11).
- **Next step:** a small, isolated staging prototype implementing the KORA
  plugin against Hermes v0.17.0 (own container/data, localhost port), running
  §26 tests, with NO production change and NO migration. Only if the prototype
  passes do we proceed to cutover planning.

**Stop point reached.** This assessment is investigation-only: no production
was modified, no migration was performed, and no implementation was committed
for the migration itself.
