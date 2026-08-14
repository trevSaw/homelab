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
- New servers must be explicitly allowlisted and reachable on `ollama_ollama-net`
  (or the configured network / outbound internet for remote servers).
- Re-verify each new tool's structured-call execution on the active model.

---

## Part 3 — MCP tool expansion: Context7 (context / token efficiency)

### Candidate investigation

| Candidate | Verdict | Reason |
| --- | --- | --- |
| **Context7** (`upstash/context7`) | ✅ **Accepted** | Official MCP server; remote Streamable HTTP endpoint `https://mcp.context7.com/mcp`; 2 read-only tools (`resolve-library-id`, `query-docs`); targeted live-doc retrieval; works without a key (rate-limited; free API key optional). Requires outbound internet only. |
| **Chisel** | ❌ Rejected | No genuine, verifiable MCP server matching the described code-context use case; candidate ambiguity + required filesystem access could not be safely restricted under existing Docker governance. |
| **CodeCortex** | ❌ Rejected | The upstream project (`AnandPilania/CodeCortex`) is a **static code-quality analyzer CLI + web dashboard** (LOC/complexity/dead-code metrics), **not an MCP server**; it provides no semantic/targeted context retrieval and would require custom wrapping (forbidden). |

Per Phase 16 policy, a smaller MCP stack is preferred over forced infrastructure.

### Context7 configuration (Hermes-native)

```yaml
mcp_servers:
  context7:
    url: https://mcp.context7.com/mcp
    tools:
      include:
        - resolve-library-id
        - query-docs
```

