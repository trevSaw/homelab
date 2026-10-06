---
title: ADR-0016 KORA Canonical Documentation Access
document_type: ADR
service: hermes
owner: Homelab
status: Accepted
version: 1.1.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - Architecture/decisions/ADR-0015-KORA-Web-Research-SearXNG.md
  - services/hermes/README.md
  - Documentation/Phase6/KORA_Documentation_Access.md
---

# ADR-0016 — KORA Canonical Documentation Access (narrowed)

## Status

**Accepted** (Phase 6, 2026-10-06). Supersedes the initial draft that mounted the
whole canonical repository read/write.

## Context

Hermes/KORA could only edit a stale sanitized clone (`/opt/data/homelab-workspace`,
HEAD `afbbeea phase18`) and had read-only mounts of `Documentation/`,
`Architecture/standards/`, `Architecture/ai/Council/`. A read-only security audit
found that a repo-wide RW mount + recursive agent ACL was too broad: it exposed
private session transcripts, compose/config, `.git`, and a gitignored Hermes-home
copy (`Documentation/Phase14/.../staging/data`) to the agent, and it relied on
repo-wide ACLs. The audit also found that several KORA-owned secrets were present
in the agent's **process environment** and were **not** removed by Hermes' terminal
scrub (`KORA_QBIT_USER/PASS`, `KORA_DOCKER_ADMIN_TOKEN`,
`HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`).

## Decision

1. **Documentation-only RW scope.** Only these canonical paths are mounted
   read/write, at their host paths:
   `Documentation/`, `Architecture/decisions/`, `Validation/`, `Services/`.
   `HERMES_WRITE_SAFE_ROOT=/opt/data:<those four paths>`. The rest of the
   canonical repo is **not mounted** (inaccessible to the agent) — no repo-wide
   mount, no `.git`, no compose/config, no session transcripts.
2. **Secret protection.** `.env*` files remain mode `600` owner fatherfrank
   (uid 1000) with no agent ACL; they are also on Hermes' built-in read deny-list.
   The WireGuard `.zip` is `600`.
3. **Write grant without root.** Host ACL `u:10000:rwX` applied **only** to the
   four documentation paths (owner-applied). `group_add` is ineffective (the s6
   image drops to gid 10000 only), and running as uid 1000 would read the `600`
   `.env` files. No container runs as root for this.
4. **Process-environment secret exposure remediation.** The KORA plugin registers
   a never-selected terminal-environment provider (`name=kora-strip`) solely to
   contribute `strip_env_keys`, so `KORA_QBIT_USER/PASS`,
   `KORA_DOCKER_ADMIN_TOKEN` and `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` are
   removed from every agent-spawned subprocess (terminal / execute_code) while the
   plugin process keeps them in `os.environ`.
5. **Obsidian vault: deferred, not mounted.** The audit found **no server-side
   vault** anywhere on the host; Obsidian Self-hosted LiveSync materializes the
   vault **on the user's devices**, with **CouchDB as the authoritative sync
   backend** (`services/couchdb`, `sync.fatherfankscloud.uk`). KORA/Hermes have no
   CouchDB access by design. No vault path is mounted or granted until a vault
   actually exists on the host and an ADR defines the LiveSync↔filesystem
   relationship. This keeps the user's current (client-side) vault untouched.
6. **Docker administration unchanged** — no socket in Hermes; `docker-admin`
   remains the only Docker boundary.
7. The stale `/opt/data/homelab-workspace` clone is **kept** and marked
   deprecated until the new architecture is validated; `/opt/data/homelab-repo`
   remains an empty placeholder.

## Alternatives considered

| Option | Outcome |
| --- | --- |
| Whole-repo RW mount + repo-wide ACL (initial draft) | **Rejected** — over-broad; exposed private/undesired content and `.git`. |
| **Documentation-path RW only + targeted ACL + terminal env scrub** | **Adopted.** Satisfies documentation maintenance with the least surface. |
| Run Hermes as host uid 1000 | Rejected — could read `600` `.env` files. |
| Register a fake terminal backend for env scrubbing | Adopted only as the documented `strip_env_keys` extension point (backend never selected). |
| Mount the vault inside the repo now | Rejected — no server-side vault exists; would invent structure and fight CouchDB LiveSync. |

## Consequences

**Positive:** Hermes maintains docs/ADRs/validation/service-index directly in the
canonical repo; the broad ACL and process-env leaks are removed; the vault and
CouchDB boundary are respected.

**Negative / risks:** the agent cannot read the rest of the repo (compose/config)
— live Docker tooling covers runtime state. Files the agent creates in the doc
paths are owned uid 10000 (human may need `chown` to edit). No default ACLs were
set, so new human-created files need the ACL re-applied to be agent-writable.
`.env` files must stay `600` with no agent ACL.

## Security

No Docker socket; Docker admin only via `docker-admin`; agent filesystem scope
limited to four documentation paths; `.env`/keys unreadable by the agent (perms +
read deny-list); KORA_* secrets scrubbed from agent subprocesses; no push
credentials; CouchDB untouched.
