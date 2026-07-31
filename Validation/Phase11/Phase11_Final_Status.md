# Phase 11 — Final Status

**Date:** 2026-07-31  
**Basis:** [Completion_Audit.md](Completion_Audit.md), [StandardsRoadmap.md](../../Architecture/standards/StandardsRoadmap.md) Phase 11, Phase 10.5 Migration Matrix, Phase 10.75 import scope  
**Recommendation:** **COMPLETE WITH DEFERRED ITEMS**

---

## Roadmap success criteria (Phase 11)

From StandardsRoadmap — Phase 11 *Storage Modernization*:

| Deliverable | Phase 11 outcome |
|---|---|
| AppData migration | **Met for the core hive→appdata wave** defined by the Phase 10.5 matrix (see below) |
| Media separation | **Met** — Jellyfin media, downloads, libraries remain on `/hive` by policy |
| Compose updates | **Met for cut-over services**; remaining compose SoT cleanup deferred |
| Validation | **Met** — framework + per-service reports + completion audit |
| Storage standards | **Met** — `services.conf` policy, excludes, appdata layout |
| Backup redesign | **Not executed in Phase 11** → deferred (architecture), not a migration failure |

Phase 11 was never “migrate every container on the host.” Phase 10.75 explicitly imported CasaOS services **without** live appdata cutover. Phase 13.1 owns Ollama/Open WebUI platform work.

---

## What Phase 11 actually achieved

### Migration framework

| Capability | Status |
|---|---|
| Dry-run → copy → verify → compose → smoke orchestrator | Production-proven across Batches 01–06 |
| Checksum verify (`LC_ALL=C` set comparison) | Fixed + 24/24 regression tests |
| `rsync_excludes` + exclude-aware inventory | Proven (NZBGet, Jellyfin) |
| Proposed-compose `.env` staging | Fixed |
| Post-start `--smoke-only` | Fixed |
| Rollback via `.old` (no auto-delete) | Retained for soak |

**Verdict:** Framework satisfies Phase 11 validation/storage-standards needs and is ready for later cutovers.

### Core hive → `/mnt/monarch/appdata` migrations (READY FOR SOAK)

| Service | New config path |
|---|---|
| Portainer | `/mnt/monarch/appdata/portainer` |
| Homepage (+ images path) | `/mnt/monarch/appdata/homepage` |
| code-server | `/mnt/monarch/appdata/code-server` |
| Authentik | `/mnt/monarch/appdata/authentik` |
| Calibre | `/mnt/monarch/appdata/calibre` |
| Calibre-Web | `/mnt/monarch/appdata/calibre-web` |
| Traefik (ACME/data) | `/mnt/monarch/appdata/traefik` |
| Beszel | already on appdata (verified) |
| NZBGet | `/mnt/monarch/appdata/nzbget` |
| Hotio | `/mnt/monarch/appdata/hotio` |
| Jellyfin | `/mnt/monarch/appdata/jellyfin` |

Also already on appdata (no storage move required): n8n, Open WebUI data, Hermes data, Honcho data, Beszel-agent, Odysseus data.

### Media separation

Confirmed live: large datasets stay on `/hive` (TV/movies, downloads, libraries). Config/state moved to SSD appdata where Phase 11 cut over.

---

## Migration failures vs non-failures

### 1. True migration failures / unfinished *storage* moves

These are cases where Phase 11 **intended or attempted** a persistent-config move and it did **not** land on `/mnt/monarch/appdata`.

| Item | Reality | Classification |
|---|---|---|
| **Ollama** | Still `/hive/ollama` (~64G). Batch 04 stopped before execute. Matrix listed it as migratable. | **Unfinished storage migration** — but roadmap also places Ollama under **Phase 13.1**; treat as **deferred storage exception**, not a broken cutover |
| Homepage images leftover | Live images on appdata; `/hive/data/homepage/images` never renamed `.old` | **Cleanup debt**, not a failed config move |

No completed cutover left durable config on the wrong path with a broken service as a result of a failed migrate. Aborts (Jellyfin checksum false positive; Batch05 CasaOS STOP) were handled safely.

### 2. Not migration failures (do not score Phase 11 as failed)

| Item | Why it is not a migration failure |
|---|---|
| Hermes / Honcho smoke “SOAK FAILED” | Config **already on appdata**; failures are permissions / runtime smoke, not hive→appdata |
| CasaOS `/DATA/AppData` services | Phase 10.75 imported compose only; live cutover was never Phase 11 Batch 01–06 scope |
| Traefik still launched from `/hive/traefik` | ACME already on appdata; remaining work is **compose source-of-truth** |
| n8n / Beszel / Odysseus compose under appdata trees | Storage already modernized; repo SoT is governance |
| Nextcloud / Readarr / Kavita (`/ssd`) / Crafty / *arr* | Imported or inventoried; cutover = later migration/governance batches |
| Portainer `health=unhealthy` | Distroless healthcheck issue; API smoke passed at migrate time |
| Backup redesign | Roadmap deliverable not done → **defer**, not a migrate fail |
| Large `.old` trees | Intentional soak retention |

---

## Distilled verdict against roadmap

| Question | Answer |
|---|---|
| Did Phase 11 modernize production appdata storage for the planned hive wave? | **Yes** |
| Is media separated from app config? | **Yes** |
| Is the migration framework validated? | **Yes** |
| Must every host service be on appdata for Phase 11 to close? | **No** (roadmap + 10.75 + 13.1 say otherwise) |
| Are remaining items blockers to closing Phase 11? | **No** — they are deferred work (see [Phase11_Remaining_Work.md](Phase11_Remaining_Work.md)) |

---

## Recommendation

# COMPLETE WITH DEFERRED ITEMS

**Mark Phase 11 closed** for storage modernization of the Phase 10.5 hive matrix and for delivery of a production-ready migration framework.

Carry forward unfinished items as **explicit deferred work** into Phase 12+ / Phase 13.1 / dedicated CasaOS-cutover batches — not as open Phase 11 migration failures.

Do **not** use “every container migrated” as the exit criterion; that conflates storage modernization with CasaOS retirement and AI platform redesign.
