---
title: Hermes Service README
document_type: README
service: hermes
owner: Homelab
status: Active
version: 25.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0011-KORA-Heavy-Coding-Hermes-Delegation-OpenCode-Go.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - Architecture/decisions/ADR-0013-Discord-Native-Transport.md
  - Documentation/Phase3/KORA_Controlled_Administration.md
  - Documentation/Phase4/Discord_Transport.md
  - Documentation/Phase22/KORA_OpenCode_Go_Migration.md
  - AI/Hermes/README.md
  - AI/KORA/Config/hermes_registration.yaml
  - Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md
---

# Hermes (KORA runtime platform)

Hermes is the **generic agent/runtime platform**. KORA is a **Hermes Agent**
(head intelligence/governance agent) hosted inside it. There is **no standalone
KORA Runtime**; the old standalone runtime was retired 2026-08-11.

## Architecture (Phase 22)

```text
Open WebUI → Hermes (api_server :8642, model "KORA") → KORA HEAD AGENT
   ├── default model: Ollama gpt-oss:20b-cloud (general work)
   ├── heavy coding: KORA → delegate_task → Hermes child → OpenCode Go (deepseek-v4-flash)
   ├── Honcho (native provider) / Chroma / Graphify
   └── MCP / Tools (Hermes tool runtime) + skills + sanitized workspace
```

| Concern | Final decision |
| --- | --- |
| Runtime | Hermes **v0.21.4** (2026.9.21, digest-pinned) |
| KORA | Hermes Agent — plugin at `/opt/data/plugins/kora` |
| Primary chat path | **Yes** — Open WebUI → Hermes → KORA → Ollama (`gpt-oss:20b-cloud`) |
| Heavy coding model | Hermes delegation → OpenCode Go (`deepseek-v4-flash`); key `OPENCODE_GO_API_KEY` in `services/hermes/.env` |
| Workspace | Sanitized git repo `/opt/data/homelab-workspace` (no `.env`); canonical repo never mounted; apply via `scripts/kora-apply.sh` |
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
(stdio or Streamable HTTP `url`). Enabled servers' tools are registered under
toolset `mcp-<server>` (alias `<server>`) with names `mcp_<server>_<tool>`.

**Platform exposure (current reality):** which MCP tools a platform actually
sees is governed by `platform_toolsets.<platform>`. For `api_server` (normal
KORA via Open WebUI) the list is currently
`[connections, file, kora, taskbridge, terminal, delegation]`. Because
`taskbridge` is an explicit MCP server in that list, Hermes' MCP-merge logic
(`_merge_mcp_servers`) treats it as an allowlist entry and suppresses the
default auto-inclusion of the other servers — so **only `taskbridge` MCP tools
are exposed to normal KORA sessions**. `graphify`, `context7`, and `jdocmunch`
remain configured/enabled as servers but are **not** currently in the
`api_server` toolset (see "MCP verification status" below). Adding them back to
`platform_toolsets.api_server` is deferred; it is a configuration change, not
an architecture change.

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

> **Phase 1 (2026-09-27) reality check:** the bullets below record historical
> verification. Under the current `platform_toolsets.api_server` list, only the
> `taskbridge` MCP server is exposed to normal KORA (api_server) sessions;
> `graphify`/`context7`/`jdocmunch` tools are **not** currently in that
> toolset, so normal KORA must not be told they are directly available. Their
> servers remain configured and enabled globally (`hermes mcp list` shows all
> four enabled).

- ✅ MCP servers configured, discovered, and registered globally (`hermes mcp
  list` shows `jdocmunch`, `context7`, `graphify`, `taskbridge` enabled).
  Historical note: at the time of the Phase 16 verification the `api_server`
  toolset did not list an MCP server, so default inclusion exposed `graphify`;
  after `taskbridge` was added to the list, only `taskbridge` is exposed.
- ✅ **Structured MCP tool calling verified** (historical) with KORA on
  `gpt-oss:20b-cloud`: KORA emitted a genuine structured `tool_calls` message
  for `mcp_graphify_graph_stats`, Hermes executed it, Graphify returned real
  data (19 nodes, 28 edges, 0 communities), and KORA incorporated the result
  into its response ("The graph has 19 nodes, 28 edges and 0 communities").
