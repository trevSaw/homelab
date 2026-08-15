# KORA Workspace / OpenCode-Style Development Capability

**Status:** Foundation (Phase 17.x) — controlled development/workspace layer.
**Scope:** KORA can read the homelab repo and draft content in its writable
workspace; it does **not** yet have deployment authority, Docker access, or
repo write.

## Architecture

```text
Open WebUI → Hermes (runs as uid 10000 'hermes') → KORA HEAD AGENT
   ├── file toolset        (read anywhere; write scoped to /opt/data)
   ├── jDocMunch           (governance + docs retrieval)
   ├── Context7 / Graphify (read-only retrieval)
   ├── Honcho / Chroma     (memory / knowledge)
   └── repo mount          (read-only in practice; see boundaries)
```

## Filesystem boundaries

| Host path | Container path | Mode | Purpose |
| --- | --- | --- | --- |
| `/mnt/monarch/appdata/hermes` | `/opt/data` | rw | Hermes/KORA home + writable workspace |
| `/home/fatherfrank/projects/homelab` | `/opt/data/homelab-repo` | rw (mount) | Canonical homelab repo |
| `/home/fatherfrank/projects/homelab/Architecture/standards` | `/opt/data/homelab-governance` | ro | Governance standards |
| `/home/fatherfrank/projects/homelab/Documentation` | `/opt/data/homelab-docs` | ro | Knowledge/docs corpus |
| `/home/fatherfrank/projects/homelab/Architecture/ai/Council` | `/opt/data/council` | ro | Council content (Phase 15, paused) |

**Effective access:** the Hermes runtime runs as uid **10000 (`hermes`)**. The
repo mount is owned by uid 1000 (`fatherfrank`), so KORA can **read** the repo
but **cannot write it** (safe by design — least privilege). KORA writes are
limited to `/opt/data` (its home) by `HERMES_WRITE_SAFE_ROOT` + the file tool's
write deny-list. No `docker.sock`, no host paths outside the mounts.

## Enabled Hermes toolsets (api_server)

- `kora` — KORA plugin (governance, chroma query, ollama list, memory boundary;
  `wipe_volume` denied).
- `file` — `read_file`, `write_file`, `patch`, `search_files` (narrow, scoped
  writes). **No delete tool** in this toolset.
- MCP (read-only): `graphify` (7), `context7` (2), `jdocmunch` (7 + governance
  repo).

**Not enabled:** `terminal`, `code_execution` (would be root/host-capable in a
root container — excluded per Phase 17.x security rules). `delegation` (Phase
15, paused).

## Governance retrieval path

- `Architecture/standards/` mounted read-only at `/opt/data/homelab-governance`
  and indexed into jDocMunch as repo **`local/homelab-governance`** (13 files,
  303 sections).
- KORA is directed (GOVERNANCE_RETRIEVAL_DIRECTIVE in the kora plugin) to
  consult it before deployment/proposal work via
  `mcp_jdocmunch_search_sections` / `get_section` (repo
  `local/homelab-governance`).
- Verified: "Docker deployment standards" → Service Lifecycle Standard /
  HomelabArchitectureStandard; governance standards retrievable.

## Git access

- **Read:** `git` read operations are NOT currently executable by KORA (no
  shell toolset; the `file` toolset has no git tool). Repo content is readable
  via `file`/`search_files`.
- **Write:** no git write/commit capability (no shell; repo mount not writable
  by uid 10000).
- GitHub: no MCP (no PAT). Outbound HTTPS works.

## Command execution boundaries

- KORA has **no shell/terminal/code-execution toolset** in this phase.
- `docker compose config` validation is **not** available (no Compose plugin in
  the Hermes container; no docker.sock).
- HTTP verification: no web/search toolset enabled.

## Security boundaries

1. **What KORA can read:** repo (read-only in practice), `/opt/data`, governance
   (ro), docs (ro), council (ro).
2. **What KORA can write:** `/opt/data` only (write-safe-root scoped; deny-list
   for sensitive files).
3. **Commands:** none executed (no shell toolset).
4. **Docker:** none (no socket, no MCP).
5. **Host root filesystem:** no access (container-isolated; only intended
   mounts).
6. **SSH keys / credentials:** not exposed via new mounts beyond the repo itself
   (repo `.env` files are readable through the repo mount — flagged; no host
   credential files).
7. **Cloudflare creds:** not directly exposed (would only be within repo
   `.env`, same as #6).
8. **Traefik / DNS:** no access (no docker, no config mount).
9. **Deployment:** none.
10. **Requires approval:** any consequential action (there are none available
    yet); Hermes `approvals.mode=manual` retained.

## What KORA can do now

- Read the canonical homelab repo (`/opt/data/homelab-repo`), inspect service
  compose files.
- Search/read files in `/opt/data` (draft workspace).
- Retrieve governance standards and project docs via jDocMunch.
- Produce deployment plans/reasoning (LLM).

## What KORA cannot do yet

- Write/modify the homelab repo (uid mismatch — safe by design).
- Run shell/git/docker/compose commands.
- Deploy, restart, stop, or modify running services.
- Verify HTTP endpoints or read container logs.

## Planned future deployment capability

Separate, explicitly designed phase: decide repo-write path (host group/ownership
change or a hermes-owned staging dir), a scoped execution/validation tool, Docker
access (read-only first), and a deployment approval gate — all gated by the
existing manual-approval model.
