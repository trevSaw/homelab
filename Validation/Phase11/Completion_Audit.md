# Phase 11 — Completion Audit

**Audit date:** 2026-07-31T12:10Z  
**Scope:** Live Docker host only (read-only)  
**Evidence sources:** `docker inspect` of all containers, bind mounts, compose working dirs, `/mnt/monarch/appdata`, `/hive`, `/DATA/AppData`, `/ssd/appdata`, `scripts/migration/*`, `Validation/Phase11/**`

## Conclusion

# ❌ Phase 11 NOT COMPLETE

Phase 11 successfully migrated a core set of hive-managed services to `/mnt/monarch/appdata`, and the migration framework is patched and regression-tested. However, **multiple live services still store persistent application configuration outside `/mnt/monarch/appdata`** (notably Ollama on `/hive`, Nextcloud on `/hive`, Readarr on `/hive`, Kavita on `/ssd`, and the CasaOS `/DATA/AppData` *arr / utility stack). Batch 03–05 also left soak/smoke failures and stopped cutovers unresolved.

Phase 12 should **not** be treated as unblocked until remaining config migrations are finished or explicitly deferred with updated policy.

---

## Executive counts

| Metric | Count | Notes |
|---|---:|---|
| Running/stopped containers discovered | **41** | All via `docker ps -a` + inspect |
| Compose projects (logical services) | **29** | Grouped by `com.docker.compose.project` |
| ✅ Migrated (config on appdata) | **13** projects | Includes stacks already on appdata |
| ⚠ Partially migrated | **2** | Traefik; Ollama/Open-WebUI stack |
| ❌ Not migrated | **12** | Hive / DATA / SSD config still live |
| ➖ Exempt / deferred | **2** | Byparr; Odysseus (Nextcloud DB noted as databases-path exception under cloud) |
| Phase 11 `READY FOR SOAK` reports | **12** service folders | See Audit 6 |
| Phase 11 `SOAK FAILED` / STOP unresolved | **2** | Hermes, Honcho (location already appdata) |

Machine-readable detail: [`Completion_Audit.json`](Completion_Audit.json)

---

## Audit 1 — Live container inventory

41 containers inspected. Summary by compose project:

| Project | Containers | Status | Health | Compose location | Config bind(s) |
|---|---|---|---|---|---|
| jellyfin | jellyfin | running | healthy | repo `services/jellyfin` | `/mnt/monarch/appdata/jellyfin` (+ hive media) |
| nzbget | nzbget | running | n/a | repo `services/NZBget` | `/mnt/monarch/appdata/nzbget` (+ `/hive/downloads`) |
| hotio | qbittorrent | running | n/a | repo `services/Hotio` | `/mnt/monarch/appdata/hotio` (+ downloads) |
| calibre-web | calibre, calibre-web | running | n/a | repo `services/calibre-web` | `/mnt/monarch/appdata/calibre{,-web}` (+ library) |
| authentic | authentik-* (4) | running | healthy | repo `services/authentic` | `/mnt/monarch/appdata/authentik/*` |
| code-server | code-server | running | n/a | repo `services/code-server` | `/mnt/monarch/appdata/code-server` (+ RO `/hive` workspace) |
| homepage | homepage | running | healthy | repo `services/homepage` | `/mnt/monarch/appdata/homepage` |
| portainer | portainer | running | **unhealthy** | repo `services/portainer` | `/mnt/monarch/appdata/portainer` |
| n8n | n8n | running | n/a | `/mnt/monarch/appdata/n8n` | appdata |
| beszel | beszel | running | n/a | `/mnt/monarch/appdata/beszel` | appdata |
| beszel_agent | beszel-agent | running | n/a | `/mnt/monarch/appdata/beszel_agent` | appdata |
| hermes | hermes | running | n/a | `/mnt/monarch/appdata/hermes` | appdata |
| honcho | honcho-* (4) | running | n/a | `/mnt/monarch/appdata/honcho` | postgres/redis on appdata |
| odysseus | odysseus-* (4) | running | mixed | `/mnt/monarch/appdata/odysseus` | appdata data + whole `/hive` tooling mount |
| traefik | traefik | running | n/a | **`/hive/traefik`** | `acme.json` on appdata |
| ollama | ollama, open-webui | running | mixed | **`/hive/ollama`** | ollama=`/hive/ollama`; open-webui=appdata |
| cloud | nextcloud, nextcloud-db | running | n/a | **`/hive/cloud`** | app on hive; DB on `/mnt/monarch/databases` |
| kavita | kavita | running | healthy | `/hive/library/Kavita` | **`/ssd/appdata/kavita/config`** |
| readarr | readarr | running | n/a | Portainer `/data/compose/39` | **`/hive/readarr`** |
| glorious_thomas | prowlarr | running | n/a | CasaOS | `/DATA/AppData/config` |
| radarr | radarr | running | n/a | CasaOS | `/DATA/AppData/radarr/config` |
| breathtaking_ken | jellyseerr | running | n/a | CasaOS | `/DATA/AppData/jellyseerr/config` |
| bazarr | bazarr | running | n/a | CasaOS | `/DATA/AppData/bazarr/config` |
| big-bear-actual-server | actual-server | running | n/a | CasaOS | `/DATA/AppData/big-bear-actual-server` |
| linuxserver-lazylibrarian | …-app-1 | running | n/a | CasaOS | `/DATA/AppData/lazylibrarian/config` |
| big-bear-crafty | big-bear-crafty | running | n/a | CasaOS | `/DATA/AppData/big-bear-crafty/data/*` |
| linuxserver-mariadb | …-app-1 | running | n/a | CasaOS | `/DATA/AppData/mariadb/config` |
| uptimekuma | uptimekuma | running | healthy | CasaOS | `/DATA/AppData/uptimekuma/app/data` |
| byparr | byparr-byparr-1 | running | healthy | Portainer `/data/compose/50` | **no bind mounts** |