- ⚠️ Note: when the model passes the optional `project_path` argument (e.g.
  `"/opt/data"`), Graphify resolves `<project_path>/graphify-out/graph.json`
  and errors; instructing the model to omit it (use the server default) returns
  real data. This is a model argument-filling behavior, not an MCP defect.
- Historical note: `qwen3:8b` (previous KORA model) emitted MCP tool
  invocations as **text JSON** instead of structured `tool_calls`, so execution
  did not occur; `gpt-oss:20b-cloud` resolves this (see Phase 16 model switch).

## qBittorrent read-only live inspection (Phase 2)

KORA can answer live torrent questions (seeding/downloading/stalled/completed,
counts, transfer speeds) via dedicated **read-only** KORA plugin tools that
call the qBittorrent WebUI API directly:

- `kora.qbit_torrents` — list torrents (optional `filter`:
  `all|downloading|seeding|completed|paused|active|inactive|stalled|
  stalled_uploading|stalled_downloading|errored`; optional `limit`).
- `kora.qbit_transfer_info` — global upload/download speeds and session totals.
- `kora.qbit_app_version` — live API health/version.
- `kora.qbit_categories`, `kora.qbit_tags` — read-only categories/tags.

**What it exposes:** only GET endpoints (`/api/v2/torrents/info`,
`/api/v2/transfer/info`, `/api/v2/app/version`, `/api/v2/torrents/categories`,
`/api/v2/torrents/tags`). **Deliberately NOT exposed:** every mutation
operation (pause/resume/delete/add/recheck/reannounce/limits/category/priority
/preferences). Read-only enforcement is implemented in the tool handlers — no
mutation handlers or endpoints exist in the capability.

**Authentication/secret handling:** qBittorrent 4.5.x has a single WebUI
account and no read-only token, so the integration uses the WebUI credentials
(`KORA_QBIT_USER`/`KORA_QBIT_PASS`) which live **only** in the gitignored
`services/hermes/.env` and are injected into the container via `env_file` +
`environment`. They are never committed, logged, printed, or included in
diagnostics. Limitation: the WebUI account can technically mutate via the API;
the integration restricts itself to read-only calls, but a prompt-level
misuse would be prevented by the tool layer, not by a read-only account.

**Network path:** Hermes reaches qBittorrent's already-published WebUI port
(`:8080`, bound to `0.0.0.0` by `services/Hotio/compose.yml`) through the host
Docker bridge using the container's default gateway — **no networking change,
no new port, no public exposure**. Optional `KORA_QBIT_BASE_URL` overrides the
auto-detected base URL.

**Security boundary:** unchanged — Hermes stays UID 10000, no Docker socket,
no host filesystem mount, no host-level privilege. qBittorrent remains internal
and is not routed through Traefik. **Docker socket access is intentionally NOT
required** for live qBittorrent inspection: application-level state comes from
the qBittorrent API, and container-level state comes from `/opt/data/docker-state/*`.

**How KORA uses it:** the KORA plugin's `QBIT_DIRECTIVE` instructs the model to
prefer these live tools over the docker-state snapshot for torrent questions,
treat the snapshot only as fallback container-level context, never infer
torrent state from container state, and report "cannot determine" (never
"absent"/"zero") if authentication or the API is unavailable.

## Controlled Docker administration (Phase 3)

KORA can inspect **live** Docker state and perform a deliberately narrow set of
lifecycle operations through dedicated `kora.docker_*` plugin tools. Hermes
still has **no Docker socket**; the tools call the narrow `docker-admin` helper
(see `services/docker-admin/README.md` and
`Documentation/Phase3/KORA_Controlled_Administration.md`) over the internal
`kora-admin` network with a bearer token read from
`/opt/data/docker-admin.token`.

