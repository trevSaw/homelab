# Phase 10.5 / Phase 11 — Post-Migration Verification Audit

**Generated:** 2026-07-30T11:30:00Z (read-only)  
**Host:** mocha  
**Scope:** Verify listed services after Phase 10.5 framework + Phase 11 live batches  
**Mutations:** none (no compose edits, no deletes, no migrations)

## Executive Summary

This audit checks whether each service is **actually running from `/mnt/monarch/appdata`** (or correctly classified as verify/already-migrated / not-yet-migrated), and whether it is healthy enough for soak.

| Result | Count |
|--------|------:|
| Services audited | 14 |
| PASS / READY FOR SOAK | 8 |
| WARNING / NEEDS REVIEW | 3 |
| FAIL | 3 |

**Overall Phase status:** **NEEDS REVIEW** — several services are correctly on appdata and healthy, but **Honcho**, **Hermes**, and **Ollama** (not migrated) block a clean “all clear,” and **n8n** Traefik routing plus a few drift/soak caveats need attention before `.old` cleanup.

---

## Per-service status

| Service | Verdict | Recommendation |
|---------|---------|----------------|
| Portainer | PASS (warn: Docker healthcheck) | READY FOR SOAK |
| Homepage | PASS | READY FOR SOAK |
| Homepage Images | PASS (empty tree) | READY FOR SOAK |
| Code-Server | WARNING (post-cutover tree drift) | NEEDS REVIEW |
| Traefik (verify) | PASS (warn: compose still hive-managed) | READY FOR SOAK |
| Beszel | PASS | READY FOR SOAK |
| Honcho | FAIL (Postgres permissions) | ROLLBACK RECOMMENDED* |
| Hermes | FAIL (uid mismatch / kanban) | NEEDS REVIEW |
| n8n | WARNING (data OK; Traefik host timeout) | NEEDS REVIEW |
| Open WebUI | PASS (warn: compose project still under `/hive/ollama`) | READY FOR SOAK |
| Authentik | PASS | READY FOR SOAK |
| Calibre | PASS | READY FOR SOAK |
| Calibre-Web | PASS | READY FOR SOAK |
| Ollama | FAIL (not migrated) | NEEDS REVIEW |

\*Honcho data is already on appdata; “rollback” means restore DB usability (ownership fix / restore from backup), not necessarily move paths back to hive.

---

## 1. Portainer — PASS — READY FOR SOAK

### Source / destination / mounts
| Item | Value |
|------|-------|
| Original | `/hive/portainer` → `/hive/portainer.old` |
| New | `/mnt/monarch/appdata/portainer` |
| Live mount | `/mnt/monarch/appdata/portainer` → `/data` |
| Compose project | `services/portainer/compose.yaml` |

### Compose
- Bind: `/mnt/monarch/appdata/portainer:/data` — **no legacy `/hive/portainer`**

### Data (`.old` vs new)
| | `.old` | appdata |
|--|--------|---------|
| Files | 18 | 18 |
| Dirs | 19 | 17 |
| Size | ~2.6MB | ~2.6MB |

Dir delta expected (excluded root-owned `compose/49|50`). Slight byte growth on appdata from live use after cutover.

### Permissions
`fatherfrank:fatherfrank`, broadly `0777` on tree (historical). Container runs and serves API.

### Health / logs / smoke
- Status: `running`, Docker health **unhealthy** (distroless image lacks `/bin/sh` for `CMD-SHELL` wget) — **functional**
- Restarts: 0
- Logs: clean INF startup; deprecation WARN on `/status`
- Smoke: `http://127.0.0.1:9000/api/status` → **200**

### `.old`
Present; directory mtime pre-dates migration day. Safe to retain for soak. **Do not delete yet.**

---

## 2. Homepage — PASS — READY FOR SOAK

