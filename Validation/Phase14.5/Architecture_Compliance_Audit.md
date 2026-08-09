# Phase 14.5 — Architecture Compliance Audit

**Method:** Code inspection + runtime verification.

## Boundaries

| # | Requirement | Evidence | Result |
| --- | --- | --- | --- |
| 1 | Knowledge ≠ Memory ≠ Tools | Tool results never stored as Knowledge or Memory | ✅ |
| 2 | Graphify MCP ≠ Tool Platform | `GraphifyClient` reuses generic MCP transport but keeps graph ops; Tool Platform is a separate layer | ✅ |
| 3 | MCP ≠ entire Tool Platform | Tool Platform owns abstraction; MCP is one provider (local Ollama tools also supported) | ✅ |
| 4 | Discovery ≠ authorization | Discovered tools start disabled (`upsert_from_discovery` default disabled) | ✅ |
| 5 | Authorization ≠ execution | `ToolAuthorizer` gate before `ToolExecutor` | ✅ |
| 6 | Consequential tools governed | High-risk/destructive require approval | ✅ |
| 7 | Open WebUI ≠ Tool authority | No Open WebUI tool registry; KORA owns policy | ✅ |
| 8 | EventBus canonical | Tool lifecycle events on existing EventBus | ✅ |
| 9 | No autonomous tool loops | Strategy-driven single tool invocation; no multi-step planning | ✅ |
| 10 | Graphify remains graph provider | Graphify deployed independently; `query_graph`/`get_node`/`get_neighbors`/`shortest_path`/`graph_stats` preserved | ✅ |

## Runtime verification

- `pytest`: 173 passed.
- KORA `homelab/kora-runtime:14.5.0` healthy.
- Tool Platform: `ollama.list_models`, `ollama.list_running` registered + enabled.
- Real read-only invocation: `ollama.list_models` → returned model list (200, 8.7ms).
- Chat path: operational query → `stores_queried: ['tools']`; architecture → tools skipped.
- Graphify regression: `graphify health: True`, `graph_stats` served; Chroma/Graphify/Ollama healthy.

## Security / hygiene

- No secrets in new code; MCP keys via env/.env placeholders.
- MCP servers must be explicitly configured; discovery stays disabled.
- No arbitrary endpoint trust; no unauthorized execution.
