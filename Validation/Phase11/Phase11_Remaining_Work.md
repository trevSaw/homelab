# Phase 11 — Remaining Work

**Date:** 2026-07-31  
**Companion:** [Phase11_Final_Status.md](Phase11_Final_Status.md), [Completion_Audit.md](Completion_Audit.md)

This list separates **true leftover storage moves** from **architecture / governance** work.  
Architecture items are **deferred to Phase 12+** (or Phase 13.1 where noted). They are **not** Phase 11 migration failures.

---

## A. Deferred storage decisions (optional follow-on migrations)

These still have persistent config outside `/mnt/monarch/appdata`. They were **not** completed in Batches 01–06. Schedule deliberately; do not treat as Phase 11 blockers.

| Service | Current config | Suggested home | Suggested phase / note |
|---|---|---|---|
| **Ollama** | `/hive/ollama` (~64G models+config) | `/mnt/monarch/appdata/ollama` | **Phase 13.1** (AI platform) *or* dedicated storage batch; matrix already allows relocate-later |
| Open WebUI | already on appdata | keep | Align compose SoT when Ollama moves |
| Nextcloud app | `/hive/cloud/nextcloud` + config | TBD appdata vs hive cloud design | Future storage redesign; DB already on `/mnt/monarch/databases` |
| Readarr | `/hive/readarr` | `/mnt/monarch/appdata/readarr` | Post–CasaOS/Portainer cutover batch |
| Kavita | `/ssd/appdata/kavita/config` | `/mnt/monarch/appdata/kavita` or keep `/ssd` | Explicit storage decision (SSD vs monarch) |
| Prowlarr / Radarr / Jellyseerr / Bazarr | `/DATA/AppData/...` | `/mnt/monarch/appdata/<svc>` | CasaOS retirement + migrate batch |
| Actual / LazyLibrarian / Crafty / MariaDB / Uptime Kuma | `/DATA/AppData/...` | appdata | Same CasaOS cutover program |

Framework rows exist for most of these (`services.conf` + Phase 10.75 imports). Live cutover is remaining work, not a failed migrate.

---

## B. Architecture / governance (Phase 12+)

Do **not** classify as migration failures.

### B1. Compose source-of-truth

| Item | Current | Target |
|---|---|---|
| Traefik | Launched from `/hive/traefik` | Repo `services/traefik` (+ env) |
| Ollama / Open WebUI | Launched from `/hive/ollama` | Repo `services/ollama` after Ollama move |
| n8n, Beszel, Hermes, Honcho, Odysseus | Compose often under `/mnt/monarch/appdata/...` | Prefer git `services/` as SoT |
| CasaOS apps | `/var/lib/casaos/apps/...` | Repo compose + intentional recreate |
| Readarr | Portainer `/data/compose/39` | Repo `services/readarr` |
| Kavita | `/hive/library/Kavita/compose.yml` | Repo `services/kavita` |
| Nextcloud | `/hive/cloud/compose.yaml` | Repo `services/nextcloud` |

### B2. CasaOS retirement

Phase 10.75 completed **repository import**. Remaining:

- Stop using CasaOS as live orchestrator for imported apps
- Cut over one service at a time with the Phase 10.5 framework
- Retire `/DATA/AppData` and `/var/lib/casaos/apps` after soak
- Clean stale `/hive/AppData` mirrors when confirmed unused

### B3. Service redesign / platform work

| Item | Belongs in |
|---|---|
| Hermes uid/permissions remediation | Ops fix / AI stack hygiene (not storage migrate) |
| Honcho Postgres permissions | Ops fix (data already on appdata) |
| Portainer healthcheck (distroless) | Compose hardening |
| Odysseus whole-`/hive` tooling mounts | Deferred classification in `services.conf` |
| EchoOS / CosmoOS / Byparr | Already deferred / out of scope |
| Backup redesign (Phase 11 roadmap deliverable) | Dedicated backup phase or Phase 12+ storage/backup workstream |
| Storage standards docs polish | Architecture docs |

### B4. Future storage policy decisions

- Keep Kavita on `/ssd` vs move to monarch appdata  
- Nextcloud: what stays on hive vs appdata vs databases  
- Ollama models: SSD appdata sizing / later relocate (already noted as relocatable)  
- Whether `/hive/AppData` and Portainer legacy compose dirs are archived or deleted after cutover  

---

## C. Soak / cleanup (not architecture, not failures)

Execute only after agreed soak (≥ 7 days per successful service):

| Action | Paths |
|---|---|
| Remove `.old` after stable soak | jellyfin, NZBGet, Hotio, calibre*, authentik, homepage, code-server, portainer, … |
| Finish homepage images rename | `sudo mv /hive/data/homepage/images /hive/data/homepage/images.old` if still present and unused |
| Confirm backups cover **new** appdata paths before deleting `.old` | especially Jellyfin, Authentik, NZBGet |

Do not auto-delete. Do not delete `/hive/ollama` until Ollama is migrated and soaked.

---

## D. Suggested later-phase packaging

| Later phase / batch | Contents |
|---|---|
| **Phase 12** (Secrets & Security) | Proceed; not blocked by deferred storage items |
| **Ops remediation batch** | Hermes, Honcho, Portainer healthcheck |
| **Compose SoT batch** | Traefik → repo; appdata-launched stacks → `services/` |
| **CasaOS cutover program** | Prowlarr → … → Uptime Kuma (framework already mapped) |
| **Phase 13.1** | Ollama (+ models) migrate/relocate, Open WebUI compose alignment, GPU stack |
| **Cloud/storage redesign** | Nextcloud, Kavita path policy, backup redesign |

---

## E. What is *not* remaining Phase 11 work

- Re-litigating successful READY FOR SOAK cutovers (Jellyfin, NZBGet, Hotio, Authentik, Calibre*, Homepage, code-server, Portainer, …)
- Treating intentional hive media/downloads mounts as incomplete migration
- Treating CasaOS non-cutover as a Phase 11 failure (Phase 10.75 non-goal)
- Treating Hermes/Honcho permission smoke issues as storage migration failures

---

## Bottom line

**Phase 11 closes with deferred items.**  
Remaining host diversity is mostly **governance, CasaOS retirement, AI platform, and explicit storage decisions** — schedule those deliberately in Phase 12+ / 13.1 rather than holding Phase 11 open.
