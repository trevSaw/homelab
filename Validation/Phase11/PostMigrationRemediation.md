# Phase 11 — Post Migration Remediation

**Date:** 2026-07-30
**Type:** Remediation and validation pass (not a migration)
**Scope:** Honcho, Hermes, n8n, Homepage Images, Ollama
**Constraints honoured:** no services migrated, no `.old` directories deleted, no compose files rewritten, no unrelated cleanup

---

## Executive Summary

The two "SOAK FAILED" services (Honcho and Hermes) shared a **single common root cause** that the earlier
audit had attributed to two separate pre-existing problems. Evidence shows both were broken at the same
moment by one recursive ownership change applied to `/mnt/monarch/appdata`:

| Fact | Evidence |
|---|---|
| A single recursive metadata operation hit **all** of appdata | Every path sampled under `/mnt/monarch/appdata` carries ctime **2026-07-30 09:06:33 UTC** (spread over ~75 ms), while mtimes are unchanged (Jun/Jul dates) — i.e. ownership changed, content did not |
| Hermes broke 30 s later | First `PermissionError` at **09:07:03 UTC** |
| Honcho broke 38 s later | First `could not open file "global/pg_filenode.map"` at **09:07:11 UTC** |
| Neither had ever failed before | `PermissionError` count by date: **166, all 2026-07-30**. Postgres `Permission denied` count by date: **633, all 2026-07-30** |
| Honcho was healthy for 5 weeks on the same bind mount | `database system is ready to accept connections` on 2026-06-20, 2026-06-25, 2026-07-08 and **2026-07-24 14:04:52 UTC** |

The ownership change was almost certainly the operator's `chown -R` on `/mnt/monarch/appdata`, run at
09:06:33 UTC to clear the Portainer "destination not writable" STOP that blocked Batch 01. It flattened every
service's data to `1000:1000`. Services running as root or as uid 1000 (Portainer, Homepage, code-server,
Traefik, n8n, Open WebUI, Beszel, Calibre, Calibre-Web, Kavita, Odysseus) were unaffected. The only two
services running as a **non-root, non-1000** user — Honcho's PostgreSQL (uid 999) and Hermes' gateway
(uid 10000) — lost access to their own data.

This is therefore **not** a pre-existing fault, not a compose fault, and not a PostgreSQL fault. It is
collateral damage from a migration-support action, i.e. a **MIGRATION ISSUE** in both cases.

Because this is exactly the "verified ownership mismatch caused by the migration" case, the deterministic
correction (restore the image-documented uid/gid, ownership only) was applied to both services. Both are
now fully operational with zero errors since restart. n8n and Homepage Images were verified as functioning
correctly and are downgraded to **PASS**. Ollama remains **DEFERRED** and is confirmed ready for a future
migration window.

---

## 1. Honcho — MIGRATION ISSUE (resolved)

### Observed evidence

**Compose mounts** (`services/honcho/compose.yml`, and the live project at `/mnt/monarch/appdata/honcho/compose.yml` — identical for this service):

```yaml
  database:
    image: pgvector/pgvector:pg15
    container_name: honcho-postgres
    environment:
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - /mnt/monarch/appdata/honcho/postgres:/var/lib/postgresql/data
```

**Container inspect:** `User=""` (no user override), `Entrypoint=docker-entrypoint.sh`, `Cmd=postgres`,
single bind mount as above, `RestartCount=0` — no restart loop, no mount error.

**Container user vs postgres user:**

| Item | Value |
|---|---|
| Container `Config.User` | empty → entrypoint starts as root, then drops privileges |
| `id postgres` inside `pgvector/pgvector:pg15` | **uid=999 gid=999** |
| Actual postmaster + child process uids | **999** (verified via `/proc/*/status`) |
| Owner of `pgdata` tree at time of failure | **1000:1000**, 1102 files |
| `pgdata` mode | `0700` — so uid 999 had no access at all |

