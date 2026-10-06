# KORA Documentation Access (Phase 6)

**Status:** Implemented (2026-10-06). ADR: `ADR-0016`.

Hermes/KORA can read and write the homelab **documentation** directly, with a
narrow scope, no Docker socket, and no process-environment secret leakage.

## Scope (read/write)

Only these canonical paths are mounted read/write at their host paths:

| Path (host) | Purpose |
| --- | --- |
| `/home/fatherfrank/projects/homelab/Documentation` | service/ops docs, Phase reports |
| `/home/fatherfrank/projects/homelab/Architecture/decisions` | ADRs |
| `/home/fatherfrank/projects/homelab/Validation` | validation records |
| `/home/fatherfrank/projects/homelab/Services` | service index/catalog |

`HERMES_WRITE_SAFE_ROOT=/opt/data:<the four paths above>`.

**Not mounted (inaccessible to the agent):** the rest of the canonical repo
(`services/`, `AI/`, `Assets/`, `Indexes/`, root session transcripts, `.git`,
config files). The Obsidian vault is not mounted.

## Secret protection

- `.env*` files: mode `600` owner `fatherfrank` (uid 1000), **no agent ACL**;
  also on Hermes' built-in read deny-list. `services/Hotio/...wireguard...zip`
  hardened to `600`.
- **Process-environment scrub:** the KORA plugin registers a never-selected
  terminal-environment provider (`kora-strip`) whose `strip_env_keys` removes
  `KORA_QBIT_USER`, `KORA_QBIT_PASS`, `KORA_DOCKER_ADMIN_TOKEN` and
  `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` from every agent-spawned subprocess.
  (Hermes already strips `API_SERVER_KEY`, `DISCORD_BOT_TOKEN`,
  `OPENCODE_GO_API_KEY`.) The gateway/plugin process still sees them, so tools work.

## Write grant (no root)

Host ACL `u:10000:rwX` applied only to the four documentation paths (owner
applied). `group_add` does not reach the agent (s6 drops to gid 10000 only), and
running as uid 1000 would let the agent read the `600` `.env` files.

## Git / Docker

- No `git` write scope beyond the doc paths (`.git` not mounted). Local commits by
  Hermes are not supported in this narrow design; the operator commits.
- No Docker socket; administration remains via `docker-admin`.

## Obsidian vault — deferred (not mounted)

Audit result: **no server-side Obsidian vault exists on this host** (no
`.obsidian` directory anywhere under `/home/fatherfrank`, `/mnt/monarch`, `/hive`,
`/srv`, `/opt`, `/data`). Obsidian Self-hosted LiveSync keeps the vault on the
user's devices; **CouchDB** (`services/couchdb`, `sync.fatherfankscloud.uk`) is
the authoritative sync backend, and KORA/Hermes have no CouchDB access by design.

Architecture to establish **before** granting vault access: a vault must be
materialized on the host (e.g. by a dedicated LiveSync client), and an ADR must
define how Hermes edits relate to CouchDB LiveSync (CouchDB authoritative;
filesystem is a materialization). Until then, no vault path is mounted, and the
user's current vault is untouched.

## Deprecated

`/opt/data/homelab-workspace` (stale clone) — kept, no longer authoritative.
`/opt/data/homelab-repo` — empty placeholder.

## Validation

See the Phase 6 report/validation output: doc read/write, no repo-root access,
`.env` blocked, terminal env scrub, docker-admin/qBittorrent/SearXNG/Open WebUI
regressions, `git diff --check`.