### Source / destination / mounts
| Item | Value |
|------|-------|
| Original config | `/hive/config/homepage` → `.old` |
| New | `/mnt/monarch/appdata/homepage` |
| Live mounts | appdata config + images |
| Compose | `services/homepage/compose.yaml` via `PATH_*=/mnt/monarch/appdata` |

### Compose
- `${PATH_CONFIG}/homepage`, `${PATH_DATA}/homepage/images` resolve to appdata
- No literal legacy hive config binds

### Data
| | `.old` config | appdata |
|--|---------------|---------|
| Files | 3 | 3 |
| Dirs | 2 | 3 (extra `images/`) |
| Size | 14K / 42KB tree | 52K |

### Health / smoke
- `healthy`, restarts 0
- Logs clean (24h)
- `https://home.fatherfankscloud.uk/` → **200**

### `.old`
`/hive/config/homepage.old`, `/hive/homepage.old` present. Safe to retain.

---

## 3. Homepage Images — PASS — READY FOR SOAK

| Item | Value |
|------|-------|
| Original | `/hive/data/homepage/images` (**still present**, root-owned; **not renamed to `.old`**) |
| New | `/mnt/monarch/appdata/homepage/images` (empty) |
| Live mount | appdata images → `/app/public/images` |

Both trees empty (0 files). Migration of empty companion path succeeded; **operator still owes** `sudo mv ... images.old` for rollback hygiene.

---

## 4. Code-Server — WARNING — NEEDS REVIEW

### Source / destination / mounts
| Item | Value |
|------|-------|
| Original | `/hive/code-server` → `.old` |
| New | `/mnt/monarch/appdata/code-server` |
| Live `/config` | **appdata** |
| Intentional `/hive` | RO workspace `/hive` → `/config/workspace/hive` |

### Compose
- Config on appdata ✓  
- Legacy config path gone ✓  
- `/hive` RO workspace **intentional** ✓  
- Typo path `workspcae` remains (pre-existing)

### Data drift (material)
| | `.old/config` | appdata |
|--|---------------|---------|
| Files | 41259 | **40934** (−325) |
| Dirs | 6886 | **6769** |
| Bytes | ~3.20GB | ~3.06GB |

Post-cutover live use (e.g. extension cleanup observed at migration) explains drift. **Not bit-identical to `.old`.** Soak OK if intentional; do not treat trees as frozen equals.

### Health / smoke
- `running`, restarts 0
- Logs: normal LSIO migrations banner
- `https://code.fatherfankscloud.uk/` → **302** (auth)

### `.old`
Present (~1.6G parent / ~3.2G config tree). Retain for soak; compare carefully before delete.

---

## 5. Traefik (verify only) — PASS — READY FOR SOAK

### Source / destination / mounts
| Item | Value |
|------|-------|
| Live ACME | `/mnt/monarch/appdata/traefik/acme.json` ✓ |
| Stale leftover | `/hive/config/traefik.old` |
| Compose project | **still** `/hive/traefik/compose.yaml` (not cut to repo) |

### Compose (repo)
- `${PATH_CONFIG}/traefik/acme.json` with `PATH_CONFIG=/mnt/monarch/appdata` — correct when used  
- Live stack not yet switched to `services/traefik`

### Data
| | stale `.old` acme | live appdata acme |
|--|-------------------|-------------------|
| Size | ~21KB (Feb) | ~31KB (Jul 20) |

Live cert store is the newer appdata file.

### Health / smoke
- `running` since 2026-07-27; no restart loop
- ACME file mode `0600`
- Routed checks: home/sso/calibre **200**
- Logs: routine TLS EOF / 499 noise only

### Recommendation
READY FOR SOAK for **data path**. Optional follow-up: cut compose management from `/hive/traefik` → repo (maintenance window).

---

## 6. Beszel — PASS — READY FOR SOAK

