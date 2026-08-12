# Phase 16 — MCP / Tools Platform

**Status:** ✅ Complete (2026-08-12)

## Purpose

Establish Hermes-native MCP as KORA's tool mechanism, prove reliable structured
tool execution, expose a governed read-only Graphify tool set, and document the
tool allowlist/security model. Uses Hermes's native MCP — no custom tool
runtime, parser, proxy, or orchestration.

## Part 1 — KORA model switch: qwen3:8b → gpt-oss:20b

This established the inference model that supports structured tool calling
(`gpt-oss:20b-cloud`).

## What changed (model)

Hermes runtime model configuration only (config, not code):

```yaml
model:
  default: gpt-oss:20b-cloud   # was: qwen3:8b
  provider: custom             # unchanged
  base_url: http://ollama:11434/v1  # unchanged
providers:
  gpt-oss:20b-cloud:
    api: http://ollama:11434/v1
    name: gpt-oss:20b-cloud
    default_model: gpt-oss:20b-cloud
```

- **Why:** `qwen3:8b` (CPU-bound) emitted MCP tool invocations as **text JSON**
  (`{"tool_call": ...}`) instead of structured `tool_calls`, so Hermes never
  executed MCP tools. `gpt-oss:20b-cloud` (the gpt-oss 20B model served by
  Ollama; note the id is `gpt-oss:20b-cloud`, not bare `gpt-oss:20b`) emits
  genuine structured tool calls.
- **Not changed:** KORA agent architecture, Honcho, Chroma, Graphify, Open WebUI
  access control, MCP server config (`graphify` / `graph_stats` still the only
  exposed MCP tool), Council files, no new containers, no custom runtime/parser/
  proxy, no Hermes fork.

## Results

| Item | Result |
| --- | --- |
| Model used | `gpt-oss:20b-cloud` (via Ollama, cloud-hosted) |
| KORA responds | ✅ (`OK`, identity digest intact) |
| KORA identity | ✅ `[KORA]` digest + classification/strategy present |
| Honcho connected | ✅ memory provider active (context injection continues) |
| Structured tool call | ✅ genuine `tool_calls` (`mcp_graphify_graph_stats`) |
| Hermes executed MCP call | ✅ |
| Graphify returned real data | ✅ `Nodes: 19, Edges: 28, Communities: 0` |
| KORA incorporated result | ✅ "The graph has 19 nodes, 28 edges and 0 communities." |
| New containers / runtime | ❌ none |
| New MCP tools exposed | ❌ none (only `graph_stats`) |

## Performance observations

- **Model generation (gpt-oss:20b-cloud):** cloud-hosted, fast (earlier direct
  turns returned in seconds) — versus `qwen3:8b` (CPU-bound, ~50-100s per LLM
  call).
- **Total KORA turn time (~184s):** dominated by the **Honcho dialectic**
  (qwen3:8b via Honcho's own env config, ~180s timeout) which runs on every
  turn and is **independent** of the KORA model. This is the remaining
  latency bottleneck (separate config concern, out of scope).
- **Tool-call path:** structured call + execution + incorporation adds minimal
  latency beyond the base turn.

## Remaining limitations

- Bare `gpt-oss:20b` is not available; the model id is `gpt-oss:20b-cloud`
  (cloud-served). If local/offline inference is required, revisit model choice.
- If the model supplies the optional `project_path` argument to `graph_stats`,
  Graphify resolves `<project_path>/graphify-out/graph.json` and errors
  (default graph is `/data/graph.json`). Omit `project_path` to use the default.
- Honcho dialectic latency (qwen3:8b) remains a separate, documented issue.
- No further MCP tools, Council implementation, or autonomous workflows were
  added (per scope).

## Verification path

`Open WebUI → Hermes → KORA → (structured MCP tool_call) → Hermes MCP execution → Graphify graph_stats → result → KORA synthesis`

---

## Part 2 — MCP / Tools platform finalization

### Hermes-native MCP architecture

```text
Open WebUI → Hermes v0.17.0 → KORA HEAD AGENT
                                  │  Hermes-native MCP (mcp_servers)
                                  ▼
                            Graphify (Streamable HTTP :8080/mcp)
```

- MCP servers configured in Hermes `config.yaml` under `mcp_servers`.
- Enabled servers' tools auto-exposed to KORA (toolset `graphify` /
  `mcp-<server>`), named `mcp_<server>_<tool>`.