**Read probes (before fix):**

```
uid999_read_exit=1   # postgres user could NOT read global/pg_filenode.map
uid1000_read_exit=0  # only uid 1000 could
```

**Filesystem timestamps (the decisive evidence):**

```
pgdata                          mtime=2026-07-24 14:04:52   ctime=2026-07-30 09:06:33
pgdata/global/pg_filenode.map   mtime=2026-06-20 03:59:09   ctime=2026-07-30 09:06:33
```

mtime unchanged + ctime changed = metadata-only change (ownership), not a data change.

**Logs:** clean checkpoint activity from 2026-06-20 through the last successful start on 2026-07-24
14:04:52 UTC, then 633 `FATAL: could not open file "global/pg_filenode.map": Permission denied`
beginning 09:07:11 UTC on 2026-07-30, plus `could not open file "postmaster.pid": Permission denied`.
`honcho-api` and `honcho-deriver` failed downstream with
`psycopg.OperationalError ... FATAL: could not open file "global/pg_filenode.map"`.

**Existed before migration?** No. PostgreSQL refuses to start on a data directory it does not own
("data directory has wrong ownership"). It started successfully on 2026-07-24, which proves `pgdata`
was owned by uid 999 at that time. Ownership can only have changed between then and the first failure —
and the ctime pins that change to 09:06:33 UTC on 2026-07-30.

### Root cause

The recursive `chown` of `/mnt/monarch/appdata` at 2026-07-30 09:06:33 UTC changed the PostgreSQL data
directory from `999:999` to `1000:1000`. With mode `0700`, the postgres process (uid 999) could no longer
open its own relation map. Not a permissions *mode* problem, not a compose problem, not a PostgreSQL
defect — a pure ownership problem introduced by a migration-support action.

**Confidence: Very high** (timestamp correlation to the second, uid probes, and the PostgreSQL
startup-ownership invariant all agree).

### Fix applied

Ownership-only correction, scoped to the postgres subtree; no content, compose or `.old` changes:

```bash
docker stop honcho-postgres
docker run --rm -v /mnt/monarch/appdata/honcho/postgres:/p debian:12-slim chown -R 999:999 /p
docker start honcho-postgres
docker restart honcho-api honcho-deriver
```

### Verification after fix

```
/p        uid=999 gid=999 mode=755
/p/pgdata uid=999 gid=999 mode=700
1102 files now 999:999

2026-07-30 20:41:23 JST [29] LOG:  redo done at 0/16B0B198
2026-07-30 20:41:23 JST [1]  LOG:  database system is ready to accept connections
```

- `psql -U postgres` succeeds; PostgreSQL 15.18.
- Databases intact: `postgres`, `template0`, `template1`.
- Schema intact: `peers`, `sessions`, `messages`, `documents`, `message_embeddings`, `session_peers`,
  `queue`, `active_queue_sessions`, `webhook_endpoints`, `alembic_version`.
- Extensions intact: `plpgsql 1.0`, **`vector 0.8.3`** (pgvector present).
- Alembic migration head present: `e4eba9cfaa6f`.
- `honcho-api` startup clean, cache connected, `/docs` returns **200**.
- `honcho-deriver` running: `ReconcilerScheduler started with 2 tasks: ['sync_vectors', 'cleanup_queue']`.
- Errors since restart: **0** for postgres, api and deriver.
- Crash recovery replayed a WAL tail cleanly (`invalid record length` at the tail is the normal marker for
  an unclean stop, not corruption).

**Observation for the operator (not a fault):** all application tables are empty (`peers=0 sessions=0
messages=0 documents=0`). File mtimes date to 2026-06-20 and were untouched by the chown, so nothing was
lost today — this instance has simply never stored data. Worth confirming that matches your expectation.