| Item | Value |
|------|-------|
| Data | `/mnt/monarch/appdata/beszel/beszel_data` |
| Compose | appdata + repo both point at appdata |
| Container | `running` |
| Smoke | `http://127.0.0.1:8090/` → **200** |
| Agent | `beszel-agent` Up; log: `WebSocket connected host=mocha:8090` |

No hive config `.old` (already-migrated). No Traefik hostname required (host port publish).

---

## 7. Honcho — FAIL — ROLLBACK RECOMMENDED*

### Mounts / compose
- Postgres: `/mnt/monarch/appdata/honcho/postgres` ✓ (already on appdata)  
- Redis: `/mnt/monarch/appdata/honcho/redis` ✓  
- Repo compose matches appdata paths ✓  

### Health / logs / smoke
- Containers `running` but **Postgres unusable**
- Logs (24h): hundreds of `FATAL: could not open file "global/pg_filenode.map": Permission denied`
- `psql` fails with same error
- `https://honcho.fatherfankscloud.uk/` → **timeout**

### Permissions
`pgdata` owned by **uid 1000** with `0600` files; Postgres role cannot open maps.

### Recommendation
**Not soak-ready.** Fix ownership / restore DB before any further migration work depending on Honcho. Path location is already appdata; problem is **access**, not missing migration.

---

## 8. Hermes — FAIL — NEEDS REVIEW

### Mounts / compose
- `/mnt/monarch/appdata/hermes` → `/opt/data` ✓  
- Compose hard-coded appdata ✓  

### Health / logs / smoke
- `running`; UI `https://hermes.fatherfankscloud.uk/` → **302**
- Logs: recurring `PermissionError` on `/opt/data/kanban.db.init.lock` (158+ matches / 24h)
- Gateway process **uid 10000**; data owned by **uid 1000**

### Recommendation
Core UI responds, but kanban subsystem is broken. Treat as **NEEDS REVIEW / not clean soak** until ownership aligned with runtime uid.

---

## 9. n8n — WARNING — NEEDS REVIEW

### Mounts / compose
- `/mnt/monarch/appdata/n8n` (+ workflows/reports) ✓  
- Compose on appdata; no hive config binds ✓  
- `database.sqlite` present (~4.8MB)

### Health / logs / smoke
- `running`
- Logs: workflow axios `ECONNREFUSED 0.0.0.0:443` (workflow/network issue, not mount)
- Direct `http://127.0.0.1:5678/` → **200**
- Traefik hostname check **timed out** (routing/DNS/label gap vs direct port)

### Recommendation
Migration path **OK**. Fix Traefik exposure before calling edge access “verified.” Data soak can proceed with warning.

---

## 10. Open WebUI — PASS — READY FOR SOAK

| Item | Value |
|------|-------|
| Data mount | `/mnt/monarch/appdata/open-webui` ✓ |
| Health | `healthy` |
| Smoke | `https://chat.fatherfankscloud.uk/` → **200** |
| Compose project | still `/hive/ollama/compose.yml` (shared stack) |
| Repo compose | open-webui already on appdata; ollama still `/hive/ollama` |

Warning only: stack management still hive-side until Ollama migration/compose cutover.

---

## 11. Authentik — PASS — READY FOR SOAK

### Mounts
- db/redis/media/templates/certs under `/mnt/monarch/appdata/authentik/*` ✓  
- Compose uses `${PATH_DATA}` → `/mnt/monarch/appdata` ✓  

### Data
Docker root compare vs `/hive/data/authentik.old`: **3092 files / 33 dirs** both sides. Byte delta small (live redis/db writes after cutover). Host `find` without root under-counts `.old` (permission).

### Health / smoke
- server/worker/db/redis all **healthy**
- `https://sso.fatherfankscloud.uk/-/health/live/` → **200**
- Logs: normal migrate/gunicorn; no permission storm

### `.old`
`/hive/data/authentik.old`, `/hive/authentic.old` present. Retain ≥ 7 days.

---

## 12. Calibre — PASS — READY FOR SOAK

