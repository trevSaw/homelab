# Phase 16 — KORA Model Switch: qwen3:8b → gpt-oss:20b

**Status:** ✅ Complete (2026-08-12)

## What changed

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