| | |
|---|---|
| **Risk of fix** | Low — ownership only, no writes to data pages |
| **Downtime taken** | ~15 s (service was already 100% unavailable for 2.5 h) |
| **Blocks future migrations?** | No |
| **Classification** | **MIGRATION ISSUE** — resolved, READY FOR SOAK |

---

## 2. Hermes — MIGRATION ISSUE (resolved)

The audit's "pre-existing" suspicion is **disproved** by the evidence.

### Observed evidence

**Which process is uid 10000:** the Hermes application itself. `/etc/passwd` in
`nousresearch/hermes-agent:latest` contains:

```
hermes:x:10000:10000::/opt/data:/bin/sh
```

`HERMES_HOME=/opt/data` and `HERMES_WRITE_SAFE_ROOT=/opt/data` are baked into the image, so uid 10000's
home directory *is* the bind mount. The container starts as root under s6-overlay
(`Entrypoint=/init /opt/hermes/docker/main-wrapper.sh`, `Config.User=root`) and s6 drops the gateway and
dashboard services to uid 10000.

**Expected ownership from the image:** `/opt/data` must be owned by **10000:10000**. The image sets no
PUID/PGID mechanism.

**Does compose specify PUID/PGID?** No. Neither `services/hermes/compose.yml` nor the live
`/mnt/monarch/appdata/hermes/compose.yml` sets `user:`, `PUID` or `PGID`. Only `TZ`, dashboard auth and
`OLLAMA_BASE_URL` are set. So ownership is entirely a filesystem concern.

**Ownership at time of failure:** `/opt/data` = `1000:1000`, mode `0700`, 738 files — uid 10000 had no
access whatsoever.

**Did it exist before migration?** No.

```
/mnt/monarch/appdata/hermes   mtime=2026-07-30 09:06:03   ctime=2026-07-30 09:06:33
PermissionError count by date: 166  — all on 2026-07-30
first PermissionError: 2026-07-30T09:07:03Z  (30 s after the chown)
```

Additionally, files such as `.hermes_history` (Jul 9), `cache/` (Jul 14) and `kanban.db` (Jun 20) were
written *by the app itself*, which runs as uid 10000 — they could only have been created while the tree was
owned by 10000. Hermes also uses the same bind path in its pre-migration compose
(`compose-old.yml` already mounted `/mnt/monarch/appdata/hermes:/opt/data`), so this path was never migrated
in Phase 11 at all.

### Root cause

Same single event: the recursive `chown` at 09:06:33 UTC changed `/opt/data` from `10000:10000` to
`1000:1000`, so the gateway could no longer create `/opt/data/kanban.db.init.lock`, retrying once per
minute. Ownership problem, migration-induced.

**Confidence: Very high.**

### Fix applied

```bash
docker stop hermes
docker run --rm -v /mnt/monarch/appdata/hermes:/h debian:12-slim chown -R 10000:10000 /h
docker start hermes
```

### Verification after fix

```
/h                      uid=10000 gid=10000 mode=700
/h/kanban.db.init.lock  uid=10000 gid=10000 mode=644
738 files now 10000:10000
uid10000_write_ok           # write probe as the real app user succeeds
```

- Gateway starts clean under s6: `HERMES_DASHBOARD_READY port=9119`, `Hermes Web UI → http://0.0.0.0:9119`.
- `PermissionError` count strictly after `StartedAt=2026-07-30T11:42:27Z`: **0** (last occurrence 11:42:14Z,
  before the restart).
- HTTPS via Traefik: `https://hermes.fatherfankscloud.uk/` → **302** (dashboard auth redirect, expected).
- `RestartCount=0`, status running.
- Remaining log warnings are configuration choices, not faults: `No user allowlists configured` and
  `No messaging platforms enabled`.

| | |
|---|---|
| **Risk of fix** | Low — ownership only, within the app's own home directory |
| **Downtime taken** | ~20 s (service had been erroring for 2.5 h) |
| **Blocks future migrations?** | No |
| **Classification** | **MIGRATION ISSUE** — resolved, READY FOR SOAK |