- Transport: Streamable HTTP (remote, Context7's managed service).
- Runs: remote service; no local container added. Hermes is the MCP client.
- API key: optional (free key from context7.com adds higher rate limits); add via
  `headers: Authorization: Bearer <key>` if obtained.
- Tools enabled: `resolve-library-id` (library lookup), `query-docs` (targeted
  current documentation retrieval). Both read-only.
- Purpose: retrieve **targeted, current** library/API documentation (Docker,
  Hermes, MCP, Python libs, etc.) instead of dumping full docs into context.
- Redundancy: **not** redundant with Chroma/Graphify/Honcho — Context7 is live
  external library documentation; Chroma remains our own-knowledge platform.

### Token / context efficiency (verified qualitatively)

- `query-docs` returns **relevant documentation snippets for a specific query**,
  not full documentation corpora — targeted retrieval avoids dumping large raw
  content into KORA's context.
- `resolve-library-id` returns a small ranked library match (id, name, summary),
  keeping context tiny.
- Both tools return compact text results that KORA incorporates directly.
- (Quantitative token measurement deferred — see limitations.)

### Verification status

- ✅ Hermes discovers `context7` (2 tools selected, enabled) — verified via
      `hermes mcp list`.
- ✅ KORA emits structured `mcp_context7_resolve_library_id` + `mcp_context7_query_docs`
      calls (genuine `tool_calls`).
- ✅ Hermes executes both; Context7 returns real documentation (Docker Compose
      healthcheck docs, `/docker/compose`).
- ✅ KORA incorporates the result ("The /docker/compose docs contain an example
      of a healthcheck in a compose service...").

### Token / context efficiency (observed)

- `query-docs` returned **targeted healthcheck documentation snippets** for the
  query, not the full Docker Compose corpus — KORA's answer was built from the
  retrieved snippet without dumping large raw content into context.
- `resolve-library-id` returned a small ranked library match, keeping that step
  minimal.
- No formal token benchmark was run (per scope); the qualitative targeted-vs-full
  retrieval behavior is confirmed.

### Known limitations (Context7)

- Requires outbound internet to `mcp.context7.com`; rate limits apply without an
  API key.
- Context7 indexes community-contributed library docs; accuracy/coverage vary by
  library (see Context7's own disclaimer).
- Remote service — not fully self-hosted (backend is Context7's managed API).

---

## Part 4 — Phase 16.x MCP expansion (candidate evaluation)

**Status:** ✅ Complete (2026-08-13) — candidates evaluated and **jDocMunch
installed + verified** (implementation pass). Docker/Proxmox rejected; the
remaining candidates deferred with documented prerequisites. Per Phase 16
policy, a smaller MCP stack is preferred over forced infrastructure; only
jDocMunch offered a clear, safe, immediate-value integration.

### Candidate decisions

| Candidate | Verdict | Reason |
| --- | --- | --- |
| **jCodeMunch** (`jgravelle/jcodemunch-mcp`) | ⏸ **Deferred** | Genuine MCP server, read-only, excellent token efficiency (symbol-level retrieval, 27.9× vs grep-and-read), non-root Dockerfile, personal-use license OK. But it requires **building a code index** for a corpus. The homelab repo is documentation/ops-centric with only small helper scripts (no meaningful code corpus), and a broad repo mount would expose `.env`/secret files. Deferred pending a safe, meaningful code corpus (see "How to revisit"). |
| **jDocMunch** (`jgravelle/jdocmunch-mcp`) | ✅ **Installed + verified** | Genuine, read-only, section-level doc retrieval (strong token efficiency), free for personal use. Installed as a Hermes-native **stdio** MCP server (`uvx jdocmunch-mcp`) with the homelab `Documentation/` tree mounted read-only at `/opt/data/homelab-docs`. Index persists under `/opt/data` (HOME override). Allowlisted retrieval tools: `index_local`, `search_sections`, `get_section`, `get_sections`, `get_section_excerpt`, `get_toc`, `get_toc_tree`. Context7 remains for external/current docs; jDocMunch serves **local** Brainiac docs. |
| **jDataMunch** (`jgravelle/jdatamunch-mcp`) | ⏸ **Deferred** | Genuine, read-only, server-side aggregation (≈25,000× token reduction on large CSVs). No tabular corpus exists in the homelab; stdio-only, no official image. Deferred. |
| **GitHub MCP** (`github/github-mcp-server`) | ⏸ **Deferred** | Official, MIT, supports `--read-only` + toolset filtering, no host access — clean. But it **requires a GitHub credential** (fine-grained PAT or OAuth) which is not available, and there is no active GitHub use case. Deferred until a user-supplied read-only PAT + use case exist. |
| **Docker MCP** (official `docker/mcp-gateway` / catalog) | ❌ **Rejected** | Requires Docker daemon/socket control and launches/manages arbitrary server containers — directly violates our container governance ("no docker socket beyond what is required"). |
| **Proxmox MCP** (`GethosTheWalrus/proxmox-mcp-server`) | ❌ **Rejected** | Specified upstream repo does not exist (404); no Proxmox infrastructure exists in this homelab (Docker-based). |
| **Filesystem MCP** (official `modelcontextprotocol/servers`) | ⏸ **Deferred** | Official, MIT, constrainable to a single read-only mount. But it is a **blunt primitive** (raw file dumps, no retrieval/token efficiency) and KORA's doc-retrieval needs are already served by Context7 (live) + jDocMunch (local). Deferred. |

### What remains unchanged

- **Installed + verified:** `context7` (`resolve-library-id`, `query-docs`),
  `graphify` (7 read-only tools), and **new** `jdocmunch` (7 read-only tools).
- No KORA code, no custom MCP infra, no new containers (jDocMunch runs as a
  stdio subprocess inside Hermes), no new credentials.

### jDocMunch — implementation

- **Upstream:** `jgravelle/jdocmunch-mcp` (PyPI `jdocmunch-mcp` v1.133.0),
  dual-use license (free for personal/non-commercial use).
- **Transport:** Hermes-native **stdio** (`command: uvx`, `args: [jdocmunch-mcp]`),
  running as a subprocess inside the Hermes container. `HOME=/opt/data` so the
  index and uv cache persist on the appdata volume.
- **Corpus:** homelab `Documentation/` mounted **read-only** at
  `/opt/data/homelab-docs` (KORA's own knowledge base). Index is built by KORA
  via `index_local` and stored under `/opt/data` — the source corpus is never
  modified.
- **Allowlisted tools:** `index_local`, `search_sections`, `get_section`,
  `get_sections`, `get_section_excerpt`, `get_toc`, `get_toc_tree` (read-only
  retrieval + local indexing).
- **Disabled (not exposed):** the other ~57 jDocMunch tools (health/coverage,
  OpenAPI spec tools, delete-safety checks) — not in the allowlist.
- **Security:** read-only corpus mount; no network egress (lexical BM25 offline;
  savings counter disabled via `JDOCMUNCH_SHARE_SAVINGS=0`); no filesystem
  access outside the mounted corpus + its own index dir.
- **Purpose/relationship:** jDocMunch = **local** Brainiac documentation;
  Context7 = **external/current** library docs. Complementary, not duplicative.
- **Verification:** ✅ Hermes discovers `jdocmunch` (7 tools, enabled). Index built
  via the CLI (`jdocmunch-mcp index-local --path /opt/data/homelab-docs`) and
  persisted under `/opt/data`. End-to-end KORA verification passed: KORA emitted
  structured `mcp_jdocmunch_search_sections` (repo `local/homelab-docs`) then
  `mcp_jdocmunch_get_section`, Hermes executed both, and KORA reported the real
  retrieved section ("Phase 16 — MCP / Tools Platform" from the local docs).
  Note: `index_local`/`search_sections`/`get_section` require the `path`/`repo`/
  `section_id` arguments — the model must supply them (passing them explicitly
  in the prompt yields correct tool calls).

### How to revisit (future)

- **jCodeMunch:** provide a safe, meaningful code corpus (a real codebase dir
  with no `.env`/secrets), mount it read-only, then add a stdio `mcp_servers`
  entry (`command: uvx, args: [jcodemunch-mcp]`) with a read-only retrieval
  allowlist (`search_symbols`, `get_symbol_source`, `get_file_outline`,
  `find_importers`, `get_blast_radius`). Verify a structured tool call.
- **jDataMunch:** provide a real tabular corpus (CSV/JSONL), mount read-only,
  stdio entry + read-only allowlist (`describe_dataset`, `sample_rows`,
  `get_rows`, `aggregate`).
- **GitHub MCP:** supply a fine-grained read-only PAT (kept out of git, e.g. in
  Hermes `~/.hermes/.env` / volume env), run the official image with
  `--read-only`, allowlist `repos`, `issues` (read), `pull_requests` (read),
  `search_*`.
- **Filesystem MCP:** only if a concrete read-only file-access need arises that
  jDocMunch/Context7 cannot cover.