- Explicit tool allowlisting via `mcp_servers.<name>.tools.include`.
- No KORA code, wrappers, proxies, parsers, or custom tool infrastructure.

### Current MCP server

| Server | Transport | Enabled tools (allowlist) |
| --- | --- | --- |
| `graphify` | Streamable HTTP `http://graphify:8080/mcp` | `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `shortest_path`, `graph_stats` |

### Tool classification & decision

| Tool | Class | Enabled | Reason |
| --- | --- | --- | --- |
| `query_graph` | A — safe read-only search | ✅ | BFS/DFS graph search over served graph |
| `get_node` | A — safe read-only lookup | ✅ | Node detail lookup |
| `get_neighbors` | A — safe read-only lookup | ✅ | Neighbor/edge lookup |
| `get_community` | A — safe read-only lookup | ✅ | Community membership lookup |
| `god_nodes` | A — safe read-only | ✅ | Most-connected nodes (core abstractions) |
| `shortest_path` | A — safe read-only | ✅ | Path search between concepts |
| `graph_stats` | A — safe read-only | ✅ | Summary statistics |
| `list_prs` | C — PR/repository operational | ❌ | Repository operational; not general knowledge |
| `get_pr_impact` | C — PR/repository operational | ❌ | Repository operational |
| `triage_prs` | C — PR/repository operational | ❌ | Repository operational / triage |

### Tool governance policy (Phase 16)

- **READ-ONLY tools** — may be exposed to KORA when explicitly allowlisted.
- **WRITE / MUTATING tools** — must NOT be enabled merely because they exist.
- **ADMINISTRATIVE tools** — must remain disabled unless explicitly approved.
- **PR / repository tools** — treated separately from general knowledge tools;
  not enabled in the initial set.
- **Future MCP servers** — must be explicitly allowlisted.
- Principle: *"Existence of an MCP tool does not mean KORA is authorized to use it."*

### Verification results

| Tool | Structured call | Executed | Real result | Incorporated |
| --- | --- | --- | --- | --- |
| `graph_stats` | ✅ | ✅ | Nodes: 19, Edges: 28, Communities: 0 | ✅ "The graph has 19 nodes, 28 edges and 0 communities." |
| `query_graph` | ✅ | ✅ | BFS depth=2, 2 nodes (KORA, Orchestration) + edge | ✅ reported traversal |
| `get_neighbors` | ✅ | ✅ | Neighbors of KORA (Orchestration, kora.md) | ✅ reported neighbors |

- Model: `gpt-oss:20b-cloud` (verified structured `tool_calls`).
- `qwen3:8b` previously failed structured MCP calling in the full KORA/Hermes
  context (emitted text JSON) — not worked around.

### Known limitations

- Honcho dialectic latency (`qwen3:8b`, ~180s/turn) is separate and independent
  of the KORA model; not addressed here.
- If a model supplies the optional `project_path` argument, Graphify resolves
  `<project_path>/graphify-out/graph.json` and errors; omit it to use the
  default graph.
- Bare `gpt-oss:20b` id is unavailable; the model id is `gpt-oss:20b-cloud`.
- PR tools remain disabled pending explicit approval.

### Future MCP expansion guidance

- Add tools only via `mcp_servers.<name>.tools.include` (Hermes-native).
- New servers must be explicitly allowlisted and reachable on `ollama_ollama-net`.
- Re-verify each new tool's structured-call execution on the active model.