---

## 3. n8n — PASS (downgraded from WARNING)

### Observed evidence

**Is routing actually broken?** No — **there is no Traefik route for n8n, by design.**

- Neither `services/n8n/compose.yml` nor the live `/mnt/monarch/appdata/n8n/compose.yml` contains a single
  `traefik.*` label. `grep traefik` on the live compose returns nothing.
- Traefik agrees and says so explicitly:
  `Filtering disabled container container=n8n-n8n-3fb4f21ab7fb...` — a container without
  `traefik.enable=true` is skipped.
- n8n is attached to `homelab` and `ai-assistant` networks only — **not** the `proxy` network Traefik uses.
- n8n is configured for plain LAN access: `N8N_HOST=mocha`, `N8N_PROTOCOL=http`, `N8N_SECURE_COOKIE=false`,
  published port `5678:5678`.

**Are labels correct / duplicate routers / stale configuration?** No labels exist, therefore no duplicate
routers and no stale n8n router. Nothing to correct.

**Is HTTPS functioning?** There is no HTTPS vhost for n8n. The audit's "timeout" was a **DNS** artefact,
not Traefik:

```
n8n.fatherfankscloud.uk     -> 0.0.0.9      (blackholed)
honcho.fatherfankscloud.uk  -> 0.0.0.9      (blackholed)
home.fatherfankscloud.uk    -> 192.168.50.44
chat.fatherfankscloud.uk    -> 192.168.50.44
```

`0.0.0.9` is a DNS-level block/placeholder answer, so `curl` hung until timeout. That is upstream DNS
behaviour, entirely unrelated to the migration. (It also explains the Honcho "Traefik timeout" recorded in
the audit.)

**Can workflows load?**

- `PRAGMA integrity_check` on `/mnt/monarch/appdata/n8n/database.sqlite` → **ok**
- `select count(*) from workflow_entity` → **4 workflows**, all currently inactive (`active=0`)
- Config, credentials, `nodes/`, `storage/` and event logs all present in appdata

Note: the `workflows/` and `reports/` bind directories are empty on both host and container — they are
export/scratch mounts, not where n8n stores workflows. Workflows live in `database.sqlite`. The earlier
audit's "17 JSON files" claim did not hold up; the authoritative count is 4 workflows in the database.

**Can login succeed?**

- `http://127.0.0.1:5678/` → **200**
- `/rest/login` → **401** unauthenticated (endpoint alive and enforcing auth)
- `/rest/workflows` → **401** unauthenticated (correct)
- `/rest/settings` → `userManagement: {authenticationMethod: 'email', showSetupOnFirstLoad: False}` — the
  owner account exists and setup is complete, so login is available

**Permissions:** n8n runs as `node` (uid 1000) and its appdata is `1000:1000`, so the 09:06:33 chown was a
no-op for this service. Zero `permission denied` / `EACCES` entries in 24 h of logs.

### Root cause

No fault. The WARNING came from probing an HTTPS hostname that was never configured, over a DNS record that
returns `0.0.0.9`.

**Confidence: High.**

### Recommended action (optional, not applied)

Two non-blocking observations, both pre-existing and unrelated to data placement:

1. n8n is still run from the legacy live project file `/mnt/monarch/appdata/n8n/compose.yml`
   (`com.docker.compose.project.config_files`), not the repo copy. Its data paths are already correct
   appdata paths, so nothing is at risk; the repo version merely adds `env_file`, a healthcheck, log
   rotation and a memory limit. Adopting the repo file requires a container recreate — schedule with the
   other compose-ownership alignments.
2. If HTTPS access to n8n is actually wanted, that is a **new feature**, not a repair: add `traefik.enable`
   labels, join the `proxy` network, set `N8N_HOST`/`WEBHOOK_URL` to the public hostname, re-enable
   `N8N_SECURE_COOKIE`, and fix the `0.0.0.9` DNS record.