Restart policy: virtually all `unless-stopped`.

Full per-container mount tables are in the JSON artifact.

---

## Audit 2 — Migration status (logical services)

Classification rules used:

- **✅ Migrated** — persistent *application config/state* under `/mnt/monarch/appdata/<service>` (intentional hive media/downloads mounts allowed).
- **⚠ Partial** — persistent config split across locations, or compose still rooted on `/hive` while data is on appdata.
- **❌ Not migrated** — live persistent config still under `/hive`, `/DATA/AppData`, or `/ssd/appdata`.
- **➖ Exempt** — intentionally elsewhere / no config binds / deferred by policy.

### ✅ Migrated

| Service | Live config | Evidence |
|---|---|---|
| Jellyfin | `/mnt/monarch/appdata/jellyfin` | mounts + Batch06 READY FOR SOAK; media stays on hive |
| NZBGet | `/mnt/monarch/appdata/nzbget` | mounts + Batch05; `.old` present |
| Hotio (qbittorrent) | `/mnt/monarch/appdata/hotio` | mounts + Batch05 |
| Calibre | `/mnt/monarch/appdata/calibre` | mounts + Batch02 |
| Calibre-Web | `/mnt/monarch/appdata/calibre-web` | mounts + Batch02 |
| Authentik | `/mnt/monarch/appdata/authentik/*` | mounts + Batch02 |
| code-server | `/mnt/monarch/appdata/code-server` | mounts + Batch01; `/hive` is RO workspace only |
| Homepage | `/mnt/monarch/appdata/homepage` | mounts + Batch01 |
| Portainer | `/mnt/monarch/appdata/portainer` | mounts + Batch01 (**health=unhealthy**) |
| n8n | `/mnt/monarch/appdata/n8n` | mounts; already on appdata |
| Beszel | `/mnt/monarch/appdata/beszel` | mounts; already migrated |
| Beszel-agent | `/mnt/monarch/appdata/beszel_agent` | mounts (live already on appdata) |
| Hermes | `/mnt/monarch/appdata/hermes` | location migrated / already appdata; **smoke FAILED** (Batch04) |
| Honcho | `/mnt/monarch/appdata/honcho` | location migrated / already appdata; **smoke FAILED** (Batch03) |

### ⚠ Partially migrated

| Service | Why partial | Evidence |
|---|---|---|
| **Traefik** | ACME/data on appdata; **compose still executed from `/hive/traefik`** | `acme.json` → `/mnt/monarch/appdata/traefik/acme.json`; `compose_workdir=/hive/traefik`; `PATH_CONFIG=/mnt/monarch/appdata` |
| **Ollama / Open WebUI** | Open WebUI data on appdata; **Ollama models/config still `/hive/ollama` (~64G)**; stack compose still `/hive/ollama` | live mounts; repo compose still lists `/hive/ollama:/root/.ollama` |

### ❌ Not migrated

| Service | Live config location | Compose owner |
|---|---|---|
| Ollama | `/hive/ollama` (64G, mostly `models/`) | `/hive/ollama` |
| Nextcloud (app) | `/hive/cloud/nextcloud` + `/hive/cloud/config` | `/hive/cloud` |
| Readarr | `/hive/readarr` | Portainer compose/39 |
| Kavita | `/ssd/appdata/kavita/config` | `/hive/library/Kavita` |
| Prowlarr | `/DATA/AppData/config` | CasaOS `glorious_thomas` |
| Radarr | `/DATA/AppData/radarr/config` | CasaOS |
| Jellyseerr | `/DATA/AppData/jellyseerr/config` | CasaOS |
| Bazarr | `/DATA/AppData/bazarr/config` | CasaOS |
| Actual | `/DATA/AppData/big-bear-actual-server` | CasaOS |
| LazyLibrarian | `/DATA/AppData/lazylibrarian/config` | CasaOS |
| Crafty | `/DATA/AppData/big-bear-crafty/data/*` | CasaOS |
| MariaDB (linuxserver) | `/DATA/AppData/mariadb/config` | CasaOS |
| Uptime Kuma | `/DATA/AppData/uptimekuma/app/data` | CasaOS |

