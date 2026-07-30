# Phase 10.5 — Migration Inventory (hardened)

**Host:** mocha · **Scope:** `services/` · **Updated after first dry-run:** 2026-07-30  
**Runtime changes in this phase:** none (framework/docs only)

## Policy (final)

| Class | Location |
|-------|----------|
| Docker application configuration / state | `/mnt/monarch/appdata/<service>` |
| Large datasets | stay on `/hive` |
| **Exception — Ollama** | config **and** models → `/mnt/monarch/appdata/ollama` (relocatable later via `services.conf`) |

## Assumptions

- Authoritative compose = tracked `services/` (not Portainer stack copies under `/hive/portainer/compose/*`).
- `Services/.env` sets `PATH_DATA` / `PATH_CONFIG` to `/mnt/monarch/appdata` when stacks use env mounts.
- Live container mounts may **drift** from repo compose (homepage is the known example).
- Inventory sizes use `du`/`find`; permission-denied paths produce a **partial-stats warning**, not a silent abort.

## Expected warnings (not failures)

| Warning | Meaning |
|---------|---------|
| git working tree not clean | EXPECTED while Phase 10.5 is uncommitted |
| Target missing — EXPECTED in dry-run | Copy not executed yet |
| destination populated (EXPECTED for verify/already_migrated) | Traefik acme / beszel data already on appdata |
| compose missing .env / unset variables | Create `.env` from `.env.example` before `--execute` |
| Partial tree stats / permission-denied | e.g. root-owned Portainer `compose/49`,`compose/50` |
| Container not found for inspect | Stack stopped or different container names |
| Shared docker.sock in multiple stacks | EXPECTED — not a real duplicate |

## Per-service notes (post dry-run)

### Migration candidates (`required=yes`)

| Service | Source | Target | Excludes | Live notes |
|---------|--------|--------|----------|------------|
| code-server | `/hive/code-server/config` (~1.6–3GB) | `/mnt/monarch/appdata/code-server` | — | Needs `.env` (`PASSWORD`) before execute |
| homepage | `/hive/config/homepage` | `/mnt/monarch/appdata/homepage` | — | **Live drift:** container still on `/hive/config` + `/hive/data`, not PATH_* |
| homepage-images | `/hive/data/homepage/images` | `/mnt/monarch/appdata/homepage/images` | — | Run after/with homepage |
| portainer | `/hive/portainer` (~815K) | `/mnt/monarch/appdata/portainer` | `compose/49,compose/50` | Source path **correct** (matches container `/data`); tiny tree; root-owned stack dirs |
| ollama | `/hive/ollama` (~64GB) | `/mnt/monarch/appdata/ollama` | — | Intentional models move; needs `.env` |
| calibre | `/hive/calibre/config` | `/mnt/monarch/appdata/calibre` | — | Books stay `/hive/library` |
| calibre-web | `/hive/calibre-web/config` | `/mnt/monarch/appdata/calibre-web` | — | Books stay |
| jellyfin | `/hive/jellyfin/config` (~9GB) | `/mnt/monarch/appdata/jellyfin` | — | Media stays; may need `.env` |
| nzbget | `/hive/NZBget/config` | `/mnt/monarch/appdata/nzbget` | `downloads/**,*.log,nzbget.log` | Nested `config/downloads` ~110G + huge log — **must exclude** |
| hotio | `/hive/Hotio/config` | `/mnt/monarch/appdata/hotio` | — | Downloads stay |

### Verify-only / already on appdata

| Service | Status |
|---------|--------|
| traefik | acme already at `/mnt/monarch/appdata/traefik/acme.json` |
| beszel, honcho, hermes, n8n, open-webui | already on appdata |
| authentik | compose uses `PATH_DATA`; live appdata dir may be absent if stack not running from repo |

### Deferred / out of scope

beszel-agent (relative), echoos (classify graph), cosmoos (`/var/lib/cosmos`), odysseus (relative + pool mounts), Kavita/Nextcloud (untracked).

## Known limitations

- `services.conf` rsync excludes are best-effort for size estimates; always review `rsync --stats` dry-run.
- Homepage requires **two** migration keys (config + images) plus compose/env alignment.
- Portainer `compose/*` historical stack YAMLs are part of Portainer `/data` — migrating them is fine; they are not “live compose authority”.
- NZBget after migrate should keep nested downloads on hive (exclude) **or** re-point NZBget internal paths — operator must confirm app config after move.

## Prerequisites before any Phase 11 execute

1. `.env` present for stacks that declare `env_file`
2. `PATH_*` correct in `Services/.env`
3. Dry-run SUCCESS summary with zero critical errors
4. Proposed compose diff reviewed
5. Free space ≥ migratable estimate + 10% + 100MiB