| | |
|---|---|
| **Risk** | None outstanding |
| **Downtime** | 0 (nothing applied) |
| **Blocks future migrations?** | No |
| **Classification** | **PASS** |

---

## 4. Homepage Images — PASS (downgraded from WARNING)

### Observed evidence

**Was the image directory migrated correctly?** Yes — and there was nothing to move. **Both sides are
empty and always were.**

```
source      /hive/data/homepage/images   files=0   (root:root, mtime Jan 23 2026)
destination /mnt/monarch/appdata/homepage/images   files=0   bytes=0
```

Inspected as root via a container to rule out a permission-masked listing: `/hive/data/homepage` contains
only the empty `images/` directory (whole tree = 0 files). The outstanding `sudo mv ... images images.old`
noted in the Homepage migration report is therefore **unnecessary** — there is no data at risk on either
side.

**Does compose point at the correct location?** Yes.

```9:10:services/homepage/compose.yaml
      - ${PATH_CONFIG}/homepage:/app/config
      - ${PATH_DATA}/homepage/images:/app/public/images
```

Resolved live container mounts confirm both:

```
/mnt/monarch/appdata/homepage        -> /app/config      rw
/mnt/monarch/appdata/homepage/images -> /app/public/images rw
```

**Is the symlink correct?** Yes.

```
services/homepage/.env -> ../.env      (symlink, valid)
services/.env:  PATH_CONFIG=/mnt/monarch/appdata
                PATH_DATA=/mnt/monarch/appdata
```

Interpolation resolves to appdata, which matches the running container's actual mounts — so the symlink is
doing its job.

**Do images actually load?** There are no images to load, and none are requested:

- Homepage config (`settings.yaml`, `kubernetes.yaml`) contains **zero** `/images/...` references.
- The rendered dashboard at `https://home.fatherfankscloud.uk/` returns **200**, 46,201 bytes, with 12
  service entries and a Bookmarks section — and **0** `/images/` references in the HTML.
- Container is `healthy`, logs clean, `/app/public/images` mounts correctly (empty, owned `node`).

Service icons are resolved from Homepage's built-in/CDN icon set, not from `/app/public/images`. That
directory only matters if you add custom local images later — at which point the mount is already correct
and writable.

### Root cause

No fault. The WARNING was raised for an empty directory that never contained data.

**Confidence: High.**

### Recommended action

None required. Optionally clean up the stray empty root-owned `/hive/data/homepage/` tree during a later
maintenance pass — deliberately **not** done here (out of scope for this pass).

| | |
|---|---|
| **Risk** | None |
| **Downtime** | 0 |
| **Blocks future migrations?** | No |
| **Classification** | **PASS** |

---

## 5. Ollama — DEFERRED (verified ready)

Not migrated, as instructed. Verification only.

### Current configuration

| Item | Value |
|---|---|
| Image | `ollama/ollama:latest` |
| Bind mount (live) | `/hive/ollama` → `/root/.ollama` — still on legacy storage, as expected |
| Compose project file in use | `/hive/ollama/compose.yml` (legacy live project) |
| Repo compose | `services/ollama/compose.yaml` — still references `/hive/ollama`, so it needs a path update before migration |
| Tuning env | `OLLAMA_KV_CACHE_TYPE=q8_0`, `OLLAMA_CONTEXT_LENGTH=2048`, `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_NUM_PARALLEL=1` |
| Container status | Up 5 days, logs clean, no permission errors |
| Runtime user | root (so the appdata chown pattern poses no risk to this service) |

### Current models

`ollama list` succeeds and returns **17 entries: 12 local + 5 cloud-hosted** (cloud entries show size `-`
and consume no local storage).