Note: Batch05 stopped at Prowlarr before CasaOS cutovers. `services.conf` now has rows for these, but **live cutover has not occurred**.

### ➖ Exempt / intentional exceptions

| Service | Why exempt |
|---|---|
| Byparr | No bind mounts (network-only); `services.conf` deferred |
| Odysseus stack | Data already under appdata; whole `/hive` + `/mnt/monarch` tooling mounts; `services.conf` deferred/partial — not a simple config move |
| Nextcloud DB | Lives at `/mnt/monarch/databases/nextcloud-mariadb` (database volume, not appdata config tree) |
| Media / downloads / libraries | Intentionally remain on hive (Jellyfin TV/movies, downloads, Kavita library trees, etc.) |
| EchoOS / CosmoOS | Deferred / out of hive→appdata scope per `services.conf` (not heavily exercised in this live set) |

---

## Audit 3 — Compose verification

### Matches (repo compose owns live container; paths aligned)

Verified live mounts match repo compose for: Jellyfin, NZBGet, Hotio, Calibre/Calibre-Web, Authentik, code-server, Homepage, Portainer.

### Mismatches / drift

| Service | Issue |
|---|---|
| Traefik | Live compose file is `/hive/traefik/compose.yaml`, not repo `services/traefik`. Data path already appdata via `PATH_CONFIG`. |
| Ollama / Open WebUI | Live compose is `/hive/ollama/compose.yml`. Repo `services/ollama/compose.yml` still targets `/hive/ollama` for Ollama. Open WebUI already appdata. |
| n8n / Beszel / Hermes / Honcho / Odysseus | Compose runs from **appdata trees**, not always from `services/` in the git repo (acceptable if intentional; still a governance drift vs “repo is SoT”). |
| CasaOS *arr stack | Live compose under `/var/lib/casaos/apps/...`; repo imports exist under `services/*` but are **not** what is running. |
| Readarr | Portainer `/data/compose/39`; repo import exists but not live-driving. |
| Kavita | Live compose under `/hive/library/Kavita`; config on `/ssd/appdata`. |
| Nextcloud | Live compose `/hive/cloud/compose.yaml`. |
| Portainer health | Live `health=unhealthy` despite migrated data path — operational issue, not a path mismatch. |

### Rollback paths documented (`.old` present)

Observed on disk:

`/hive/jellyfin/config.old`, `/hive/NZBget/config.old`, `/hive/Hotio/config.old`, `/hive/calibre/config.old`, `/hive/calibre-web/config.old`, `/hive/code-server.old`, `/hive/portainer.old`, `/hive/homepage.old`, `/hive/config/homepage.old`, `/hive/config/traefik.old`, `/hive/data/authentik.old`, `/hive/authentic.old`

---

## Audit 4 — Migration framework

| Check | Result | Evidence |
|---|---|---|
| Checksum verification patch present | ✅ | `build_checksum_inventory` / `compare_checksum_inventories` in `scripts/migration/lib/common.sh` |
| `LC_ALL=C` inventory build/sort | ✅ | `LC_ALL=C xargs`, `LC_ALL=C awk`, `LC_ALL=C sort` in inventory helpers |
| Set comparison (not positional locale sort) | ✅ | path-keyed MISSING/CHANGED/EXTRA report |
| Regression tests | ✅ | `scripts/migration/tests/test-checksum-verify.sh` → **passed=24 failed=0** (re-run during audit) |
| `update-compose` `.env` staging | ✅ | `Staged .env into proposed dir for compose validation` in `update-compose.sh` |
| `--smoke-only` post-start path | ✅ | `run-migration.sh` invokes verify with `--smoke-only` |
| Service-specific excludes functioning | ✅ | Jellyfin live: excludes `cache/**,data/transcodes/**,.temp/**,log/**`; verify matched **41099** files; dest cache/transcodes empty (0B) while metadata present |
| Framework readiness | **READY** | Suitable for remaining cutovers; do not bypass gates |

Write-up: [`Framework_Fix_Checksum_Locale.md`](Framework_Fix_Checksum_Locale.md)

---

## Audit 5 — Storage inventory

### Totals

