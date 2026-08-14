---
title: Hermes Service README
document_type: README
service: hermes
owner: Homelab
status: Active
version: 14.1.0
last_reviewed: 2026-08-11
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - AI/Hermes/README.md
  - AI/KORA/Config/hermes_registration.yaml
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# Hermes (KORA runtime platform)

Hermes is the **generic agent/runtime platform**. KORA is a **Hermes Agent**
(head intelligence/governance agent) hosted inside it. There is **no standalone
KORA Runtime**; the old standalone runtime was retired 2026-08-11.

## Final architecture (Phase 14 closeout)

```text
Open WebUI → Hermes (api_server :8642, model "KORA") → KORA HEAD AGENT
                                                       ├── Honcho (native provider)
                                                       ├── Chroma
                                                       ├── Graphify
                                                       ├── Ollama (model.default)
                                                       └── MCP / Tools (Hermes tool runtime)
```

| Concern | Final decision |
| --- | --- |
| Runtime | Hermes v0.17.0 (api_server platform) |
| KORA | Hermes Agent — plugin at `/opt/data/plugins/kora` |
| Primary chat path | **Yes** — Open WebUI → Hermes → KORA → Ollama |
| Model | Controlled by Hermes `config.yaml model.default` (currently `gpt-oss:20b-cloud`; was `qwen3:8b` before Phase 16 switch) |
| Memory | Hermes native honcho provider (workspace `kora`, peer `user`) |
| KORA identity | Presented as **KORA** (API_SERVER_MODEL_NAME=KORA) |

## Notes

- KORA identity, governance, Memory policy, Knowledge policy, and
  explainability are KORA-owned; Hermes provides routing, sessions, agent
  loop, tool/MCP transport, and model plumbing.
- Historical Phase 14.1 "thin execution layer" posture and the delegation
  design (`delegation: base_url: http://kora:8080/v1`) are superseded by the
  retirement of the standalone KORA Runtime.
- Design/migration docs: `Documentation/Phase14/Phase14-Migration/`.

## MCP (native)

Hermes natively supports MCP servers via `mcp_servers` in `config.yaml`
(stdio or Streamable HTTP `url`). Enabled servers' tools are auto-exposed to
agents (default `include_default_mcp_servers`), registered under toolset
`mcp-<server>` with names `mcp_<server>_<tool>`.

Currently configured (read-only, whitelisted):

```yaml
mcp_servers:
  jdocmunch:
    command: uvx
    args: [jdocmunch-mcp]
    env:
      HOME: /opt/data
      JDOCMUNCH_SHARE_SAVINGS: "0"
    tools:
      include:
        - index_local
        - search_sections
        - get_section
        - get_sections
        - get_section_excerpt
        - get_toc
        - get_toc_tree
  context7:
    url: https://mcp.context7.com/mcp
    tools:
      include:
        - resolve-library-id
        - query-docs
  graphify:
    url: http://graphify:8080/mcp
    tools:
      include:
        - query_graph
        - get_node
        - get_neighbors
        - get_community
        - god_nodes
        - shortest_path
        - graph_stats
```

- **Graphify** (`http://graphify:8080/mcp`, Streamable HTTP, local): **7** safe
  read-only graph/relationship tools (query_graph, get_node, get_neighbors,
  get_community, god_nodes, shortest_path, graph_stats) — NOT just graph_stats.
  Disabled: PR/repository tools (`list_prs`, `get_pr_impact`, `triage_prs`).
- **Context7** (`https://mcp.context7.com/mcp`, remote Streamable HTTP):
  2 read-only tools for targeted current library/API documentation
  (`resolve-library-id`, `query-docs`). Requires outbound internet; free API
  key optional (`headers: Authorization: Bearer <key>`).
- **jDocMunch** (stdio subprocess via `uvx jdocmunch-mcp`, local):
  7 read-only tools for **local** homelab documentation retrieval
  (`index_local`, `search_sections`, `get_section`, `get_sections`,
  `get_section_excerpt`, `get_toc`, `get_toc_tree`). Corpus = homelab
  `Documentation/` mounted read-only at `/opt/data/homelab-docs`; index
  persisted under `/opt/data`. Free for personal (non-commercial) use.
- Tool governance policy: see `Documentation/Phase16/README.md`.

### Phase 16.x expansion (2026-08-13)

Evaluated jCodeMunch, jDocMunch, jDataMunch, GitHub MCP, Docker MCP, Proxmox
MCP, Filesystem MCP. **Installed:** jDocMunch (local docs retrieval — see
above). **Deferred:** jCodeMunch (no meaningful code corpus; broad mount would
expose secrets), jDataMunch (no data corpus), GitHub (no PAT), Filesystem (no
need). **Rejected:** Docker MCP (docker-socket control), Proxmox (no Proxmox;
upstream 404). Context7 + Graphify + jDocMunch are the MCP servers. Full
decision matrix in `Documentation/Phase16/README.md` (Part 4).

- Server: Graphify (`http://graphify:8080/mcp`, Streamable HTTP).
- Exposed tool: `mcp_graphify_graph_stats` (read-only graph summary stats).
- No other MCP tools are exposed.

### MCP verification status

- ✅ MCP server configured, discovered, and the tool registered
  (`hermes mcp list` shows `graphify` enabled, 1 tool selected; api_server
  toolset `graphify` is enabled for KORA).
- ✅ **Structured MCP tool calling verified** with KORA on `gpt-oss:20b-cloud`:
  KORA emitted a genuine structured `tool_calls` message for
  `mcp_graphify_graph_stats`, Hermes executed it, Graphify returned real data
  (19 nodes, 28 edges, 0 communities), and KORA incorporated the result into
  its response ("The graph has 19 nodes, 28 edges and 0 communities").
- ⚠️ Note: when the model passes the optional `project_path` argument (e.g.
  `"/opt/data"`), Graphify resolves `<project_path>/graphify-out/graph.json`
  and errors; instructing the model to omit it (use the server default) returns
  real data. This is a model argument-filling behavior, not an MCP defect.
- Historical note: `qwen3:8b` (previous KORA model) emitted MCP tool
  invocations as **text JSON** instead of structured `tool_calls`, so execution
  did not occur; `gpt-oss:20b-cloud` resolves this (see Phase 16 model switch).

## Migration

| Item | Decision |
| --- | --- |
| Prior SoT | `/mnt/monarch/appdata/hermes/compose.yml` |
| Compose SoT now | `services/hermes/compose.yaml` (**live ownership migrated 2026-08-01**) |
| Data | **Preserved** `/mnt/monarch/appdata/hermes` |
| Legacy appdata compose | Disabled; see appdata `README.COMPOSE_OWNERSHIP.md` |

## Exceptions

| Item | Exception |
| --- | --- |
| Image pin | Pinned to Hermes Agent v0.17.0 digest (see compose) |
| Healthcheck | Best-effort against api_server `/health` (`:8642`) |