| Local model | Size |
|---|---|
| `devstral-small-2:latest` | 15 GB |
| `qwen3:14b` | 9.3 GB |
| `nsheth/llama-3-lumimaid-8b-v0.1-iq-imatrix:latest` | 5.5 GB |
| `qwen3:8b` | 5.2 GB |
| `dimweb/sfr-llama3-8b:latest` | 4.9 GB |
| `llama3.1:latest` | 4.9 GB |
| `qwen2.5-coder:7b` | 4.7 GB |
| `qwen2.5:7b` | 4.7 GB |
| `deepseek-r1:7b` | 4.7 GB |
| `qwen3:4b` | 2.5 GB |
| `qwen2.5:3b` | 1.9 GB |
| `nomic-embed-text:latest` | 274 MB |

Cloud (no local data): `gpt-oss:120b-cloud`, `qwen3-coder:480b-cloud`, `qwen3.5:397b-cloud`,
`qwen3.5:cloud`, `deepseek-v4-pro:cloud`.

### Expected migration size and free space

| Metric | Value |
|---|---|
| Source tree `/hive/ollama` | **68,737,096,851 B ≈ 64.0 GiB** |
| Object count | 76 files, 22 directories (large immutable blobs — ideal for rsync) |
| `/mnt/monarch` capacity | 1.9 TB total, 4.8 GB used, **1.99 TB free** |
| Free space after migration | ~1.92 TB (~3.5 % used) |
| Headroom verdict | **Ample** — required 64 GiB is ~3.4 % of available space |

### Readiness assessment — READY for a future window

Favourable factors: model blobs are content-addressed and immutable, so the bulk copy can be done live and
finished with a short delta sync; the service runs as root so no uid remapping is needed; logs are clean.

Pre-migration requirements to plan for:

1. Update `services/ollama/compose.yaml` to `/mnt/monarch/appdata/ollama:/root/.ollama` (or `${PATH_DATA}`).
2. **Blast radius:** `services/ollama/compose.yaml` also defines **`open-webui`**, whose data is already on
   appdata. Applying the file will recreate Open WebUI too — plan for both, or split the file first.
3. Ollama is currently owned by the legacy project `/hive/ollama/compose.yml`; adopting the repo file is a
   project-ownership change, so the old project should be stopped rather than left running in parallel.
4. Dependent services to re-verify afterwards: `open-webui`, `hermes` (`OLLAMA_BASE_URL=http://ollama:11434`),
   and the `ollama_ollama-net` network name that other stacks reference externally.
5. Estimated downtime: ~2–5 minutes if pre-synced (delta + restart); ~10–20 minutes for a cold 64 GiB copy.

| | |
|---|---|
| **Risk** | Medium — large dataset plus shared compose file with Open WebUI |
| **Downtime** | 2–5 min with pre-sync |
| **Blocks future migrations?** | No — it *is* the future migration |
| **Classification** | **DEFERRED** (verified ready) |

---

## Cross-cutting finding: scope of the 09:06:33 chown

A full sweep of every running container's appdata bind mounts against its runtime uid confirms no other
service is affected:

| Service | Runtime uid | Data owner | Verdict |
|---|---|---|---|
| honcho-postgres | 999 | 999 (restored) | fixed |
| hermes | 10000 | 10000 (restored) | fixed |
| n8n | 1000 (`node`) | 1000 | ok |
| authentik-db / redis / worker | root | 70 / 999 / mixed | ok — Authentik was re-copied *after* the chown with a root-preserving rsync, so uid 70 survived (3,118 files still `70`) |
| authentik-server | 1000 | 1000 (media) | ok, healthy |
| portainer, beszel, beszel-agent | root (distroless) | 1000 | ok |
| homepage, code-server, calibre, calibre-web, open-webui, traefik, honcho-redis | root | 1000 | ok |
| kavita, odysseus (4 containers) | root | 1000 | ok — checked explicitly, 0 permission errors in logs |

Latent-risk check: the only services that were *not* restarted since the chown (Odysseus stack, Kavita,
n8n, Open WebUI, Beszel) all run as root or uid 1000, so a future restart will not surprise you.