| Tool | Type | Purpose |
| --- | --- | --- |
| `kora.docker_list` | read | all containers (state/health/image/networks/ports) |
| `kora.docker_inspect` | read | one container (state, health, mounts, env **keys only**) |
| `kora.docker_logs` | read | recent logs (`tail`) |
| `kora.docker_health` | read | one container health/state |
| `kora.docker_image` | read | image tags/id/size/digests (accepts a container name) |
| `kora.docker_networks` / `kora.docker_volumes` | read | list or inspect one |
| `kora.docker_restart` | **write** | restart one container (confirm=true), then verify |
| `kora.docker_compose_validate` | read | `docker compose config -q` for a canonical project |
| `kora.docker_compose_up` | **write** | recreate/deploy a canonical project (confirm=true), then verify |

**Boundary:** no delete/remove/prune/exec/build/pull, no arbitrary `docker`
command, no Docker TCP, no public exposure. Restart/deploy refuse the control
plane (`hermes`, `docker-admin`). Writes require `confirm: true` and are
verified after the fact. Live Docker data now takes precedence over
`/opt/data/docker-state/*`, which remains fallback/contextual evidence. Failure
to inspect is still never evidence of absence.

## External web research (Phase 5)

KORA has governed external web research through the **self-hosted SearXNG**
service (`services/searxng`, internal-only, ADR-0014) using Hermes' **native
`web` toolset** — no custom bridge and no new MCP server (ADR-0015).

- **Mechanism:** `web_search` is backed by the bundled Hermes SearXNG provider
  (`plugins/web/searxng`), selected by `SEARXNG_URL=http://searxng:8080` and
  `web.search_backend: searxng` in `config.yaml`.
- **Parity:** the `web` toolset is enabled for **both** `api_server` (Open WebUI)
  and `discord`, so both transports get the same research capability.
- **Extraction:** `web_extract` is intentionally unavailable — SearXNG is
  search-only and the alternative extract providers are third-party.
  `web.keyless_fallback: false` prevents silent third-party egress. Pages and
  repositories are fetched with `terminal` (curl/git) or via delegation.
- **Policy (`RESEARCH_DIRECTIVE`):** local homelab facts use the existing
  homelab tools; external/current facts use `web_search` (SearXNG); deep
  repository/code research is delegated to the OpenCode Go child. SearXNG is
  **discovery only — never authority**; prefer upstream/official sources; never
  present a snippet as a verified fact; never invent versions/URLs.
- **Engine tuning:** this host's egress IP is blocked/CAPTCHA'd by most general
  engines, so SearXNG's `github` engine (official GitHub API) is enabled and
  categorised into `general` as the dependable software-discovery path.
- **Defect fix:** KORA's `pre_tool_call` destructive-name guard matched the
  substring `"rmi"` in `terminal`, silently blocking all shell use. It now
  matches destructive **tokens** (`*.remove`, `*.prune`, `*.exec`, ...), so
  `terminal` works while destructive operations remain blocked.

Validation (Kapowarr, 2026-10-06): KORA discovered `Casvt/Kapowarr` via
`web_search`, delegated the deep repo work to the OpenCode Go child, which
cloned the repo and read `docker-compose.yml`, and produced a governed plan
citing the upstream source. See
`Validation/Phase5/KORA_Web_Research_Validation.md`.

### Research evidence/provenance contract (Phase 5.1)

The first real task promoted model inference (invented image tag, fabricated
paths/hostname) into factual deployment claims. Root cause was **not** just a
weak directive: Hermes' hook-output spill
(`hooks.output_spill.max_chars`, default 10000) replaced KORA's ~18 KB
`pre_llm_call` context with a **500-char head + 500-char tail**, so the research
rules never reached the model. **Follow-up (Phase 5.1b):** the directive set was
compacted to **9,750 chars** (< the 10,000 cap), so the **full** directive payload
now reaches the model (all of `LIVE_STATE`, `QBIT`, `DOCKER_ADMIN`, `DELEGATION`,
`RESEARCH` included); the contract is still bookended as a safeguard. The
contract is injected only for research/plan/deployment intent (deterministic
gate) so ordinary conversation is never forced into the four-section format.
Fix (`services/hermes/plugin/kora/__init__.py`, `plugin.yaml` v0.4.1):

