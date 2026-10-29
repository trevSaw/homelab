---
title: CouchDB Service README
document_type: README
service: couchdb
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-08-18
related_documents:
  - Documentation/services/couchdb/couchdb.md
---

# CouchDB (Obsidian Self-hosted LiveSync)

Infrastructure database service backing **Obsidian Self-hosted LiveSync**.
Obsidian Desktop/Mobile clients reach CouchDB **only** through Traefik HTTPS at
`sync.fatherfankscloud.uk`. CouchDB itself is not exposed to the LAN; port 5984
is published loopback-only for provisioning and administration.

## Purpose

Provides the real-time document database for Obsidian Self-hosted LiveSync note
synchronisation across the user's devices. This is an **infrastructure service**,
independent of the AI/KORA stack.

## Architecture

```text
Obsidian Desktop / Mobile
        │  HTTPS (Traefik, wildcard LE cert)
        ▼
sync.fatherfankscloud.uk ──► CouchDB (container "couchdb")
                                  │
                       /mnt/monarch/appdata/couchdb/{data,etc}
```

- CouchDB joins the external `proxy` network; Traefik routes
  `sync.fatherfankscloud.uk` → container port 5984.
- CORS is handled **natively by CouchDB** (`config/10-livesync.ini`); there is no
  Traefik CORS middleware.
- **KORA/Hermes/MCP/Open WebUI has no access to this database.** No credentials,
  MCP tools, or configuration are shared with the AI stack as part of this service.

## Dependencies

- Traefik on the external `proxy` network (wildcard ACME cert via Cloudflare DNS-01).
- DNS: `sync.fatherfankscloud.uk` CNAME → `mocha.fatherfankscloud.uk` in Technitium
  (canonical and active DNS provider; maintained via
  `scripts/migration/setup-technitium.sh`).

## Networks

| Network | Reason |
|---------|--------|
| proxy | Traefik ingress (the only remote path to CouchDB) |

## Storage

| Mount | Path inside container | Description |
|------|----------------------|-------------|
| `/mnt/monarch/appdata/couchdb/data` | `/opt/couchdb/data` | Persistent database files |
| `/mnt/monarch/appdata/couchdb/etc` | `/opt/couchdb/etc/local.d` | Runtime CouchDB config (local.d) |
| `services/couchdb/config/10-livesync.ini` | `/opt/couchdb/etc/local.d/10-livesync.ini` (ro) | CORS config (versioned) |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TZ` | Yes | Timezone (Asia/Tokyo) |
| `COUCHDB_USER` | Yes | CouchDB admin — **infrastructure only, never used by Obsidian** |
| `COUCHDB_PASSWORD` | Yes | Admin password (generated, gitignored) |
| `COUCHDB_DB` | Yes | LiveSync database name (`obsidian`) |
| `SYNC_USER` | Yes | Client/service account (`obsidian-sync`) |
| `SYNC_PASSWORD` | Yes | Sync account password (generated, gitignored) |

## Deployment

```bash
cd services/couchdb
cp .env.example .env          # fill COUCHDB_USER/PASSWORD, SYNC_USER/PASSWORD
mkdir -p /mnt/monarch/appdata/couchdb/{data,etc}
chown -R 1000:1000 /mnt/monarch/appdata/couchdb
docker compose -f compose.yaml config >/dev/null
docker compose -f compose.yaml up -d
bash scripts/provision.sh     # operator-initiated, idempotent
```

**Container user note:** CouchDB runs as `1000:1000` (PUID/PGID 1000, matching the
homelab convention). The official image's own user is uid `5984`, but running as
`1000` is the Self-hosted LiveSync author's reference configuration and keeps the
appdata directories owned by `fatherfrank`.

## Authentication Model

| Account | Role | Used by |
|---|---|---|
| `COUCHDB_USER` | Server admin | Infrastructure administration + provisioning only |
| `SYNC_USER` (`obsidian-sync`) | Member on `COUCHDB_DB` only | Obsidian Self-hosted LiveSync clients |

Obsidian clients **must never** use the admin account. `obsidian-sync` receives
only member permissions on the `obsidian` database (see `scripts/provision.sh`).

## Provisioning

Run `bash services/couchdb/scripts/provision.sh` (idempotent). It verifies CouchDB
is healthy before writing, then creates/verifies the database, the sync user, and
database security permissions. It never runs at container startup and grants no
privileges implicitly.

## Validation

```bash
docker compose -f compose.yaml config
docker compose -f compose.yaml ps            # health: healthy
ss -tlnp | grep 5984                          # expect 127.0.0.1:5984 only (loopback)
curl -sk https://sync.fatherfankscloud.uk/    # CouchDB Welcome JSON (via Traefik)
# CORS preflight, least-privilege, restart, and DNS checks: see
# Documentation/services/couchdb/couchdb.md
```

## Backups

- **Filesystem-level protection:** persistent CouchDB data lives under
  `/mnt/monarch/appdata/couchdb` on the SSD tier, which is covered by the existing
  `/monarch` backup/snapshot strategy (see Homelab Architecture Standard →
  Backup Standards). This protects the files on disk.
- **CouchDB-consistent backups:** a consistent database dump/replication mechanism
  (e.g. CouchDB `_replicate`/couchbackup) is **not yet implemented** and is tracked
  as a follow-up. The filesystem copy/snapshot is **not** a CouchDB-consistent
  database backup and must not be treated as one until implemented and tested.
- **File-level restore procedure:** stop the stack, copy the last snapshot back
  (`rsync -aH --delete` from `/hive/backups/couchdb/appdata-<STAMP>/` to
  `/mnt/monarch/appdata/couchdb/`), then `docker compose up -d`. Chown restored
  files to `1000:1000`.

## Restore

See Backups above.

## Upgrade Procedure

1. Bump the image tag in `compose.yaml` and record in `Versions.md`.
2. `docker compose -f compose.yaml pull && docker compose -f compose.yaml up -d`.
3. Verify healthcheck + HTTPS + CORS preflight (see Validation).

## Monitoring

- Container healthcheck (TCP probe to `127.0.0.1:5984`).
- Central logging via `com.homelab.logging=central`.

## Troubleshooting

- `docker logs couchdb` — server logs (10m/5 rotation).
- `curl -fsS http://127.0.0.1:5984/_up` — liveness from the host.
- CORS issues: confirm the client Origin is one of the allowed origins in
  `config/10-livesync.ini` and that `[chttpd] enable_cors = true` is present
  (both are required); if the LiveSync client uses custom headers in
  "database connection advanced settings", extend the `headers` list there.
- Fauxton admin UI: `ssh -L 5984:127.0.0.1:5984 mocha` then browse
  `http://127.0.0.1:5984/_utils`.

## Known Exceptions

| Item | Exception |
| --- | --- |
| Container user | Non-root `1000:1000` (PUID/PGID convention) | — |
| Port publish | `127.0.0.1:5984` loopback-only for provisioning/admin; no LAN exposure |

## Lifecycle Status

Production (deployed 2026-08-18).

## Compliance Score

90 — see `Documentation/services/couchdb/couchdb.md` for the runtime validation matrix.

## Architecture Review

This service is deliberately isolated from the AI stack. Any future
KORA/Obsidian knowledge integration requires a separate architecture decision and
phase; it will not be coupled to this deployment.

## Version History

| Date | Version | Change Summary | Author |
|------|---------|----------------|--------|
| 2026-08-18 | 1.0.0 | Initial deployment (CouchDB 3.5.2.1, Obsidian LiveSync) | Homelab Administrator |
