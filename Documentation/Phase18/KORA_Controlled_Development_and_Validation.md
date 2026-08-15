# KORA — Controlled Development & Validation (Phase 18)

**Status:** Implemented (2026-08-15). Controlled development + validation layer.
**Scope:** KORA can inspect, edit a workspace, run safe commands, validate Compose,
and verify HTTP — **without deployment authority**. Phase 19 will add controlled
deployment.

## Architecture

```text
Open WebUI → Hermes (runs as uid 10000 'hermes') → KORA HEAD AGENT
   ├── file toolset     (read/write/patch/search; writes scoped to /opt/data)
   ├── terminal toolset (shell as uid 10000; non-root, container-scoped)
   ├── workspace clone  (/opt/data/homelab-workspace — hermes-owned git working copy)
   ├── jDocMunch        (governance + docs retrieval)
   ├── Context7/Graphify (read-only retrieval)
   ├── docker-compose   (/opt/data/bin/docker-compose — daemon-independent config validation)
   └── curl (via terminal) for HTTP verification
```

## Toolsets (api_server = `kora`, `file`, `terminal`)

- `kora` — plugin (governance/refusal; `wipe_volume` denied).
- `file` — `read_file`, `write_file`, `patch`, `search_files` (writes scoped by
  `HERMES_WRITE_SAFE_ROOT=/opt/data` + write deny-list).
- `terminal` — shell execution **as uid 10000 (`hermes`)** — NOT root. Container
  isolated; can only write what uid 10000 can write (`/opt/data/**`). Cannot
  write `/etc`, host paths, or the canonical repo (uid-1000-owned).
- MCP (read-only): `graphify` (7), `context7` (2), `jdocmunch` (7 + governance).

## Workspace architecture

| Path | Owner | Mode | Purpose |
| --- | --- | --- | --- |
| `/opt/data/homelab-workspace` | uid 10000 (hermes) | rw | **KORA writable git working copy** (draft/edit/commit here) — clean shallow clone, no `.env`, no secret-bearing history |
| `/opt/data` | uid 10000 | rw | KORA home + safe-root |
| `/opt/data/homelab-governance` | uid 1000 | ro | Governance standards (Architecture/standards) |
| `/opt/data/homelab-docs` / `council` | uid 1000 | ro | Docs / Council (Phase 15, paused) |
| `/opt/data/docker-state` | uid 1000 (host) | ro | Read-only Docker state snapshots (host-generated; no docker.sock in any container) |

**NOTE (Phase 18.1 .env remediation):** the canonical homelab repo is **no longer
bind-mounted** into Hermes — it contained gitignored `.env` secrets (22 files)
that were readable. KORA's repo surface is the clean shallow workspace clone
(`/opt/data/homelab-workspace`), which excludes `.env` and secret-bearing git
history. The canonical repo (`/home/fatherfrank/projects/homelab`) remains
authoritative and is only touched via the approval-gated `scripts/kora-apply.sh`
bridge.

## Read-only infrastructure inspection (Phase 18.1)

No `docker.sock` is exposed to any container (host-escape risk). Instead, a
**host-side snapshot script** (`/home/fatherfrank/projects/docker-state/snapshot.sh`,
tracked as `scripts/docker-state-snapshot.sh`) writes read-only Docker state to
`/opt/data/docker-state` (mounted ro): `ps.txt`, `inspect.txt` (container
state/health/image/restart/networks), `networks.txt`. KORA reads these to
inspect container state — no socket, no write operations. Refresh: run the host
script (cron or manual).

## Canonical-repo apply (Phase 18.1, approval-gated)

KORA drafts + commits in the workspace clone. To move changes to the canonical
repo, KORA generates a patch (`git -C /opt/data/homelab-workspace diff >
kora.patch`), and a human runs `scripts/kora-apply.sh` which:
1. Previews the diff (`git apply --stat` + full content), rejects corrupt patches.
2. **Requires explicit `y/N` approval** before applying.
3. Applies to `/home/fatherfrank/projects/homelab` (`git apply`), optionally
   `--commit`. KORA itself never writes the canonical repo and has no push/remote.

## Git capabilities

- **Read (workspace clone):** `git status`, `git log`, `git diff`, `git show`,
  `git branch`, `git remote`, `git ls-files`. Also read-only on the canonical
  repo mount (read works; write denied by uid mismatch).