- **`RESEARCH_EVIDENCE_CONTRACT`** — a mandatory, compact (~1 KB) output
  contract: four sections (UPSTREAM FACTS / HOMELAB FACTS / PROPOSED DESIGN
  DECISIONS / UNRESOLVED QUESTIONS), current-task source of authority, evidence
  taxonomy, no invented values, conflict-stop, no unread citations, placeholder
  ban, discovery-failure semantics, delegation integrity. **Bookended first and
  last** in `pre_llm_call` so it always survives the head/tail spill. It applies
  to research/plan deliverables only, not ordinary conversation.
- **`_evidence_check` guard** in `transform_llm_output` — deterministic
  defense-in-depth that flags placeholder tokens and Compose plans missing the
  four evidence headings (visible "DO NOT TREAT AS DEPLOYABLE" note; never
  blocks, no new runtime/privilege).

Validated (read-only): Kapowarr → real `V1.3.2` + `mrcas/kapowarr:latest`, no
invented tag/paths, `/health` flagged unverified; a generic service (Uptime
Kuma) generalized correctly; ordinary conversation unaffected; a delegated
child's value preserved verbatim; a fictional project reported as unable to
verify with no fabricated values. See
`Validation/Phase5/KORA_Web_Research_Validation.md` §8–12.

## Discord transport (Phase 4)

Discord is added as a **first-class I/O transport** using Hermes' **native
Discord platform plugin** (`plugins/platforms/discord`, discord.py 2.7.1). It is
not a custom agent, bridge, webhook worker, or second runtime:

```text
Discord ─┐
         ├─▶ Hermes Gateway ─▶ KORA ─▶ Hermes Agent ─┬─ Ollama (gpt-oss:20b-cloud)
Open WebUI┘                                           ├─ OpenCode Go (deepseek-v4-flash)
                                                      ├─ MCPs / skills / delegation
                                                      └─ docker-admin / qBittorrent tools
```

Discord enters the **same** gateway, session, tool, and governance path as Open
WebUI. KORA directives and Phases 1–3 boundaries are authoritative regardless of
transport. See `Architecture/decisions/ADR-0013-Discord-Native-Transport.md` and
`Documentation/Phase4/Discord_Transport.md`.

### Least-privilege toolset

`platform_toolsets.discord` (in `/opt/data/config.yaml`) is set to the **same
tool surface as `api_server`** and deliberately excludes the native `discord`
and `discord_admin` toolsets — Discord is transport, not a server-administration
surface:

```yaml
platform_toolsets:
  discord: [connections, file, kora, taskbridge, terminal, delegation]
```

### Configuration (variables by name; values live only in `.env`)

| Variable | Purpose |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Bot credential (secret; enables the platform when present). |
| `DISCORD_ALLOWED_USERS` | Explicit allowlist of Discord user IDs (default-deny when empty). |
| `DISCORD_ALLOWED_CHANNELS` | Optional explicit channel-ID allowlist. |
| `DISCORD_REQUIRE_MENTION` | `true` — server channels respond only when mentioned. |
| `DISCORD_HOME_CHANNEL` | Optional default channel for cron/notifications. |
| `DISCORD_ALLOW_ALL_USERS` | Must remain `false` (never enable open access). |

The behavioral block in `config.yaml` is conservative: `require_mention: true`,
`free_response_channels: ''`, `server_actions: ''` (no admin actions),
`reactions: true`, `auto_thread: true`, `max_attachment_bytes: 33554432`.

### Authorization and session mapping

* **Default deny.** With no allowlist and no allow-all, the adapter rejects all
  messages and logs a warning. Only explicit `DISCORD_ALLOWED_USERS` (and/or
  `DISCORD_ALLOWED_CHANNELS`) authorize access. No role-based bypass is enabled
  (`dm_role_auth_guild` empty).
* **Sessions** are native (`gateway/session.py`):
  `agent:main:discord:dm:<chat>:<user>`,
  `agent:main:discord:channel:<channel>:<user>` (per-user isolation because
  `group_sessions_per_user: true`),
  `agent:main:discord:thread:<channel>:<thread>`. The Open WebUI path uses the
  `api_server` platform namespace, so the two never collide.
* **No privileged transport.** A Discord message follows the exact same KORA
  governance, tool allowlist, and write-confirmation path as the equivalent Open
  WebUI request; `restart sonarr` behaves identically on both. Destructive
  operations remain unavailable.

### Native behavior inherited