---

## Updated Status Table

| # | Issue | Previous status | **Classification** | Recommendation |
|---|---|---|---|---|
| 1 | **Honcho** | FAIL / SOAK FAILED | **MIGRATION ISSUE** — resolved | READY FOR SOAK |
| 2 | **Hermes** | FAIL / suspected pre-existing | **MIGRATION ISSUE** — resolved | READY FOR SOAK |
| 3 | **n8n** | WARNING | **PASS** | READY FOR SOAK |
| 4 | **Homepage Images** | WARNING | **PASS** | READY FOR SOAK |
| 5 | **Ollama** | FAIL / DEFERRED | **DEFERRED** (verified ready) | Migrate in a future window |

Counts: **PASS 2** · **WARNING 0** · **PRE-EXISTING ISSUE 0** · **MIGRATION ISSUE 2 (both resolved)** ·
**BLOCKED 0** · **DEFERRED 1**

No issue in this pass remains unresolved or blocking.

---

## Recommended Next Actions

**Do now (operator, 1 minute):**

1. **Never run a bare recursive chown on `/mnt/monarch/appdata` again.** Scope it to the single service
   directory being migrated. The correct unblock for a non-writable destination is
   `sudo install -d -o fatherfrank -g fatherfrank /mnt/monarch/appdata/<service>`, not a tree-wide chown.
   Consider adding a pre-flight ownership snapshot (`find <dir> -printf '%U:%G %p\n' > ownership.txt`) to
   the migration framework so any future ownership drift is instantly diffable.

**Do soon (short maintenance window):**

2. Confirm Honcho's empty application tables are expected (schema and pgvector are intact; nothing was lost
   today, but the instance holds no data).
3. Fix the DNS records returning `0.0.0.9` for `n8n.fatherfankscloud.uk` and `honcho.fatherfankscloud.uk`,
   or remove those hostnames if they are intentionally not published. This eliminates the false "routing
   broken" signal from future audits.
4. Align compose ownership for services still driven by legacy live project files — **Traefik**, **n8n**,
   **Ollama**, **Honcho** — onto the repo under `services/`. Each requires a container recreate; Traefik has
   the largest blast radius and should go last, alone.
5. Add a Portainer healthcheck compatible with its distroless image, or remove the healthcheck, so
   Portainer stops reporting `unhealthy` while functioning normally.

**Before any `.old` directory can be removed — remaining actions:**

| # | Action | Applies to |
|---|---|---|
| 1 | Complete the 7-day soak with no regressions (soak restarts from **2026-07-30** for Honcho and Hermes, since they were only just restored) | all Batch 01–04 services |
| 2 | Confirm the backup system now includes `/mnt/monarch/appdata` and has produced at least one successful post-migration backup | all |
| 3 | Verify `code-server` drift is benign — appdata has diverged from `code-server.old` through normal container writes since restart; confirm extensions/workspace state are correct | code-server |
| 4 | Re-verify Authentik after a full restart cycle (uid 70 data survived the chown; confirm the Python healthcheck fix holds) | authentik |
| 5 | Confirm Calibre's mode-`000` `qtshadercache` files are non-essential (they are a regenerable Qt cache) | calibre |
| 6 | No `.old` exists for Honcho, Hermes, n8n, Open WebUI, Beszel or Traefik — they were already on appdata, so there is nothing to clean up for them | — |
| 7 | Ollama must be migrated before `/hive/ollama` (64 GiB) can be considered | ollama |
| 8 | Leave the empty root-owned `/hive/data/homepage/` tree until the Homepage soak completes, then remove it as ordinary cleanup | homepage |

Cleanup itself remains **out of scope** and must not be performed before the soak period ends.

---

## Commands Executed (evidence and remediation)

Read-only investigation (abbreviated):