| Path | Size | Notes |
|---|---|---|
| `/mnt/monarch/appdata` | **12G** | App configs post-migration |
| `/hive` | **14T** | Dominated by media (ignored below) |
| `/DATA/AppData` | **69G** | CasaOS app configs (Crafty ~68G) |
| `/ssd/appdata` | **83M** | Kavita config |

`/mnt/monarch` free space: ~1.9T available.

### `/mnt/monarch/appdata` (largest)

| Dir | Size |
|---|---|
| jellyfin | 7.0G |
| code-server | 3.0G |
| open-webui | 895M |
| odysseus | 114M |
| kavita (present but unused by live) | 83M |
| honcho | 40M |
| calibre | 38M |
| hotio | 23M |
| others | <10M each |

### Large **application configuration** still under `/hive` (media ignored)

| Path | Size | Classification |
|---|---|---|
| `/hive/ollama` | **64G** | ❌ live Ollama config+models |
| `/hive/jellyfin/config.old` | 9.0G | rollback (soak) |
| `/hive/NZBget/config.old` | 120G | rollback (includes excluded downloads/log) |
| `/hive/code-server.old` | 1.6G | rollback |
| `/hive/cloud/nextcloud` | 517M | ❌ live Nextcloud app tree |
| `/hive/readarr` | 10M | ❌ live Readarr config |
| `/hive/Hotio/config.old` | 21M | rollback |
| `/hive/calibre/config.old` | 23M | rollback |
| `/hive/traefik` | 25K | ⚠ live compose/env still here |
| `/hive/AppData` | 57G | mostly stale/CasaOS-adjacent trees; live *arr configs are under `/DATA/AppData` |

Intentionally ignored (not app config): `/hive/jellyfin/tv` (12T), `/hive/jellyfin/movie` (1.4T), `/hive/downloads` (114G), `/hive/library` (7.4G), Nextcloud user data (tiny on this host at audit time).

`/hive/bazarr` (9.8G) is **subtitle dataset / temp**, not the live Bazarr config (live config is `/DATA/AppData/bazarr/config`).

---

## Audit 6 — Phase 11 documentation

### Complete doc sets (Dry_Run + Migration_Report + Smoke_Test + reports/ + inspect/)

Present for: authentik, beszel, calibre, calibre-web, code-server, homepage, hotio, jellyfin, nzbget, portainer, traefik, hermes, honcho.

### Gaps / anomalies

| Item | Finding |
|---|---|
| n8n / open-webui / ollama | **No** Phase11 Migration_Report / Smoke / Dry_Run (Batch04 never reached them) |
| prowlarr | Only `STOP.md` (framework/CasaOS blocker) |
| Hermes / Honcho | Docs exist but final decision **SOAK FAILED** / STOP |
| Batch summaries | Batch01–06 present; Batch03/04/05 explicitly incomplete |
| Jellyfin | Full docs + Batch06; STOP superseded |

---

## Unresolved issues (blockers before Phase 12)

1. **Remaining config migrations** — Ollama (64G), Nextcloud, Readarr, Kavita (`/ssd`), and CasaOS `/DATA/AppData` services (Prowlarr/Radarr/Jellyseerr/Bazarr/Actual/LazyLibrarian/Crafty/MariaDB/Uptime Kuma).
2. **Compose SoT drift** — Traefik and Ollama stacks still launched from `/hive/...`; several appdata-native stacks not driven from git `services/`.
3. **Hermes + Honcho smoke failures** — data already on appdata, but Batch03/04 marked SOAK FAILED (permissions). Needs remediation or explicit deferral.
4. **Portainer unhealthy** — migrated path OK; healthcheck failing.
5. **Large `.old` trees** — especially NZBGet (120G) and Jellyfin (9G); soak cleanup not yet due / not performed.
6. **Batch05 CasaOS stop** — framework rows now exist, but live cutover was never completed.

---

## Recommended next phase actions

**Do not declare Phase 11 complete.** Recommended sequence:

1. Remediate Hermes/Honcho permissions → re-smoke → READY FOR SOAK or explicit exempt.
2. Finish Ollama intentional exception migration (`/hive/ollama` → `/mnt/monarch/appdata/ollama`) and move compose SoT to repo.
3. Move Traefik compose SoT from `/hive/traefik` → repo `services/traefik`.
4. Plan CasaOS → repo cutovers for `/DATA/AppData` services (one batch at a time).
5. Decide Kavita (`/ssd` → appdata?) and Nextcloud/Readarr hive configs.
6. Only then open Phase 12 with a clean “remaining exceptions” list.

---

## Final verdict

# ❌ Phase 11 NOT COMPLETE

Evidence: 12+ logical services still run with persistent configuration outside `/mnt/monarch/appdata`; Ollama alone retains ~64G on `/hive`; CasaOS stack never cut over after Batch05 STOP; Traefik/Ollama compose still hive-rooted; Hermes/Honcho soak failed.