* **Mention-gated server channels** (`require_mention`) with threads associated
  to their originating channel; DMs require authorization.
* **Long-running tasks:** the gateway acknowledges, keeps typing indicators /
  reactions while working, and delivers the final result; manual approvals use
  native Discord buttons. No custom task queue.
* **Message limits:** long replies are chunked at Discord's 2000-char limit
  (`MAX_MESSAGE_LENGTH`, split threshold 1900) with a chunk cap that replaces
  overflow with a notice rather than flooding the channel.
* **Attachments:** images/audio handled as media; documents (pdf/md/txt/log/
  json/yaml/zip/office/… ) cached under the size cap; small text-like files are
  inlined (≤100 KB), downloads are SSRF-guarded, and nothing is executed.
* **Networking:** outbound Discord Gateway/WebSocket (`discord.py`) only — no
  public webhook, no new inbound port, no Traefik route, no Docker TCP.

### Operate / troubleshooting

1. Create a private Discord application + bot, copy the bot token.
2. Put **only** the token + allowlist in `services/hermes/.env` (never in git):
   `DISCORD_BOT_TOKEN`, `DISCORD_ALLOWED_USERS`, optional
   `DISCORD_ALLOWED_CHANNELS`, `DISCORD_REQUIRE_MENTION=true`.
3. Invite the bot with the minimal permission set (View Channels, Send Messages,
   Read Message History, Embed Links, Attach Files, Send Messages in Threads,
   Add Reactions). **Enable the MESSAGE CONTENT INTENT** (Developer Portal →
   *Bot* → *Privileged Gateway Intents* → *MESSAGE CONTENT INTENT* → Save) —
   Hermes' native adapter requests it unconditionally, so without it Discord
   rejects the gateway `IDENTIFY` (close code 4014) and the bot stays offline.
4. Recreate Hermes: `docker compose -f services/hermes/compose.yaml up -d`.
5. Confirm: `docker exec hermes /opt/hermes/.venv/bin/hermes gateway status` and
   `docker logs hermes 2>&1 | grep -i discord`.
6. Test: DM the bot (authorized user), mention it in an allowed channel, verify
   a non-mentioned message is ignored, verify an unauthorized user is denied.

Troubleshooting: no platform start ⇒ `DISCORD_BOT_TOKEN` missing/empty; all
messages denied ⇒ allowlist empty; silence in server ⇒ not mentioned
(`require_mention`); `gateway status` + gateway logs under
`/opt/data/logs/gateways/default/` are the first stop.

**Bot offline with `PrivilegedIntentsRequired` / `discord_intents_required`**:
the **MESSAGE CONTENT INTENT** is not enabled in the Discord Developer Portal.
Hermes requests it unconditionally (`plugins/platforms/discord/adapter.py`,
`intents.message_content = True`), so Discord rejects the gateway `IDENTIFY`
(close code 4014), the adapter parks the platform (non-retryable), and the
gateway keeps serving `api_server` in a DEGRADED state. The intent toggle is
Developer-Portal-only (the API cannot set it: `PATCH /applications/@me` with the
flag returns 200 but leaves `flags=0`). Enable it in the portal, then
`docker restart hermes`. Verify the app flag with
`GET https://discord.com/api/v10/applications/@me` (`flags & (1<<18 | 1<<19)`
non-zero) and watch for a Discord `READY` (no `PrivilegedIntentsRequired`) in the
gateway log.

**Auto-thread creation fails ("Hermes could not create a Discord thread …")**:
with the default `DISCORD_COMMAND_SYNC_POLICY=safe`, Hermes temporarily sets
discord.py's `http.max_ratelimit_timeout=30` during the slash-command reconcile;
discord.py caches that on each rate-limit bucket when it is first created, so a
route bucket first used during the reconcile (thread creation) can raise
`RateLimited` pre-emptively for its whole window ("Too many requests. Retry in
Ns") even though Discord never rejected the request. Fix: use the bulk policy
(`DISCORD_COMMAND_SYNC_POLICY=bulk`, the compose default), which syncs in one
request without touching `max_ratelimit_timeout`. See
`Documentation/Phase4/Discord_Transport.md` §12.

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
