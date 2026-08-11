# KORA-as-Agent Staging Prototype Report

**Branch:** `phase14-hermes-runtime`
**Date:** 2026-08-11
**Scope:** minimal integration proof. Production untouched. No migration.

---

## 1. Final architecture

```
Open WebUI client
        ↓
      Hermes v0.17.0   (generic runtime: API, sessions, agent loop, tools)
        ↓
   ┌─────────────────────────┐
   │    KORA HEAD AGENT      │   (Hermes plugin: intelligence + governance)
   └──────┬───────┬───────┬──┘
          │       │       │
      Ollama   Chroma   Honcho   (+ Graphify / MCP / future Council)
     inference knowledge memory
```

## 2. Why KORA is an agent

KORA is the specialized head agent hosted inside Hermes — **not** a container, proxy,
relay, or custom runtime. It runs as a Hermes plugin that owns classification,
strategy, governance, response composition, and explainability, and it decides
which external service is needed and calls it directly (KORA → Chroma, KORA →
Ollama, KORA → Honcho boundary).

## 3. Hermes responsibilities

Hermes owns the generic runtime: OpenAI-compatible API, sessions, agent loop,
model/inference plumbing, tool execution, MCP runtime, subagent runtime, and
upstream maintenance. These were not recreated.

## 4. Container/service responsibilities

- **Ollama** — inference + embeddings (real service; staging used production
  Ollama read-only, no config change).
- **Chroma** — knowledge store (real staging `chromadb/chroma` container).
- **Honcho** — memory service (production stack; write path is the documented
  approval-gated KORA Memory Runtime contract).
- **Graphify** — relationship serve layer (not wired as a staging service).
- **MCP/tools** — via Hermes tool runtime; KORA governs.

## 5. Ollama result — **PASS**

KORA → Ollama inference works through Hermes' model runtime; `kora.ollama_models`
lists real Ollama models. (Test 2.)

## 6. Honcho result — **BOUNDARY DOCUMENTED**

Real Honcho writes in Phase 14 flow through KORA's approval-gated Memory
Runtime (commit coordinator → Honcho adapter). That service boundary is not
exposed over HTTP for an external plugin, so the plugin reports the boundary
explicitly instead of rebuilding Memory. (Test 3.)

## 7. Chroma result — **PASS (real service)**

The KORA agent indexed one fixture document into the **real staging Chroma**
container (embed via Ollama, upsert via Chroma v2 API) and retrieved it
through `kora.knowledge_query`; the answer contained the fixture knowledge.
No Chroma reimplementation. (Test 4.)

## 8. Graphify result — **DOCUMENTED**

Graphify remains the relationship serve layer; its serve-layer integration was
not exercised as a staging service in this minimal proof. Documented limitation,
not a rebuild. (Test 5.)

## 9. MCP/tool result — **PASS**

Hermes executes tools; KORA governs. A denied tool (`kora.wipe_volume`) was
blocked by KORA's `pre_tool_call` hook before execution. (Test 6.)

## 10. Governance result — **PASS**

KORA made a real governance decision in plugin code: an Execute request was
classified `execute_forbidden` and refused (refused=true, structured reason).
Not prompt-based. Known limitation: Hermes v0.17.0 has no pre-inference veto on
the API path, so refusal is a post-inference structural replacement. (Test 7.)

## 11. Explainability result — **PASS**

KORA wrote a structured record per request (`request_id`, `classification`,
`strategy`, `governance`, `services_used`, `identity`, `timestamp`) to a JSON-lines
file — the smallest out-of-band mechanism, no production API. (Test 8.)

## 12. Custom code created/modified

Only the staging prototype files under
`Documentation/Phase14/Phase14-Migration/staging/`. No existing project code
was modified.

## 13. .py file audit

| File | Status | Class |
|---|---|---|
| `staging/plugins/kora/__init__.py` | created | **A — required KORA agent implementation** (hooks + tools; orchestrates external services) |
| `staging/plugins/kora/kora_classify.py` | created | **A — required KORA agent implementation** (classification/strategy) |
| `staging/plugins/kora/kora_explain.py` | created | **A — required KORA agent implementation** (explainability record) |
| `staging/tests/test_kora_hermes.py` | created | **B — test/integration validation** (minimal pytest) |
| `staging/explain-server/app.py` | **deleted** | over-engineered explainability API (replaced by JSONL record) |
| `staging/tests/run_prototype_tests.py` | **deleted** | oversized 12-test framework (replaced by 8-check pytest) |
| `staging/tests/ollama_proxy.py` | **deleted** | diagnostic proxy (no longer needed) |

No existing project `.py` file was modified.

## 14. Known limitations

- **No pre-inference veto** on the Hermes API path (refusal is post-inference).
- **Honcho / Graphify integration boundaries** are not yet exposed for an
  external agent; documented rather than rebuilt.
- Model performance: Hermes' API-server path was observed sending Ollama
  requests without `extra_body` (think/num_ctx not propagated) in this version —
  a staging performance issue, not an architecture blocker.

## 15. Future Council architecture (not implemented)

KORA remains head/chair; future members (NOVA/IRIS/TALIA/…) will be specialized
Hermes agents, with KORA performing final synthesis. Design boundary preserved;
nothing implemented.

## 16. Production safety verification

Production containers (`kora`, `hermes`, `open-webui`, `ollama`, `kora-chromadb`,
`graphify`, `honcho-*`) were untouched and healthy. Staging used its own project,
network, ports (127.0.0.1), volumes, and credentials. All staging containers were
torn down. Production Ollama was used read-only.

## 17. Final recommendation

The architecture is sound and the minimal proof succeeds: **KORA operates as a
real Hermes-hosted agent** that orchestrates separate containerized services
(Ollama and Chroma proven end-to-end), retains governance and explainability in
plugin code, and requires no Hermes fork and no custom runtime layer. The next
real-implementation step is to expose the KORA-owned service boundaries (Honcho
approval-gated Memory Runtime, Graphify) over HTTP for the agent to call.

---

## Final verdict

**CONDITIONAL GO.**

The core architecture works (KORA as agent inside Hermes; KORA → Ollama and
KORA → Chroma proven against real services; governance + explainability in
plugin code; no fork; production untouched). Clearly identified incomplete
service boundaries to expose before production:

1. **Honcho memory write path** — expose the KORA Memory Runtime approval-gated
   service as an HTTP boundary for the agent (not rebuilt in staging).
2. **Graphify relationship boundary** — wire the serve layer as a reachable
   staging/real service and exercise one graph interaction.
3. **Accept/mitigate the no-pre-inference-veto limitation** on the API path.

Stop condition reached: no production migration, no Council, no Memory/Knowledge
redesign, no further infrastructure.

## Staging commands

```bash
cd Documentation/Phase14/Phase14-Migration/staging
./bootstrap.sh                          # start (isolated)
python3 -m pytest tests/test_kora_hermes.py -v   # 8 minimal checks
./bootstrap.sh down                     # teardown (keeps ./data)
./bootstrap.sh destroy                  # teardown + remove ./data
```