- **Write (workspace clone):** `git add`, `git commit` (KORA identity
  `kora@homelab.local`); file create/edit/delete within the workspace.
- **Push: NOT available** (no credentials configured).
- **GitHub:** no PAT; public-repo clone/`git ls-remote` work via outbound HTTPS.

## Command execution boundaries (terminal, as hermes uid 10000)

- Allowed: `pwd`, `ls`, `find`, `grep`/`rg`, `cat`, `sed`, `awk`, `mkdir`,
  `cp`, `mv`, `rm` (within hermes-writable paths), `git`, `curl`,
  `/opt/data/bin/docker-compose config` (validation only).
- Denied by uid/permissions: writes to `/etc`, `/var`, `/root`, host paths,
  the canonical repo, and anything not owned by uid 10000. `docker.sock` absent.
- No `docker` daemon commands (CLI present but no socket; `docker-compose`
  `config` is offline validation only).

## Compose validation

- `/opt/data/bin/docker-compose config -q` — daemon-independent structural
  validation, runnable by hermes. Verified (`COMPOSE-CONFIG-VALIDATION-OK`).
- No `docker compose up`, no daemon contact, no docker.sock.

## Docker inspection (read-only)

- **Available via host snapshots** (`/opt/data/docker-state`: ps/inspect/
  networks) — read-only, no docker.sock in any container. See "Read-only
  infrastructure inspection" above.
- **Not available:** live `docker` CLI/daemon access, `docker compose up`, any
  write/exec/restart/remove operations. Those require the socket or host-side
  action and are Phase 19 / approval-gated.

## HTTP verification

- `curl` (via terminal, as hermes) for GET/HEAD/status/redirects/TLS failures
  against internal endpoints. Verified (HTTP status returned). Not a browser.

## Governance retrieval

- `Architecture/standards/` → `/opt/data/homelab-governance` (ro) → indexed in
  jDocMunch as `local/homelab-governance`. KORA directed to consult it before
  deployment/proposal work. Verified retrievable (Docker/Compose/naming/etc.).

## Approval model

- `approvals.mode = manual` preserved.
- Hierarchy: read/analyze/search/edit(workspace)/validate/diff/docker-inspection/
  http = automatic. git commit = within workspace (KORA-owned clone). git push,
  deploy, start/stop/restart/remove, Traefik write, DNS write, Cloudflare write,
  destructive ops = **NOT AVAILABLE**.

## Security boundaries

1. **Read:** repo (ro), workspace, `/opt/data`, governance/docs/council (ro).
2. **Write:** workspace clone + `/opt/data` only (uid 10000). Canonical repo
   write = denied by uid mismatch (safe by design).
3. **Commands:** terminal as uid 10000 (non-root). `/etc`/host write denied.
4. **Docker:** no socket, no daemon access.
5. **Host root FS:** no access (only intended mounts).
6. **Secrets:** **remediated (Phase 18.1)** — the canonical repo bind mount was
   removed (it exposed 22 gitignored `.env` files). KORA's repo surface is the
   clean workspace clone (no `.env`, shallow history). No host credential files
   mounted; no `.env` reachable.
7. **Cloudflare/Pi-hole/Traefik creds:** not mounted; Traefik config readable
   via the repo mount (read-only); no write.
8. **Deployment:** none.

## Intentionally NOT available (Phase 19)

- docker.sock / Docker daemon / deployment / start-stop-restart / remove
- Traefik writes · DNS writes · Cloudflare writes
- Git push / GitHub PAT
- Unrestricted shell (terminal is uid 10000, scoped) / host root

## Tests (Phase 18)

- File: read/create/modify/delete in workspace ✅; read repo compose ✅.
- Terminal: `id` → uid 10000 (hermes) ✅; safe commands execute ✅.
- Git: status/log/branch in workspace ✅.
- Compose: `docker-compose config -q` valid ✅ (daemon-independent).
- HTTP: curl status ✅.
- Boundary: `/etc` write denied ✅; host path inaccessible ✅; docker.sock absent ✅.
- Governance: jDocMunch retrieval ✅.
- SparkyFitness dry run: see below.

## Phase 19 prerequisites

1. Read-only Docker inspection (scoped mechanism, not raw docker.sock if
   possible).
2. Canonical-repo write/apply mechanism (or retain workspace-clone + human
   apply).
3. Controlled deployment gate (approval-gated `docker compose up`, health
   verify).
4. Traefik/DNS read+write (approval-gated) if required.