| Item | Value |
|------|-------|
| Config | appdata ✓ |
| Books | `/hive/library/.../novelas` intentional ✓ |
| browser_cache | hive intentional ✓ |
| Data vs `.old` | 312 files / 171 dirs both; slight byte growth |
| Smoke | `https://calibre.fatherfankscloud.uk/` → **200** |

---

## 13. Calibre-Web — PASS — READY FOR SOAK

| Item | Value |
|------|-------|
| Config | appdata ✓ |
| Books | hive intentional ✓ |
| Data | `.old` 6 files; appdata **7** (live log growth) |
| Smoke | `https://calib.fatherfankscloud.uk/` → **302** |

---

## 14. Ollama — FAIL — NEEDS REVIEW (not migrated)

| Item | Value |
|------|-------|
| Live mount | **`/hive/ollama` → `/root/.ollama`** |
| Appdata target | **MISSING** (`/mnt/monarch/appdata/ollama` does not exist) |
| Repo compose | still `/hive/ollama:/root/.ollama` |
| Size on hive | **~64GB** / 76 files |
| Smoke | `ollama list` **succeeds** (models present on hive) |

Phase 11 Batch 04 stopped before Ollama. **Not migrated.** Do not remove `/hive/ollama`.

---

## Comparison to Phase 10.5 / Phase 11 reports

| Expectation from reports | Audit finding |
|--------------------------|---------------|
| Portainer/Homepage/code-server/Authentik/Calibre* READY FOR SOAK | Confirmed on appdata; functional with noted warnings |
| Traefik verify-only on appdata ACME | Confirmed; compose project still hive-managed |
| Beszel/n8n/open-webui/hermes/honcho already on appdata | Confirmed paths; **Honcho/Hermes health fail** |
| Ollama required migrate | **Not done** |
| Homepage images `.old` rename | **Still outstanding** (`/hive/data/homepage/images` remains) |
| Code-server checksum match at cutover | **Now drifted** vs `.old` (expected post-soak live use) |
| Portainer unhealthy healthcheck | Still present; API OK |

---

## Outstanding issues (before any `.old` deletion)

1. **Ollama:** complete Phase 11 migration (`/hive/ollama` → appdata) when ready (~64GB).  
2. **Honcho:** repair Postgres permissions / restore DB; re-verify `psql` + Traefik.  
3. **Hermes:** align data ownership with runtime uid `10000` (or change user); silence kanban PermissionError.  
4. **n8n:** restore Traefik route (or document host-port-only access).  
5. **Homepage images:** `sudo mv /hive/data/homepage/images /hive/data/homepage/images.old`.  
6. **Traefik (optional):** cut compose project from `/hive/traefik` to repo after env readiness.  
7. **Portainer (optional):** replace broken distroless healthcheck.  
8. **Code-Server:** accept tree drift or re-sync before deleting `.old`.  
9. **Soak policy:** keep all `.old` trees ≥ 7 days after *successful* soak of that service; never delete Ollama hive until migrated + soaked.

---

## Overall recommendation

| Metric | Value |
|--------|-------|
| Services verified | 14 |
| PASS | 8 (Portainer*, Homepage, Homepage Images, Traefik*, Beszel, Open WebUI*, Authentik, Calibre, Calibre-Web) |
| WARNING | 3 (Code-Server drift, n8n Traefik, Open WebUI/Traefik compose footnotes counted above as PASS-with-warn / WARNING) |
| FAIL | 3 (Honcho, Hermes, Ollama) |

\*Portainer/Traefik/Open WebUI carry non-blocking warnings described above.

**Overall Phase 10.5→11 status:** **NEEDS REVIEW** — majority of migrated configs are on appdata and working, but **do not declare the modernization migration complete** until Honcho and Hermes permission failures are fixed and Ollama is migrated (or explicitly deferred with hive keep documented).

**Do not remove `.old` directories yet** except after per-service soak clearance and resolution of the outstanding list above.
