# couchdb

## Overview
- Purpose: Infrastructure database backend for Obsidian Self-hosted LiveSync note synchronisation
- Category: Infrastructure / Databases
- Current lifecycle state: Production (deployed 2026-08-18)
- Importance level: High

## Repository Location
- Service directory: `services/couchdb/`
- Compose file: `services/couchdb/compose.yaml`
- Documentation path: `Documentation/services/couchdb/couchdb.md`

## Runtime Information
- Container names: couchdb
- Restart policy: unless-stopped
- Environment files: `.env` (gitignored, secrets), `.env.example` (template, placeholders only)
- Networks: `proxy` (external) — Traefik is the only remote path into CouchDB
- Volumes: `/mnt/monarch/appdata/couchdb/{data,etc}` (bind mounts, canonical appdata)
- Container user: `1000:1000` (PUID/PGID convention; LiveSync reference config)

## IP / Ports
| Port | Host bind | Purpose |
|---|---|---|
| `5984/tcp` | `127.0.0.1` only | Provisioning / admin (Fauxton via SSH tunnel). **Not on LAN.** |
| `443/tcp` | via Traefik | `sync.fatherfankscloud.uk` (HTTPS, wildcard LE cert) |

CouchDB exposes no port to the LAN. Remote access exists solely through the
Traefik HTTPS route.

## Architecture
```text
Obsidian Desktop / Mobile
        │  HTTPS
        ▼
sync.fatherfankscloud.uk (Traefik router, certresolver "le")
        ▼
couchdb (proxy network, port 5984)
        ▼
/mnt/monarch/appdata/couchdb/{data,etc}
```

- CORS handled natively by CouchDB via `services/couchdb/config/10-livesync.ini`
  (origins `app://obsidian.md`, `capacitor://localhost`, `http://localhost`).
- No Traefik CORS middleware is used.
- Obsidian clients connect with the `obsidian-sync` account (member on the
  `obsidian` database only).

## Architecture Relationships
- Upstream dependencies: Traefik (proxy network); DNS resolution for
  `sync.fatherfankscloud.uk` (Technitium, canonical and active DNS provider).
- Downstream consumers: Obsidian Desktop and Mobile via the LiveSync plugin.
- Reverse proxy relationships: Traefik is the sole ingress; CouchDB does not publish
  any LAN port.
- **Not related to:** KORA/Hermes/MCP/Open WebUI. The AI stack has no access to this
  database and no credentials are shared. Any future KORA/Obsidian integration is a
  separate architectural decision.

## Security Review
- Secret handling approach: admin and sync passwords in gitignored `.env`; `.env.example`
  has placeholders only; no credentials in git.
- Least privilege: `obsidian-sync` is a member of the `obsidian` database with empty
  roles; it cannot read `/_users` or administer the database.
- Privileged mode status: not used.
- Docker socket exposure: none.
- External exposure: none directly; HTTPS via Traefik only. Port 5984 is loopback-only.
- Known risks: CORS origin list must match the LiveSync client origins; if clients add
  custom headers in advanced connection settings, the `headers` list in
  `config/10-livesync.ini` must be extended.

## Operational Notes
- Backup considerations:
  - **Filesystem-level:** `/mnt/monarch/appdata/couchdb` sits on the SSD tier and is
    covered by the existing `/monarch` backup/snapshot strategy. This protects the
    files on disk.
  - **CouchDB-consistent:** a consistent database dump/`_replicate` mechanism is
    **not yet implemented** — tracked as a follow-up. The filesystem copy/snapshot is
    not a CouchDB-consistent backup.
- Recovery notes: stop stack → restore appdata from snapshot (`rsync -aH --delete`
  from `/hive/backups/couchdb/appdata-<STAMP>/`) → chown `1000:1000` →
  `docker compose up -d` → re-run `scripts/provision.sh` (idempotent).
- Monitoring requirements: container healthcheck (TCP :5984); central logging.
- Maintenance considerations: pinned `3.5.2.1` (see `Versions.md`); upgrade = bump tag
  + `docker compose up -d` + re-validate.

## DNS
- Canonical and active: `sync.fatherfankscloud.uk` CNAME → `mocha.fatherfankscloud.uk` in
  Technitium (maintained via `scripts/migration/setup-technitium.sh`).
- Dependency (Phase 19, not CouchDB-specific): Tailscale split-DNS for
  `fatherfankscloud.uk` must be configured in the Tailscale admin console
  (restricted nameserver → `100.102.139.115`) for Tailscale-only clients to resolve
  homelab hostnames. No CouchDB-specific workaround is applied.

## Governance Metadata
- ADR references: []
- Migration priority: P3
- Migration wave: Phase 20 (independent infrastructure deployment)

### Evidence References

Classification:
- Source: Apache CouchDB 3.5.2.1 official Docker image; Self-hosted LiveSync plugin docs.

Runtime:
- Deployed 2026-08-18; validation matrix below.

Dependencies:
- Source: Phase 19 audit (Technitium DNS, Traefik wildcard cert); Pi-hole retired after the DNS cutover.

Risks:
- Tailscale split-DNS (Phase 19) pending admin-console action.

Migration:
- Initial deployment; DNS record added to `setup-technitium.sh` CNAME list.

ADRs:
- None. Future KORA/Obsidian knowledge integration requires a new ADR/phase.

## Validation Matrix (2026-08-18)

| Check | Expected | Result |
|---|---|---|
| `docker compose config` | valid | PASS |
| Container start + healthcheck | running, healthy | PASS |
| Port 5984 loopback-only | `ss` shows `127.0.0.1:5984` only | PASS |
| Traefik HTTPS `sync.fatherfankscloud.uk` | CouchDB Welcome JSON, LE wildcard cert | PASS |
| CORS preflight (all 3 origins) | single echoed ACAO, credentials, methods/headers, max-age | PASS |
| Database `obsidian` exists | 200 on `GET /obsidian` (admin) | PASS |
| `obsidian-sync` exists | `_users/org.couchdb.user:obsidian-sync`, empty roles | PASS |
| `_security` | members=`[obsidian-sync]`, admins empty | PASS |
| Least privilege | `obsidian-sync` 403 on `/_users`; cannot create DBs | PASS |
| Restart resilience | restart → healthy → data persists → HTTPS OK | PASS |
| DNS (Technitium) | `sync.fatherfankscloud.uk` → `192.168.50.44` (LAN) / `100.102.139.115` (Tailscale source) | PASS |

## Known Issues
- Tailscale split-DNS (Phase 19) pending admin-console action; affects all
  `fatherfankscloud.uk` hostnames, not CouchDB specifically.
- CouchDB-consistent backup/dump mechanism is a documented follow-up (not yet
  implemented).
- CouchDB CORS requires both `[cors]` **and** `[chttpd] enable_cors = true`; the
  `enable_cors` flag is included in `config/10-livesync.ini` (missing it results in
  no CORS headers — verified during deployment).
