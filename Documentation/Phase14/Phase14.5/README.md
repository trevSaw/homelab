# Phase 14.5 — Tool Platform / MCP

**Status:** ✅ Implemented and validated

**Capability:** **KORA can interact with the world.**

## Architecture

Phase 14.5 introduces a governed Tool Platform under KORA Runtime:

```text
                         KORA Runtime
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
          Knowledge         Graph          Tool Platform
          Retrieval        Retrieval            │
              │               │                │
           Chroma          Graphify             ▼
                                         Tool Registry
                                               │
                                         Tool Authorization
                                               │
                                         Tool Execution
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                              ▼                ▼                ▼
                            MCP             Local           External
                           Servers          Services         Services
```

**Critical boundary:** Graphify's MCP integration is a Phase 14.4 Knowledge Graph
integration. It is NOT itself the Phase 14.5 Tool Platform. Graphify remains a
graph provider; the Tool Platform is a separate layer.

## Tool Platform

- **Tool abstraction** — tool_id (deterministic), name, description, input/output
  schemas, capabilities, risk, provider, enabled state, approval requirement.
- **Tool Registry** — registration, lookup, discovery, enable/disable, provider
  association, duplicate handling.
- **Tool Discovery** — controlled; MCP `tools/list`; discovery does NOT imply
  authorization (new tools start disabled).
- **Tool Authorization** — distinct from discovery; read-only/low-risk auto when
  enabled; high-risk/destructive require explicit approval.
- **Tool Execution** — KORA-owned executor with validation, authorization,
  timeout, provider resolution, error handling, result normalization.
- **Tool Result** — normalized (invocation_id, tool_id, success, result, error,
  duration_ms); tool results are NOT auto-stored as Knowledge or Memory.
- **Governance** — risk classification (read_only / low_risk_mutation /
  high_risk_mutation / destructive); consequential tools require approval.

## MCP

- **Generic MCP client** (`AI/KORA/Tools/mcp/client.py`) — MCP Streamable HTTP
  (JSON-RPC 2.0): initialize, capability negotiation, tools/list, tools/call,
  connection lifecycle, error handling, timeouts.
- **MCP tool provider** (`AI/KORA/Tools/providers/mcp.py`) — bridges the Tool
  Platform to a generic MCP client; discovery + invocation.
- **Graphify boundary** — `GraphifyClient` now reuses the generic MCP client for
  transport but keeps Graphify-specific operations (`query_graph`, `get_node`,
  `get_neighbors`, `shortest_path`, `graph_stats`) intact. Graphify is NOT part
  of the Tool Platform.

## Runtime integration

- Operational queries (models/status/list/health/metrics) select the `tools`
  store; enabled read-only tools are auto-invoked; results injected into context.
- Architecture queries still use Knowledge + Graphify; Memory remains off the
  chat path. No autonomous tool loops.
- Tool invocation events (`tool.registered`, `tool.enabled/disabled`,
  `tool.invocation.started/completed/failed`, `tool.discovered`) publish on the
  existing EventBus.

## Security

- MCP servers must be explicitly configured (`tools.yaml` `mcp_servers`); no
  arbitrary endpoints trusted.
- No secrets committed; `GRAPHIFY_API_KEY`/MCP keys via env/`.env`.
- Discovery ≠ authorization; high-risk tools require approval.

## Configuration

`AI/KORA/Config/tools.yaml` + `KORA_TOOLS_*` env overrides. Safe read-only local
tools (`ollama.list_models`, `ollama.list_running`) are registered by default.

## Deployment

`services/kora/` remains the KORA Runtime (`homelab/kora-runtime:14.5.0`).
Chroma, Graphify, and Ollama remain independently manageable Compose projects on
the shared external `ollama-net`. No host-level tool infrastructure.

## Files

| Area | Location |
| --- | --- |
| Tool model | `AI/KORA/Tools/models/tool.py` |
| Registry | `AI/KORA/Tools/registry/registry.py` |
| Authorization | `AI/KORA/Tools/auth/authorizer.py` |
| Execution | `AI/KORA/Tools/executor/executor.py` |
| Generic MCP | `AI/KORA/Tools/mcp/client.py` |
| MCP provider | `AI/KORA/Tools/providers/mcp.py` |
| Local Ollama tools | `AI/KORA/Tools/providers/local/ollama.py` |
| Facade | `AI/KORA/Tools/platform.py` |
| Config | `AI/KORA/Tools/config/tool_config.py` |
| Builder | `AI/KORA/Tools/builder.py` |
| Graphify (reused MCP) | `AI/KORA/Knowledge/graph/graphify.py` |
