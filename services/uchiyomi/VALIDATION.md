# Uchiyomi — deployment validation record

Date: 2026-10-07 · Host: mocha · Operator: opencode (canonical repo session)

## Deployed version

| Component | Reference |
|---|---|
| Uchiyomi app | `ghcr.io/angelosha/uchiyomi@sha256:a3b5ccc3…7128ea` = upstream **v0.55.6** (2026-10-06) |
| FlareSolverr | `ghcr.io/flaresolverr/flaresolverr:v3.5.2@sha256:c80ae007…23767` |
| Suwayomi engine | `ghcr.io/suwayomi/suwayomi-server:v2.3.2243@sha256:e59f212c…751b` |

## Result summary

| Check | Result |
|---|---|
| `docker compose config -q` | PASS |
| All 3 containers healthy (app `/livez`, solver root, engine socket 200/401) | PASS |
| Embedded Postgres 16 init + migrations on first boot | PASS |
| Traefik router `uchiyomi.fatherfankscloud.uk` → HTTP 200 over TLS (Let's Encrypt, SAN `*.fatherfankscloud.uk`) | PASS |
| Technitium CNAME `uchiyomi.fatherfankscloud.uk → mocha.fatherfankscloud.uk` | PASS |
| `/healthz` (DB `SELECT 1`) | PASS |
| MangaDex source listed, `status: ok` | PASS |
| Source probe (`POST /api/admin/sources/mangadex/test`): search 12 results, covers 12/12, series page, chapters, pages | PASS |
| Suwayomi engine reachable (`v2.3.2243`, cap 25), solver wiring `ok` | PASS |
| `/library` bind mount writable by app uid 1000 | PASS |
| `/library-dl` bind mount writable, host file observed, cleaned up | PASS |
| Library scan recognises a CBZ placed on disk (series/book/pages) | PASS (see note) |
| Reader page listing served (`/api/books/:id/pages`) | PASS (see note) |
| Atomic library rescan (`POST /api/admin/library/scan`) | PASS |
| Existing Kavita/Prowlarr/qBittorrent/NZBGet/Kapowarr untouched | PASS |

### Note on the acquisition test

Per the task constraint, **no copyrighted material was downloaded**. The
download *pipeline* was verified up to source page resolution via the built-in
admin source probe (search → covers → series page → chapter list → page list).
The filesystem and library-recognition halves were verified with a **self-
generated public-domain test CBZ** (two programmatically-drawn PNG pages plus
`ComicInfo.xml`) written to `/hive/comics/uchiyomi/library/`; Uchiyomi scanned
it (1 series, 1 book), exposed its 2 pages via the reader API, and the artifact
was then removed and the app reset to a pristine first-run state. No third-party
chapter was saved to disk.

## Access

- URL: `https://uchiyomi.fatherfankscloud.uk` (internal only; LAN + Tailscale via
  the split-horizon `mocha` record; no public exposure).
- Initial admin username/password: see `/mnt/monarch/appdata/uchiyomi/admin-credentials.txt`
  (mode `600`, outside git). Change it after first login.

## Storage

| Host path | Container | Notes |
|---|---|---|
| `/hive/comics/uchiyomi/library` | `/library` | owned library, initially empty |
| `/hive/comics/uchiyomi/downloads` | `/library-dl` | Uchiyomi download target |
| `/hive/comics/uchiyomi/sources` | `/sources` (ro) | optional source pack, empty |
| `/mnt/monarch/appdata/uchiyomi/data` | `/data` | embedded Postgres |
| `/mnt/monarch/appdata/uchiyomi/config` | `/config` | generated JWT/VAPID secrets |
| `/mnt/monarch/appdata/uchiyomi/cache` | `/cache` | image cache |
| `/mnt/monarch/appdata/uchiyomi/backups` | `/backups` | nightly DB dumps |
| `/mnt/monarch/appdata/uchiyomi/suwayomi` | engine datadir | extensions |

## Changes made

- Added `services/uchiyomi/` (compose.yaml, .env, .env.example, README.md,
  Versions.md, VALIDATION.md). New files only.
- Created media/appdata directories listed above.
- Added one Technitium DNS record (CNAME `uchiyomi`).
- **No existing service, compose file, library, or media was modified.**

## Cleanup note

The app's embedded database and `/config` were reset once after testing, so the
install is at a clean first-run state with only the admin account created.