```bash
docker inspect honcho-postgres --format '{{json .Mounts}}'
docker exec honcho-postgres sh -c 'id postgres; ls -lan /var/lib/postgresql/data/pgdata'
docker exec -u 999 honcho-postgres cat /var/lib/postgresql/data/pgdata/global/pg_filenode.map
stat -c '%n uid=%u gid=%g mode=%a mtime=%y ctime=%z' <appdata paths>
docker logs -t honcho-postgres | grep 'Permission denied' | awk '{print substr($1,1,10)}' | sort | uniq -c
docker logs -t hermes      | grep 'PermissionError' | awk '{print substr($1,1,10)}' | sort | uniq -c
docker exec hermes sh -c 'grep hermes /etc/passwd; ls -lan /opt/data'
docker logs traefik | grep -i n8n
getent hosts n8n.fatherfankscloud.uk home.fatherfankscloud.uk
sqlite3 database.sqlite 'select count(*) from workflow_entity; PRAGMA integrity_check;'
docker run --rm -v /hive/data/homepage:/s:ro alpine:3.20 find /s/images -type f | wc -l
docker exec ollama ollama list ; df -B1 /mnt/monarch /hive
```

Remediation (ownership only, scoped):

```bash
# Honcho — 11:41 UTC
docker stop honcho-postgres
docker run --rm -v /mnt/monarch/appdata/honcho/postgres:/p debian:12-slim chown -R 999:999 /p
docker start honcho-postgres
docker restart honcho-api honcho-deriver

# Hermes — 11:42 UTC
docker stop hermes
docker run --rm -v /mnt/monarch/appdata/hermes:/h debian:12-slim chown -R 10000:10000 /h
docker start hermes
```

## Timestamps (UTC)

| Time | Event |
|---|---|
| 2026-06-20 03:59 | Honcho pgdata created (uid 999) |
| 2026-07-24 14:04:52 | Last healthy Honcho PostgreSQL start — proves uid 999 ownership |
| 2026-07-30 09:06:33 | **Recursive chown of `/mnt/monarch/appdata` → 1000:1000** (root cause) |
| 2026-07-30 09:07:03 | Hermes first `PermissionError` |
| 2026-07-30 09:07:11 | Honcho first `pg_filenode.map` failure |
| 2026-07-30 11:41:21 | Honcho postgres ownership restored, container started, DB recovered |
| 2026-07-30 11:41:46 / 11:41:56 | `honcho-api` / `honcho-deriver` restarted clean |
| 2026-07-30 11:42:27 | Hermes ownership restored, container started clean |
| 2026-07-30 11:43+ | Post-fix verification: 0 errors across all four containers |

## Lessons Learned

1. **A tree-wide `chown` is a service-breaking operation, not a convenience.** One command intended to
   unblock a single directory silently broke two unrelated services 30 seconds later and cost the project a
   false "SOAK FAILED" verdict on each.
2. **ctime is the forensic tool for ownership incidents.** mtime unchanged + ctime changed uniformly across
   unrelated services was conclusive proof of a single metadata operation, and pinned it to the second.
3. **PostgreSQL's startup ownership check is a free timestamped witness.** A successful
   `ready to accept connections` message is proof that the data directory was correctly owned at that
   moment — which is what disproved the "pre-existing" theory.
4. **"Pre-existing" must be proven, not assumed.** Both services were initially classified as pre-existing
   faults; per-date error counts (zero before the incident day) overturned both.
5. **Absence of a Traefik route is not a broken route.** Probing a hostname that was never configured — over
   a DNS record answering `0.0.0.9` — produced two spurious FAIL/WARNING findings. Future audits should
   check for `traefik.enable` labels and proxy-network membership before probing HTTPS.
6. **Verify a warning has a subject before escalating it.** The Homepage images warning concerned a
   directory that has been empty since January.
7. **Root-preserving copies pay off.** Authentik's uid 70 PostgreSQL data survived the incident precisely
   because it was re-copied with a root rsync *after* the chown — the technique that protected it is the one
   to standardise on.
