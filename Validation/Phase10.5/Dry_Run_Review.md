# Phase 10.5 Dry-Run Review

Generated: 2026-07-30T00:14:18Z on mocha

Mode: `--dry-run` only. No data copied. No compose applied. No containers stopped.

## Script syntax

```
OK scripts/migration/lib/common.sh
OK scripts/migration/compose-path-check.sh
OK scripts/migration/copy-config.sh
OK scripts/migration/inventory.sh
OK scripts/migration/preflight.sh
OK scripts/migration/rollback.sh
OK scripts/migration/run-migration.sh
OK scripts/migration/update-compose.sh
OK scripts/migration/verify-destination.sh
OK scripts/migration/verify-service.sh
```

## services.conf

```
# Phase 10.5 services.conf — declarative migration map (mocha personal homelab)
# Format (pipe-delimited):
# key|compose_relpath|container_names|source_config|target_config|keep_hive|risk|order|migration_required|already_migrated|notes
# - source_config/target_config may be empty when N/A
# - keep_hive: comma-separated paths that MUST stay on /hive
# - migration_required: yes|no|verify|deferred
# - already_migrated: yes|no|partial
# - Folder services/authentic/ is keyed as authentik (correct spelling)
#
# ORDER waves: 10=low, 20=medium, 30=higher, 40=final, 90=out-of-scope/stay, 99=untracked

code-server|services/code-server/compose.yml|code-server|/hive/code-server/config|/mnt/monarch/appdata/code-server|/hive|low|10|yes|no|Config only; keep /hive and /mnt/monarch/appdata workspace RO mounts
homepage|services/homepage/compose.yaml|homepage||/mnt/monarch/appdata/homepage||low|11|verify|partial|Uses PATH_CONFIG/PATH_DATA; verify live dirs under appdata
traefik|services/traefik/compose.yaml|traefik||/mnt/monarch/appdata/traefik||low|12|verify|partial|acme.json via PATH_CONFIG; high blast radius; small data
beszel|services/beszel/compose.yml|beszel||/mnt/monarch/appdata/beszel||low|13|no|yes|Already on /mnt/monarch/appdata/beszel/beszel_data
portainer|services/portainer/compose.yaml|portainer|/hive/portainer|/mnt/monarch/appdata/portainer||low|14|yes|no|Config/state under /data mount
authentik|services/authentic/compose.yaml|authentik-db,authentik-redis,authentik-server,authentik-worker||/mnt/monarch/appdata/authentik||medium|20|verify|partial|PATH_DATA/authentik/*; compose dir still named authentic
honcho|services/honcho/compose.yml|honcho-api,honcho-deriver,honcho-postgres,honcho-redis||/mnt/monarch/appdata/honcho||medium|21|no|yes|postgres+redis already on appdata
hermes|services/hermes/compose.yml|hermes||/mnt/monarch/appdata/hermes||medium|22|no|yes|Already on appdata
n8n|services/n8n/compose.yml|n8n||/mnt/monarch/appdata/n8n||medium|23|no|yes|Already on appdata
open-webui|services/ollama/compose.yml|open-webui||/mnt/monarch/appdata/open-webui||medium|24|no|yes|Shares compose with ollama; already on appdata
ollama|services/ollama/compose.yml|ollama|/hive/ollama|/mnt/monarch/appdata/ollama||higher|30|yes|no|INTENTIONAL EXCEPTION: migrate config+models to appdata (largest model ~8B). Relocatable later via services.conf source/target swap if SSD capacity requires returning models to /hive
calibre|services/calibre-web/compose.yml|calibre|/hive/calibre/config|/mnt/monarch/appdata/calibre|/hive/library|higher|31|yes|no|Same compose as calibre-web; books stay on /hive/library
calibre-web|services/calibre-web/compose.yml|calibre-web|/hive/calibre-web/config|/mnt/monarch/appdata/calibre-web|/hive/library|higher|32|yes|no|Books stay on /hive/library
jellyfin|services/jellyfin/compose.yml|jellyfin|/hive/jellyfin/config|/mnt/monarch/appdata/jellyfin|/hive/jellyfin/tv,/hive/jellyfin/movie|final|40|yes|no|Config only; media stays on /hive
nzbget|services/NZBget/compose.yml|nzbget|/hive/NZBget/config|/mnt/monarch/appdata/nzbget|/hive/downloads|final|41|yes|no|Config only; downloads stay on /hive
hotio|services/Hotio/compose.yml|qbittorrent|/hive/Hotio/config|/mnt/monarch/appdata/hotio|/hive/downloads/completed|final|42|yes|no|Config only; downloads stay; related media stack
beszel-agent|services/beszel_agent/compose.yml|beszel-agent|||./beszel_agent_data|low|15|deferred|no|Relative path; host-system docker.sock — classify before migrate
echoos|services/EchoOS/compose.yaml|logseq-web|/hive/echoos||/hive/echoos|higher|35|deferred|no|Graph data on /hive; classify config vs dataset before any move
cosmoos|services/CosmoOS/compose.yaml|cosmos-server|||/var/lib/cosmos|higher|36|no|n/a|Host /var/lib/cosmos + whole-root mount — out of /hive→appdata scope
odysseus|services/odysseus/docker-compose.yml|odysseus|||./data|medium|25|deferred|partial|Relative ./data; whole /hive and /mnt/monarch mounts for tooling — not a config move
```

## Inventory (all services)

```
========================================
Service:          code-server
Compose:          services/code-server/compose.yml
Containers:       code-server
Source config:    /hive/code-server/config
Target config:    /mnt/monarch/appdata/code-server
Keep on /hive:    /hive
Risk / order:     low / 10
Migration req:    yes
Already migrated: no
Notes:            Config only; keep /hive and /mnt/monarch/appdata workspace RO mounts
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/code-server/config:/config
      - /hive:/config/workspace/hive:ro
      - /mnt/monarch/appdata:/config/workspcae/monarch:ro
Source stats: bytes=3200369128 files=41259 dirs=6885 (3.0GB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json

========================================
Service:          homepage
Compose:          services/homepage/compose.yaml
Containers:       homepage
Source config:    (none)
Target config:    /mnt/monarch/appdata/homepage
Keep on /hive:    (none)
Risk / order:     low / 11
Migration req:    verify
Already migrated: partial
Notes:            Uses PATH_CONFIG/PATH_DATA; verify live dirs under appdata
----------------------------------------
Compose bind mounts (raw lines):
      - ../.env
      - ${PATH_CONFIG}/homepage:/app/config
      - ${PATH_DATA}/homepage/images:/app/public/images
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-homepage.json

========================================
Service:          traefik
Compose:          services/traefik/compose.yaml
Containers:       traefik
Source config:    (none)
Target config:    /mnt/monarch/appdata/traefik
Keep on /hive:    (none)
Risk / order:     low / 12
Migration req:    verify
Already migrated: partial
Notes:            acme.json via PATH_CONFIG; high blast radius; small data
----------------------------------------
Compose bind mounts (raw lines):
      - "80:80"
      - "443:443"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ${PATH_CONFIG}/traefik/acme.json:/etc/traefik/acme.json
      - /etc/localtime:/etc/localtime:ro
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-traefik.json

========================================
Service:          beszel
Compose:          services/beszel/compose.yml
Containers:       beszel
Source config:    (none)
Target config:    /mnt/monarch/appdata/beszel
Keep on /hive:    (none)
Risk / order:     low / 13
Migration req:    no
Already migrated: yes
Notes:            Already on /mnt/monarch/appdata/beszel/beszel_data
----------------------------------------
Compose bind mounts (raw lines):
      - "8090:8090"
      - APP_URL=http://mocha:8090
      - /mnt/monarch/appdata/beszel/beszel_data:/beszel_data
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json

========================================
Service:          portainer
Compose:          services/portainer/compose.yaml
Containers:       portainer
Source config:    /hive/portainer
Target config:    /mnt/monarch/appdata/portainer
Keep on /hive:    (none)
Risk / order:     low / 14
Migration req:    yes
Already migrated: no
Notes:            Config/state under /data mount
----------------------------------------
Compose bind mounts (raw lines):
      - /var/run/docker.sock:/var/run/docker.sock
      - /hive/portainer:/data
      - 9000:9000
      - 9445:9443
```

## Compose path check

```
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

## Compose path check detail

# Compose path check (runtime)

Generated: 2026-07-30T00:14:18Z

## services/authentic/compose.yaml
- mount host: `${PATH_DATA}/authentik/db`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/authentik/redis`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/authentik/media`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/authentik/templates`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `/var/run/docker.sock`
  - INFO host-system mount
- mount host: `${PATH_DATA}/authentik/media`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/authentik/templates`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/authentik/certs`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)

## services/beszel_agent/compose.yml
- mount host: `/var/run/docker.sock`
  - WARN duplicate host path also in services/authentic/compose.yaml
  - INFO host-system mount
- mount host: `./beszel_agent_data`
  - INFO relative path

## services/beszel/compose.yml
- mount host: `/mnt/monarch/appdata/beszel/beszel_data`
  - INFO appdata path

## services/calibre-web/compose.yml
- mount host: `/hive/calibre/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive/library/Kavita/fanfic/novelas`
  - OK keep-on-hive dataset
- mount host: `/hive/library/Kavita/browser_cache`
  - OK keep-on-hive dataset
- mount host: `/hive/calibre-web/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive/library/Kavita/fanfic/novelas`
  - OK keep-on-hive dataset

## services/code-server/compose.yml
- mount host: `/hive/code-server/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive`
  - WARN whole-pool mount (tooling) — do not treat as migratable config
- mount host: `/mnt/monarch/appdata`
  - WARN unsupported/unknown host path

## services/CosmoOS/compose.yaml
- mount host: `/var/run/docker.sock`
  - WARN duplicate host path also in services/authentic/compose.yaml
  - INFO host-system mount
- mount host: `/var/run/dbus/system_bus_socket`
  - INFO host-system mount
- mount host: `/`
  - INFO host-system mount
- mount host: `/var/lib/cosmos`
  - INFO host-system mount

## services/EchoOS/compose.yaml
- mount host: `/hive/echoos`
  - OK keep-on-hive dataset

## services/hermes/compose.yml
- mount host: `/mnt/monarch/appdata/hermes`
  - INFO appdata path

## services/homepage/compose.yaml
- mount host: `${PATH_CONFIG}/homepage`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `${PATH_DATA}/homepage/images`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)

## services/honcho/compose.yml
- mount host: `/mnt/monarch/appdata/honcho/postgres`
  - INFO appdata path
- mount host: `/mnt/monarch/appdata/honcho/redis`
  - INFO appdata path

## services/Hotio/compose.yml
- mount host: `/hive/Hotio/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive/downloads/completed`
  - OK keep-on-hive dataset

## services/jellyfin/compose.yml
- mount host: `/dev/dri`
  - INFO host-system mount
- mount host: `/hive/jellyfin/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive/jellyfin/tv`
  - OK keep-on-hive dataset
- mount host: `/hive/jellyfin/movie`
  - OK keep-on-hive dataset

## services/n8n/compose.yml
- mount host: `/mnt/monarch/appdata/n8n`
  - INFO appdata path
- mount host: `/mnt/monarch/appdata/n8n/workflows`
  - INFO appdata path
- mount host: `/mnt/monarch/appdata/n8n/reports`
  - INFO appdata path

## services/NZBget/compose.yml
- mount host: `/hive/NZBget/config`
  - INFO legacy /hive path (candidate or keep)
- mount host: `/hive/downloads`
  - OK keep-on-hive dataset

## services/odysseus/docker-compose.yml
- mount host: `./data`
  - INFO relative path
- mount host: `./logs`
  - INFO relative path
- mount host: `./data/ssh`
  - INFO relative path
- mount host: `./data/huggingface`
  - INFO relative path
- mount host: `./data/local`
  - INFO relative path
- mount host: `/hive`
  - WARN duplicate host path also in services/code-server/compose.yml
  - WARN whole-pool mount (tooling) — do not treat as migratable config
- mount host: `/mnt/monarch`
  - WARN whole-pool mount (tooling) — do not treat as migratable config
- mount host: `./config/searxng/settings.yml`
  - INFO relative path

## services/ollama/compose.yml
- mount host: `/hive/ollama`
  - INFO legacy ollama path (migrate config+models → /mnt/monarch/appdata/ollama)
- mount host: `/mnt/monarch/appdata/open-webui`
  - INFO appdata path

## services/portainer/compose.yaml
- mount host: `/var/run/docker.sock`
  - WARN duplicate host path also in services/authentic/compose.yaml
  - INFO host-system mount
- mount host: `/hive/portainer`
  - INFO legacy /hive path (candidate or keep)

## services/traefik/compose.yaml
- mount host: `/var/run/docker.sock`
  - WARN duplicate host path also in services/authentic/compose.yaml
  - INFO host-system mount
- mount host: `${PATH_CONFIG}/traefik/acme.json`
  - INFO env-interpolated PATH_* (expect /mnt/monarch/appdata)
- mount host: `/etc/localtime`
  - INFO host-system mount

## Summary

- WARN=9
- FAIL=0

## Dry-run migrations

### code-server

```
INFO: === run-migration service=code-server execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/code-server/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/code-server/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/code-server
INFO: OK: free space 1.9TB >= need ~3.4GB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=code-server
INFO: ---- Inventory ----
========================================
Service:          code-server
Compose:          services/code-server/compose.yml
Containers:       code-server
Source config:    /hive/code-server/config
Target config:    /mnt/monarch/appdata/code-server
Keep on /hive:    /hive
Risk / order:     low / 10
Migration req:    yes
Already migrated: no
Notes:            Config only; keep /hive and /mnt/monarch/appdata workspace RO mounts
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/code-server/config:/config
      - /hive:/config/workspace/hive:ro
      - /mnt/monarch/appdata:/config/workspcae/monarch:ro
Source stats: bytes=3200369128 files=41259 dirs=6885 (3.0GB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/code-server && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/code-server (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for code-server → /mnt/monarch/appdata/code-server
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/code-server-code-server-20260730T001419Z.json
INFO: [dry-run] would stop containers: code-server
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/code-server/config/ → /mnt/monarch/appdata/code-server/

Number of files: 48,149 (reg: 41,259, dir: 6,885, link: 4, special: 1)
Number of created files: 48,149 (reg: 41,259, dir: 6,885, link: 4, special: 1)
Number of deleted files: 0
Number of regular files transferred: 41,256
Total file size: 3,200,308,712 bytes
Total transferred file size: 3,200,307,177 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 65,534
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 1,662,915
Total bytes received: 152,109

sent 1,662,915 bytes  received 152,109 bytes  1,210,016.00 bytes/sec
total size is 3,200,308,712  speedup is 1,763.23 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/code-server/config → /mnt/monarch/appdata/code-server
INFO: Validating CURRENT compose: services/code-server/compose.yml
time="2026-07-30T00:14:20Z" level=warning msg="The \"PASSWORD\" variable is not set. Defaulting to a blank string."
env file /home/fatherfrank/projects/homelab/services/code-server/.env not found: stat /home/fatherfrank/projects/homelab/services/code-server/.env: no such file or directory
WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
INFO: Validating PROPOSED compose
time="2026-07-30T00:14:20Z" level=warning msg="The \"PASSWORD\" variable is not set. Defaulting to a blank string."
env file /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/.env not found: stat /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/.env: no such file or directory
WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/code-server/compose.yml
INFO: Finished code-server → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-code-server.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] code-server
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### homepage

```
INFO: === run-migration service=homepage execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/homepage/compose.yaml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/homepage
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=homepage
INFO: ---- Inventory ----
========================================
Service:          homepage
Compose:          services/homepage/compose.yaml
Containers:       homepage
Source config:    (none)
Target config:    /mnt/monarch/appdata/homepage
Keep on /hive:    (none)
Risk / order:     low / 11
Migration req:    verify
Already migrated: partial
Notes:            Uses PATH_CONFIG/PATH_DATA; verify live dirs under appdata
----------------------------------------
Compose bind mounts (raw lines):
      - ../.env
      - ${PATH_CONFIG}/homepage:/app/config
      - ${PATH_DATA}/homepage/images:/app/public/images
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-homepage.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/homepage && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/homepage (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for homepage → /mnt/monarch/appdata/homepage
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/homepage-homepage-20260730T001420Z.json
INFO: [dry-run] would stop containers: homepage
INFO: [dry-run] would start compose project services/homepage/compose.yaml
INFO: Finished homepage → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-homepage.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] homepage
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### traefik

```
INFO: === run-migration service=traefik execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/traefik/compose.yaml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
WARN: destination non-empty: /mnt/monarch/appdata/traefik
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=3 service=traefik
INFO: ---- Inventory ----
========================================
Service:          traefik
Compose:          services/traefik/compose.yaml
Containers:       traefik
Source config:    (none)
Target config:    /mnt/monarch/appdata/traefik
Keep on /hive:    (none)
Risk / order:     low / 12
Migration req:    verify
Already migrated: partial
Notes:            acme.json via PATH_CONFIG; high blast radius; small data
----------------------------------------
Compose bind mounts (raw lines):
      - "80:80"
      - "443:443"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ${PATH_CONFIG}/traefik/acme.json:/etc/traefik/acme.json
      - /etc/localtime:/etc/localtime:ro
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-traefik.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/traefik && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/traefik (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
WARN: Destination non-empty
INFO: Destination verification OK for traefik → /mnt/monarch/appdata/traefik
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/traefik-traefik-20260730T001420Z.json
INFO: [dry-run] would stop containers: traefik
INFO: [dry-run] would start compose project services/traefik/compose.yaml
INFO: Finished traefik → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-traefik.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] traefik
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### beszel

```
INFO: === run-migration service=beszel execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/beszel/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/beszel
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=beszel
INFO: ---- Inventory ----
========================================
Service:          beszel
Compose:          services/beszel/compose.yml
Containers:       beszel
Source config:    (none)
Target config:    /mnt/monarch/appdata/beszel
Keep on /hive:    (none)
Risk / order:     low / 13
Migration req:    no
Already migrated: yes
Notes:            Already on /mnt/monarch/appdata/beszel/beszel_data
----------------------------------------
Compose bind mounts (raw lines):
      - "8090:8090"
      - APP_URL=http://mocha:8090
      - /mnt/monarch/appdata/beszel/beszel_data:/beszel_data
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json
INFO: Service already on appdata — path check only
INFO: ---- Compose path check ----
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

### portainer

```
INFO: === run-migration service=portainer execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/portainer/compose.yaml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/portainer
(exit 1)
```

### authentik

```
INFO: === run-migration service=authentik execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/authentic/compose.yaml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/authentik
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=authentik
INFO: ---- Inventory ----
========================================
Service:          authentik
Compose:          services/authentic/compose.yaml
Containers:       authentik-db,authentik-redis,authentik-server,authentik-worker
Source config:    (none)
Target config:    /mnt/monarch/appdata/authentik
Keep on /hive:    (none)
Risk / order:     medium / 20
Migration req:    verify
Already migrated: partial
Notes:            PATH_DATA/authentik/*; compose dir still named authentic
----------------------------------------
Compose bind mounts (raw lines):
      - ../.env
      - ${PATH_DATA}/authentik/db:/var/lib/postgresql/data
      - ${PATH_DATA}/authentik/redis:/data
      - ../.env
      - ${PATH_DATA}/authentik/media:/media
      - ${PATH_DATA}/authentik/templates:/templates
      - ../.env
      - /var/run/docker.sock:/var/run/docker.sock
      - ${PATH_DATA}/authentik/media:/media
      - ${PATH_DATA}/authentik/templates:/templates
      - ${PATH_DATA}/authentik/certs:/certs
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-authentik.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/authentik && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/authentik (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for authentik → /mnt/monarch/appdata/authentik
WARN: Container not found for inspect: authentik-db
WARN: Container not found for inspect: authentik-redis
WARN: Container not found for inspect: authentik-server
WARN: Container not found for inspect: authentik-worker
INFO: [dry-run] would stop containers: authentik-db,authentik-redis,authentik-server,authentik-worker
INFO: [dry-run] would start compose project services/authentic/compose.yaml
INFO: Finished authentik → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-authentik.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] authentik
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### honcho

```
INFO: === run-migration service=honcho execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/honcho/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/honcho
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=honcho
INFO: ---- Inventory ----
========================================
Service:          honcho
Compose:          services/honcho/compose.yml
Containers:       honcho-api,honcho-deriver,honcho-postgres,honcho-redis
Source config:    (none)
Target config:    /mnt/monarch/appdata/honcho
Keep on /hive:    (none)
Risk / order:     medium / 21
Migration req:    no
Already migrated: yes
Notes:            postgres+redis already on appdata
----------------------------------------
Compose bind mounts (raw lines):
      - /mnt/monarch/appdata/honcho/postgres:/var/lib/postgresql/data
      - /mnt/monarch/appdata/honcho/redis:/data
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-honcho.json
INFO: Service already on appdata — path check only
INFO: ---- Compose path check ----
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

### hermes

```
INFO: === run-migration service=hermes execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/hermes/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination empty: /mnt/monarch/appdata/hermes
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=hermes
INFO: ---- Inventory ----
========================================
Service:          hermes
Compose:          services/hermes/compose.yml
Containers:       hermes
Source config:    (none)
Target config:    /mnt/monarch/appdata/hermes
Keep on /hive:    (none)
Risk / order:     medium / 22
Migration req:    no
Already migrated: yes
Notes:            Already on appdata
----------------------------------------
Compose bind mounts (raw lines):
      - /mnt/monarch/appdata/hermes:/opt/data
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-hermes.json
INFO: Service already on appdata — path check only
INFO: ---- Compose path check ----
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

### n8n

```
INFO: === run-migration service=n8n execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/n8n/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/n8n
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=n8n
INFO: ---- Inventory ----
========================================
Service:          n8n
Compose:          services/n8n/compose.yml
Containers:       n8n
Source config:    (none)
Target config:    /mnt/monarch/appdata/n8n
Keep on /hive:    (none)
Risk / order:     medium / 23
Migration req:    no
Already migrated: yes
Notes:            Already on appdata
----------------------------------------
Compose bind mounts (raw lines):
      - "5678:5678"
      - NODES_EXCLUDE:"[]"
      - /mnt/monarch/appdata/n8n:/home/node/.n8n
      - /mnt/monarch/appdata/n8n/workflows:/workflows
      - /mnt/monarch/appdata/n8n/reports:/reports
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-n8n.json
INFO: Service already on appdata — path check only
INFO: ---- Compose path check ----
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

### open-webui

```
INFO: === run-migration service=open-webui execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/ollama/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: no source_config configured (verify/already-migrated service)
INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/open-webui
WARN: could not fully evaluate free space vs source
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=2 service=open-webui
INFO: ---- Inventory ----
========================================
Service:          open-webui
Compose:          services/ollama/compose.yml
Containers:       open-webui
Source config:    (none)
Target config:    /mnt/monarch/appdata/open-webui
Keep on /hive:    (none)
Risk / order:     medium / 24
Migration req:    no
Already migrated: yes
Notes:            Shares compose with ollama; already on appdata
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/ollama:/root/.ollama
            - driver: nvidia
      - /mnt/monarch/appdata/open-webui:/app/backend/data
      - OLLAMA_BASE_URL=http://ollama:11434
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-open-webui.json
INFO: Service already on appdata — path check only
INFO: ---- Compose path check ----
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/Compose_Path_Check_Runtime.md (WARN=9 FAIL=0)
```

### ollama

```
INFO: === run-migration service=ollama execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/ollama/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/ollama
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/ollama
INFO: OK: free space 1.9TB >= need ~71GB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=ollama
INFO: ---- Inventory ----
========================================
Service:          ollama
Compose:          services/ollama/compose.yml
Containers:       ollama
Source config:    /hive/ollama
Target config:    /mnt/monarch/appdata/ollama
Keep on /hive:    (none)
Risk / order:     higher / 30
Migration req:    yes
Already migrated: no
Notes:            INTENTIONAL EXCEPTION: migrate config+models to appdata (largest model ~8B). Relocatable later via services.conf source/target swap if SSD capacity requires returning models to /hive
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/ollama:/root/.ollama
            - driver: nvidia
      - /mnt/monarch/appdata/open-webui:/app/backend/data
      - OLLAMA_BASE_URL=http://ollama:11434
Source stats: bytes=68737096851 files=76 dirs=22 (65GB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-ollama.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/ollama && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/ollama (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for ollama → /mnt/monarch/appdata/ollama
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/ollama-ollama-20260730T001422Z.json
INFO: [dry-run] would stop containers: ollama
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/ollama/ → /mnt/monarch/appdata/ollama/

Number of files: 98 (reg: 76, dir: 22)
Number of created files: 98 (reg: 76, dir: 22)
Number of deleted files: 0
Number of regular files transferred: 76
Total file size: 68,737,096,710 bytes
Total transferred file size: 68,737,096,710 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 6,144
Total bytes received: 331

sent 6,144 bytes  received 331 bytes  12,950.00 bytes/sec
total size is 68,737,096,710  speedup is 10,615,767.83 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/ollama → /mnt/monarch/appdata/ollama
INFO: Validating CURRENT compose: services/ollama/compose.yml
time="2026-07-30T00:14:22Z" level=warning msg="The \"OLLAMA_API_KEY\" variable is not set. Defaulting to a blank string."
time="2026-07-30T00:14:22Z" level=warning msg="The \"WEBUI_SECRET_KEY\" variable is not set. Defaulting to a blank string."
env file /home/fatherfrank/projects/homelab/services/ollama/.env not found: stat /home/fatherfrank/projects/homelab/services/ollama/.env: no such file or directory
WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
INFO: Validating PROPOSED compose
time="2026-07-30T00:14:22Z" level=warning msg="The \"OLLAMA_API_KEY\" variable is not set. Defaulting to a blank string."
time="2026-07-30T00:14:22Z" level=warning msg="The \"WEBUI_SECRET_KEY\" variable is not set. Defaulting to a blank string."
env file /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/.env not found: stat /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/.env: no such file or directory
WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/ollama/compose.yml
INFO: Finished ollama → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-ollama.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] ollama
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### calibre

```
INFO: === run-migration service=calibre execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/calibre-web/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/calibre/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/calibre
INFO: OK: free space 1.9TB >= need ~141MB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=calibre
INFO: ---- Inventory ----
========================================
Service:          calibre
Compose:          services/calibre-web/compose.yml
Containers:       calibre
Source config:    /hive/calibre/config
Target config:    /mnt/monarch/appdata/calibre
Keep on /hive:    /hive/library
Risk / order:     higher / 31
Migration req:    yes
Already migrated: no
Notes:            Same compose as calibre-web; books stay on /hive/library
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/calibre/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
      - /hive/library/Kavita/browser_cache:/config/browser_cache
      - /hive/calibre-web/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
Source stats: bytes=38493102 files=312 dirs=171 (37MB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-calibre.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/calibre && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/calibre (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for calibre → /mnt/monarch/appdata/calibre
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/calibre-calibre-20260730T001422Z.json
INFO: [dry-run] would stop containers: calibre
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/calibre/config/ → /mnt/monarch/appdata/calibre/

Number of files: 483 (reg: 312, dir: 171)
Number of created files: 483 (reg: 312, dir: 171)
Number of deleted files: 0
Number of regular files transferred: 312
Total file size: 38,492,278 bytes
Total transferred file size: 38,492,278 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 21,114
Total bytes received: 1,647

sent 21,114 bytes  received 1,647 bytes  15,174.00 bytes/sec
total size is 38,492,278  speedup is 1,691.15 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/calibre/config → /mnt/monarch/appdata/calibre
INFO: Validating CURRENT compose: services/calibre-web/compose.yml
INFO: CURRENT compose config OK
INFO: Validating PROPOSED compose
INFO: PROPOSED compose config OK
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/calibre-web/compose.yml
INFO: Finished calibre → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-calibre.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] calibre
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### calibre-web

```
INFO: === run-migration service=calibre-web execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/calibre-web/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/calibre-web/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/calibre-web
INFO: OK: free space 1.9TB >= need ~101MB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=calibre-web
INFO: ---- Inventory ----
========================================
Service:          calibre-web
Compose:          services/calibre-web/compose.yml
Containers:       calibre-web
Source config:    /hive/calibre-web/config
Target config:    /mnt/monarch/appdata/calibre-web
Keep on /hive:    /hive/library
Risk / order:     higher / 32
Migration req:    yes
Already migrated: no
Notes:            Books stay on /hive/library
----------------------------------------
Compose bind mounts (raw lines):
      - /hive/calibre/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
      - /hive/library/Kavita/browser_cache:/config/browser_cache
      - /hive/calibre-web/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
Source stats: bytes=340210 files=6 dirs=1 (333KB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-calibre-web.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/calibre-web && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/calibre-web (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for calibre-web → /mnt/monarch/appdata/calibre-web
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/calibre-web-calibre-web-20260730T001423Z.json
INFO: [dry-run] would stop containers: calibre-web
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/calibre-web/config/ → /mnt/monarch/appdata/calibre-web/

Number of files: 7 (reg: 6, dir: 1)
Number of created files: 7 (reg: 6, dir: 1)
Number of deleted files: 0
Number of regular files transferred: 6
Total file size: 340,202 bytes
Total transferred file size: 340,202 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 268
Total bytes received: 37

sent 268 bytes  received 37 bytes  610.00 bytes/sec
total size is 340,202  speedup is 1,115.42 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/calibre-web/config → /mnt/monarch/appdata/calibre-web
INFO: Validating CURRENT compose: services/calibre-web/compose.yml
INFO: CURRENT compose config OK
INFO: Validating PROPOSED compose
INFO: PROPOSED compose config OK
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre-web/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre-web/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/calibre-web/compose.yml
INFO: Finished calibre-web → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-calibre-web.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] calibre-web
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### jellyfin

```
INFO: === run-migration service=jellyfin execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/jellyfin/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/jellyfin/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/jellyfin
INFO: OK: free space 1.9TB >= need ~12GB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=jellyfin
INFO: ---- Inventory ----
========================================
Service:          jellyfin
Compose:          services/jellyfin/compose.yml
Containers:       jellyfin
Source config:    /hive/jellyfin/config
Target config:    /mnt/monarch/appdata/jellyfin
Keep on /hive:    /hive/jellyfin/tv,/hive/jellyfin/movie
Risk / order:     final / 40
Migration req:    yes
Already migrated: no
Notes:            Config only; media stays on /hive
----------------------------------------
Compose bind mounts (raw lines):
      - "8096:8096"
      - /dev/dri:/dev/dri
      - /hive/jellyfin/config:/config
      - /hive/jellyfin/tv:/data/tvshows
      - /hive/jellyfin/movie:/data/movies
Source stats: bytes=11033554488 files=48159 dirs=22669 (11GB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-jellyfin.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/jellyfin && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/jellyfin (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for jellyfin → /mnt/monarch/appdata/jellyfin
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/jellyfin-jellyfin-20260730T001425Z.json
INFO: [dry-run] would stop containers: jellyfin
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/jellyfin/config/ → /mnt/monarch/appdata/jellyfin/

Number of files: 70,831 (reg: 48,159, dir: 22,669, special: 3)
Number of created files: 70,831 (reg: 48,159, dir: 22,669, special: 3)
Number of deleted files: 0
Number of regular files transferred: 48,159
Total file size: 11,033,438,320 bytes
Total transferred file size: 11,033,438,320 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 196,599
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 2,630,657
Total bytes received: 235,745

sent 2,630,657 bytes  received 235,745 bytes  1,910,934.67 bytes/sec
total size is 11,033,438,320  speedup is 3,849.23 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/jellyfin/config → /mnt/monarch/appdata/jellyfin
INFO: Validating CURRENT compose: services/jellyfin/compose.yml
env file /home/fatherfrank/projects/homelab/services/jellyfin/.env not found: stat /home/fatherfrank/projects/homelab/services/jellyfin/.env: no such file or directory
WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
INFO: Validating PROPOSED compose
env file /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/.env not found: stat /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/.env: no such file or directory
WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/jellyfin/compose.yml
INFO: Finished jellyfin → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-jellyfin.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] jellyfin
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### nzbget

```
INFO: === run-migration service=nzbget execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/NZBget/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/NZBget/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/nzbget
INFO: OK: free space 1.9TB >= need ~154GB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=nzbget
INFO: ---- Inventory ----
========================================
Service:          nzbget
Compose:          services/NZBget/compose.yml
Containers:       nzbget
Source config:    /hive/NZBget/config
Target config:    /mnt/monarch/appdata/nzbget
Keep on /hive:    /hive/downloads
Risk / order:     final / 41
Migration req:    yes
Already migrated: no
Notes:            Config only; downloads stay on /hive
----------------------------------------
Compose bind mounts (raw lines):
      - type: bind
        source: /hive/NZBget/config
      - type: bind
        source: /hive/downloads
Source stats: bytes=149443981643 files=281 dirs=54 (140GB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-nzbget.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/nzbget && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/nzbget (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for nzbget → /mnt/monarch/appdata/nzbget
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/nzbget-nzbget-20260730T001428Z.json
INFO: [dry-run] would stop containers: nzbget
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/NZBget/config/ → /mnt/monarch/appdata/nzbget/

Number of files: 335 (reg: 281, dir: 54)
Number of created files: 335 (reg: 281, dir: 54)
Number of deleted files: 0
Number of regular files transferred: 281
Total file size: 149,443,981,201 bytes
Total transferred file size: 149,443,981,201 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 15,508
Total bytes received: 1,078

sent 15,508 bytes  received 1,078 bytes  33,172.00 bytes/sec
total size is 149,443,981,201  speedup is 9,010,248.47 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/NZBget/config → /mnt/monarch/appdata/nzbget
INFO: Validating CURRENT compose: services/NZBget/compose.yml
INFO: CURRENT compose config OK
INFO: Validating PROPOSED compose
INFO: PROPOSED compose config OK
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/nzbget/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/nzbget/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/NZBget/compose.yml
INFO: Finished nzbget → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-nzbget.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] nzbget
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### hotio

```
INFO: === run-migration service=hotio execute=0 apply_compose=0 ===
INFO: ---- Preflight ----
INFO: OK: compose exists: services/Hotio/compose.yml
INFO: OK: docker daemon reachable
INFO: OK: docker compose available
INFO: OK: rsync installed
INFO: OK: /mnt/monarch present
INFO: OK: /mnt/monarch appears mounted
INFO: OK: source exists: /hive/Hotio/config
INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/hotio
INFO: OK: free space 1.9TB >= need ~124MB
WARN: git working tree not clean (warning only)
INFO: OK: ZFS: all pools healthy
Preflight summary: CRITICAL=0 WARNINGS=1 service=hotio
INFO: ---- Inventory ----
========================================
Service:          hotio
Compose:          services/Hotio/compose.yml
Containers:       qbittorrent
Source config:    /hive/Hotio/config
Target config:    /mnt/monarch/appdata/hotio
Keep on /hive:    /hive/downloads/completed
Risk / order:     final / 42
Migration req:    yes
Already migrated: no
Notes:            Config only; downloads stay; related media stack
----------------------------------------
Compose bind mounts (raw lines):
      - mode: ingress
      - mode: ingress
      - mode: ingress
      - type: bind
        source: /hive/Hotio/config
      - type: bind
        source: /hive/downloads/completed
Source stats: bytes=21976525 files=854 dirs=15 (21MB)
INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-hotio.json
INFO: ---- Verify destination ----
INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/hotio && ensure ownership/permissions
INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/hotio (parent=/mnt/monarch/appdata)
INFO: Filesystem type=btrfs avail=1.9T
INFO: Destination verification OK for hotio → /mnt/monarch/appdata/hotio
INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/hotio-qbittorrent-20260730T001428Z.json
INFO: [dry-run] would stop containers: qbittorrent
INFO: ---- Copy configuration ----
INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/Hotio/config/ → /mnt/monarch/appdata/hotio/

Number of files: 870 (reg: 854, dir: 15, special: 1)
Number of created files: 870 (reg: 854, dir: 15, special: 1)
Number of deleted files: 0
Number of regular files transferred: 854
Total file size: 21,975,626 bytes
Total transferred file size: 21,975,626 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 58,730
Total bytes received: 2,636

sent 58,730 bytes  received 2,636 bytes  40,910.67 bytes/sec
total size is 21,975,626  speedup is 358.11 (DRY RUN)
INFO: ---- Verify copy ----
WARN: Target missing (expected before execute copy)
INFO: ---- Update compose ----
INFO: Proposed rewrite: /hive/Hotio/config → /mnt/monarch/appdata/hotio
INFO: Validating CURRENT compose: services/Hotio/compose.yml
INFO: CURRENT compose config OK
INFO: Validating PROPOSED compose
INFO: PROPOSED compose config OK
INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/hotio/compose.yml
INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/hotio/compose.diff
INFO: Compose NOT applied (pass --apply-compose after review)
INFO: [dry-run] would start compose project services/Hotio/compose.yml
INFO: Finished hotio → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-hotio.json
INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] hotio
INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

## Per-service logs

### authentik.log

```
2026-07-30T00:12:10Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:12:10Z Started
2026-07-30T00:12:10Z INFO: === run-migration service=authentik execute=0 apply_compose=0 ===
2026-07-30T00:12:10Z INFO: ---- Preflight ----
2026-07-30T00:12:10Z Preflight
2026-07-30T00:12:10Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:12:10Z Preflight
2026-07-30T00:12:10Z INFO: OK: compose exists: services/authentic/compose.yaml
2026-07-30T00:12:10Z INFO: OK: docker daemon reachable
2026-07-30T00:12:10Z INFO: OK: docker compose available
2026-07-30T00:12:10Z INFO: OK: rsync installed
2026-07-30T00:12:10Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:10Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:10Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:12:10Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/authentik
2026-07-30T00:12:10Z WARN: could not fully evaluate free space vs source
2026-07-30T00:12:10Z WARN: git working tree not clean (warning only)
2026-07-30T00:12:10Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:12:10Z Preflight complete critical=0 warnings=2
2026-07-30T00:12:10Z INFO: ---- Inventory ----
2026-07-30T00:12:10Z Inventory
2026-07-30T00:12:10Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:12:10Z Inventory
2026-07-30T00:12:10Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-authentik.json
2026-07-30T00:12:10Z INFO: ---- Verify destination ----
2026-07-30T00:12:10Z Verify destination
2026-07-30T00:12:10Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:12:10Z Verify destination
2026-07-30T00:12:10Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/authentik && ensure ownership/permissions
2026-07-30T00:12:10Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/authentik (parent=/mnt/monarch/appdata)
2026-07-30T00:12:10Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:12:10Z Verification destination complete
2026-07-30T00:12:10Z INFO: Destination verification OK for authentik → /mnt/monarch/appdata/authentik
2026-07-30T00:12:10Z WARN: Container not found for inspect: authentik-db
2026-07-30T00:12:10Z WARN: Container not found for inspect: authentik-redis
2026-07-30T00:12:10Z WARN: Container not found for inspect: authentik-server
2026-07-30T00:12:10Z WARN: Container not found for inspect: authentik-worker
2026-07-30T00:12:10Z INFO: [dry-run] would stop containers: authentik-db,authentik-redis,authentik-server,authentik-worker
2026-07-30T00:12:10Z INFO: [dry-run] would start compose project services/authentic/compose.yaml
2026-07-30T00:12:10Z Finished
2026-07-30T00:12:10Z INFO: Finished authentik → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-authentik.json
2026-07-30T00:12:10Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] authentik
2026-07-30T00:12:10Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
2026-07-30T00:14:21Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:14:21Z Started
2026-07-30T00:14:21Z INFO: === run-migration service=authentik execute=0 apply_compose=0 ===
2026-07-30T00:14:21Z INFO: ---- Preflight ----
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z INFO: OK: compose exists: services/authentic/compose.yaml
2026-07-30T00:14:21Z INFO: OK: docker daemon reachable
2026-07-30T00:14:21Z INFO: OK: docker compose available
2026-07-30T00:14:21Z INFO: OK: rsync installed
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:21Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:21Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/authentik
2026-07-30T00:14:21Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:21Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:21Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:21Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:21Z INFO: ---- Inventory ----
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-authentik.json
2026-07-30T00:14:21Z INFO: ---- Verify destination ----
2026-07-30T00:14:21Z Verify destination
2026-07-30T00:14:21Z Started service=authentik execute=0 apply_compose=0
2026-07-30T00:14:21Z Verify destination
2026-07-30T00:14:21Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/authentik && ensure ownership/permissions
2026-07-30T00:14:21Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/authentik (parent=/mnt/monarch/appdata)
2026-07-30T00:14:21Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:21Z Verification destination complete
2026-07-30T00:14:21Z INFO: Destination verification OK for authentik → /mnt/monarch/appdata/authentik
2026-07-30T00:14:21Z WARN: Container not found for inspect: authentik-db
2026-07-30T00:14:21Z WARN: Container not found for inspect: authentik-redis
2026-07-30T00:14:21Z WARN: Container not found for inspect: authentik-server
2026-07-30T00:14:21Z WARN: Container not found for inspect: authentik-worker
2026-07-30T00:14:21Z INFO: [dry-run] would stop containers: authentik-db,authentik-redis,authentik-server,authentik-worker
2026-07-30T00:14:21Z INFO: [dry-run] would start compose project services/authentic/compose.yaml
2026-07-30T00:14:21Z Finished
2026-07-30T00:14:21Z INFO: Finished authentik → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-authentik.json
2026-07-30T00:14:21Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] authentik
2026-07-30T00:14:21Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### beszel.log

```
2026-07-30T00:12:04Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:12:04Z Inventory
2026-07-30T00:12:04Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json
2026-07-30T00:12:10Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:12:10Z Started
2026-07-30T00:12:10Z INFO: === run-migration service=beszel execute=0 apply_compose=0 ===
2026-07-30T00:12:10Z INFO: ---- Preflight ----
2026-07-30T00:12:10Z Preflight
2026-07-30T00:12:10Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:12:10Z Preflight
2026-07-30T00:12:10Z INFO: OK: compose exists: services/beszel/compose.yml
2026-07-30T00:12:10Z INFO: OK: docker daemon reachable
2026-07-30T00:12:10Z INFO: OK: docker compose available
2026-07-30T00:12:10Z INFO: OK: rsync installed
2026-07-30T00:12:10Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:10Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:10Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:12:10Z INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/beszel
2026-07-30T00:12:10Z WARN: could not fully evaluate free space vs source
2026-07-30T00:12:10Z WARN: git working tree not clean (warning only)
2026-07-30T00:12:10Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:12:10Z Preflight complete critical=0 warnings=2
2026-07-30T00:12:10Z INFO: ---- Inventory ----
2026-07-30T00:12:10Z Inventory
2026-07-30T00:12:10Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:12:10Z Inventory
2026-07-30T00:12:10Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json
2026-07-30T00:12:10Z INFO: Service already on appdata — path check only
2026-07-30T00:12:10Z INFO: ---- Compose path check ----
2026-07-30T00:12:10Z Compose path check
2026-07-30T00:12:10Z Finished
2026-07-30T00:14:18Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:14:18Z Inventory
2026-07-30T00:14:18Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json
2026-07-30T00:14:20Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:14:20Z Started
2026-07-30T00:14:20Z INFO: === run-migration service=beszel execute=0 apply_compose=0 ===
2026-07-30T00:14:20Z INFO: ---- Preflight ----
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z INFO: OK: compose exists: services/beszel/compose.yml
2026-07-30T00:14:20Z INFO: OK: docker daemon reachable
2026-07-30T00:14:20Z INFO: OK: docker compose available
2026-07-30T00:14:20Z INFO: OK: rsync installed
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:20Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:20Z INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/beszel
2026-07-30T00:14:20Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:20Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:20Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:20Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:20Z INFO: ---- Inventory ----
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:20Z Started service=beszel execute=0 apply_compose=0
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:21Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-beszel.json
2026-07-30T00:14:21Z INFO: Service already on appdata — path check only
2026-07-30T00:14:21Z INFO: ---- Compose path check ----
2026-07-30T00:14:21Z Compose path check
2026-07-30T00:14:21Z Finished
```

### calibre.log

```
2026-07-30T00:14:22Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:22Z Started
2026-07-30T00:14:22Z INFO: === run-migration service=calibre execute=0 apply_compose=0 ===
2026-07-30T00:14:22Z INFO: ---- Preflight ----
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z INFO: OK: compose exists: services/calibre-web/compose.yml
2026-07-30T00:14:22Z INFO: OK: docker daemon reachable
2026-07-30T00:14:22Z INFO: OK: docker compose available
2026-07-30T00:14:22Z INFO: OK: rsync installed
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:22Z INFO: OK: source exists: /hive/calibre/config
2026-07-30T00:14:22Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/calibre
2026-07-30T00:14:22Z INFO: OK: free space 1.9TB >= need ~141MB
2026-07-30T00:14:22Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:22Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:22Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:22Z INFO: ---- Inventory ----
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-calibre.json
2026-07-30T00:14:22Z INFO: ---- Verify destination ----
2026-07-30T00:14:22Z Verify destination
2026-07-30T00:14:22Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:22Z Verify destination
2026-07-30T00:14:22Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/calibre && ensure ownership/permissions
2026-07-30T00:14:22Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/calibre (parent=/mnt/monarch/appdata)
2026-07-30T00:14:22Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:22Z Verification destination complete
2026-07-30T00:14:22Z INFO: Destination verification OK for calibre → /mnt/monarch/appdata/calibre
2026-07-30T00:14:22Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/calibre-calibre-20260730T001422Z.json
2026-07-30T00:14:22Z docker inspect saved for calibre
2026-07-30T00:14:22Z INFO: [dry-run] would stop containers: calibre
2026-07-30T00:14:22Z INFO: ---- Copy configuration ----
2026-07-30T00:14:22Z Copy configuration
2026-07-30T00:14:22Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:22Z Copy configuration
2026-07-30T00:14:22Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/calibre/config/ → /mnt/monarch/appdata/calibre/
2026-07-30T00:14:23Z Copy complete (dry-run)
2026-07-30T00:14:23Z INFO: ---- Verify copy ----
2026-07-30T00:14:23Z Verify copy
2026-07-30T00:14:23Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:23Z Verification
2026-07-30T00:14:23Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:23Z Verification complete (target missing dry-run)
2026-07-30T00:14:23Z INFO: ---- Update compose ----
2026-07-30T00:14:23Z Update compose
2026-07-30T00:14:23Z Started service=calibre execute=0 apply_compose=0
2026-07-30T00:14:23Z Compose update planning
2026-07-30T00:14:23Z INFO: Proposed rewrite: /hive/calibre/config → /mnt/monarch/appdata/calibre
2026-07-30T00:14:23Z INFO: Validating CURRENT compose: services/calibre-web/compose.yml
2026-07-30T00:14:23Z INFO: CURRENT compose config OK
2026-07-30T00:14:23Z INFO: Validating PROPOSED compose
2026-07-30T00:14:23Z INFO: PROPOSED compose config OK
2026-07-30T00:14:23Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre/compose.yml
2026-07-30T00:14:23Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre/compose.diff
2026-07-30T00:14:23Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:23Z Compose updated=false (proposed only)
2026-07-30T00:14:23Z INFO: [dry-run] would start compose project services/calibre-web/compose.yml
2026-07-30T00:14:23Z Finished
2026-07-30T00:14:23Z INFO: Finished calibre → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-calibre.json
2026-07-30T00:14:23Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] calibre
2026-07-30T00:14:23Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### calibre-web.log

```
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Started
2026-07-30T00:14:23Z INFO: === run-migration service=calibre-web execute=0 apply_compose=0 ===
2026-07-30T00:14:23Z INFO: ---- Preflight ----
2026-07-30T00:14:23Z Preflight
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Preflight
2026-07-30T00:14:23Z INFO: OK: compose exists: services/calibre-web/compose.yml
2026-07-30T00:14:23Z INFO: OK: docker daemon reachable
2026-07-30T00:14:23Z INFO: OK: docker compose available
2026-07-30T00:14:23Z INFO: OK: rsync installed
2026-07-30T00:14:23Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:23Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:23Z INFO: OK: source exists: /hive/calibre-web/config
2026-07-30T00:14:23Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/calibre-web
2026-07-30T00:14:23Z INFO: OK: free space 1.9TB >= need ~101MB
2026-07-30T00:14:23Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:23Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:23Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:23Z INFO: ---- Inventory ----
2026-07-30T00:14:23Z Inventory
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Inventory
2026-07-30T00:14:23Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-calibre-web.json
2026-07-30T00:14:23Z INFO: ---- Verify destination ----
2026-07-30T00:14:23Z Verify destination
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Verify destination
2026-07-30T00:14:23Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/calibre-web && ensure ownership/permissions
2026-07-30T00:14:23Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/calibre-web (parent=/mnt/monarch/appdata)
2026-07-30T00:14:23Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:23Z Verification destination complete
2026-07-30T00:14:23Z INFO: Destination verification OK for calibre-web → /mnt/monarch/appdata/calibre-web
2026-07-30T00:14:23Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/calibre-web-calibre-web-20260730T001423Z.json
2026-07-30T00:14:23Z docker inspect saved for calibre-web
2026-07-30T00:14:23Z INFO: [dry-run] would stop containers: calibre-web
2026-07-30T00:14:23Z INFO: ---- Copy configuration ----
2026-07-30T00:14:23Z Copy configuration
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Copy configuration
2026-07-30T00:14:23Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/calibre-web/config/ → /mnt/monarch/appdata/calibre-web/
2026-07-30T00:14:23Z Copy complete (dry-run)
2026-07-30T00:14:23Z INFO: ---- Verify copy ----
2026-07-30T00:14:23Z Verify copy
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Verification
2026-07-30T00:14:23Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:23Z Verification complete (target missing dry-run)
2026-07-30T00:14:23Z INFO: ---- Update compose ----
2026-07-30T00:14:23Z Update compose
2026-07-30T00:14:23Z Started service=calibre-web execute=0 apply_compose=0
2026-07-30T00:14:23Z Compose update planning
2026-07-30T00:14:23Z INFO: Proposed rewrite: /hive/calibre-web/config → /mnt/monarch/appdata/calibre-web
2026-07-30T00:14:23Z INFO: Validating CURRENT compose: services/calibre-web/compose.yml
2026-07-30T00:14:23Z INFO: CURRENT compose config OK
2026-07-30T00:14:23Z INFO: Validating PROPOSED compose
2026-07-30T00:14:23Z INFO: PROPOSED compose config OK
2026-07-30T00:14:23Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre-web/compose.yml
2026-07-30T00:14:23Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/calibre-web/compose.diff
2026-07-30T00:14:23Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:23Z Compose updated=false (proposed only)
2026-07-30T00:14:23Z INFO: [dry-run] would start compose project services/calibre-web/compose.yml
2026-07-30T00:14:23Z Finished
2026-07-30T00:14:23Z INFO: Finished calibre-web → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-calibre-web.json
2026-07-30T00:14:23Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] calibre-web
2026-07-30T00:14:23Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### code-server.log

```
2026-07-30T00:07:43Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:07:43Z Inventory
2026-07-30T00:11:55Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:11:55Z Inventory
2026-07-30T00:12:04Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json
2026-07-30T00:12:04Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:04Z Started
2026-07-30T00:12:04Z INFO: === run-migration service=code-server execute=0 apply_compose=0 ===
2026-07-30T00:12:04Z INFO: ---- Preflight ----
2026-07-30T00:12:04Z Preflight
2026-07-30T00:12:04Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:04Z Preflight
2026-07-30T00:12:04Z INFO: OK: compose exists: services/code-server/compose.yml
2026-07-30T00:12:04Z INFO: OK: docker daemon reachable
2026-07-30T00:12:04Z INFO: OK: docker compose available
2026-07-30T00:12:04Z INFO: OK: rsync installed
2026-07-30T00:12:04Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:04Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:04Z INFO: OK: source exists: /hive/code-server/config
2026-07-30T00:12:05Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/code-server
2026-07-30T00:12:05Z INFO: OK: free space 1.9TB >= need ~3.4GB
2026-07-30T00:12:05Z WARN: git working tree not clean (warning only)
2026-07-30T00:12:05Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:12:05Z Preflight complete critical=0 warnings=1
2026-07-30T00:12:05Z INFO: ---- Inventory ----
2026-07-30T00:12:05Z Inventory
2026-07-30T00:12:05Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:05Z Inventory
2026-07-30T00:12:05Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json
2026-07-30T00:12:05Z INFO: ---- Verify destination ----
2026-07-30T00:12:05Z Verify destination
2026-07-30T00:12:05Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:05Z Verify destination
2026-07-30T00:12:05Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/code-server && ensure ownership/permissions
2026-07-30T00:12:05Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/code-server (parent=/mnt/monarch/appdata)
2026-07-30T00:12:05Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:12:05Z Verification destination complete
2026-07-30T00:12:05Z INFO: Destination verification OK for code-server → /mnt/monarch/appdata/code-server
2026-07-30T00:12:05Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/code-server-code-server-20260730T001205Z.json
2026-07-30T00:12:05Z docker inspect saved for code-server
2026-07-30T00:12:05Z INFO: [dry-run] would stop containers: code-server
2026-07-30T00:12:05Z INFO: ---- Copy configuration ----
2026-07-30T00:12:05Z Copy configuration
2026-07-30T00:12:05Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:05Z Copy configuration
2026-07-30T00:12:05Z INFO: [dry-run] rsync -aHAX --info=progress2 -n /hive/code-server/config/ → /mnt/monarch/appdata/code-server/
2026-07-30T00:12:06Z Copy complete (dry-run)
2026-07-30T00:12:06Z INFO: ---- Verify copy ----
2026-07-30T00:12:06Z Verify copy
2026-07-30T00:12:06Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:06Z Verification
2026-07-30T00:12:06Z WARN: Target missing (expected before execute copy)
2026-07-30T00:12:06Z Verification complete (target missing dry-run)
2026-07-30T00:12:06Z INFO: ---- Update compose ----
2026-07-30T00:12:06Z Update compose
2026-07-30T00:12:06Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:12:06Z Compose update planning
2026-07-30T00:12:06Z INFO: Proposed rewrite: /hive/code-server/config → /mnt/monarch/appdata/code-server
2026-07-30T00:12:06Z INFO: Validating CURRENT compose: services/code-server/compose.yml
2026-07-30T00:12:06Z ERROR: docker compose config FAILED on CURRENT compose — abort
2026-07-30T00:14:18Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:18Z Inventory
2026-07-30T00:14:18Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json
2026-07-30T00:14:18Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:18Z Started
2026-07-30T00:14:18Z INFO: === run-migration service=code-server execute=0 apply_compose=0 ===
2026-07-30T00:14:18Z INFO: ---- Preflight ----
2026-07-30T00:14:18Z Preflight
2026-07-30T00:14:18Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:18Z Preflight
2026-07-30T00:14:18Z INFO: OK: compose exists: services/code-server/compose.yml
2026-07-30T00:14:19Z INFO: OK: docker daemon reachable
2026-07-30T00:14:19Z INFO: OK: docker compose available
2026-07-30T00:14:19Z INFO: OK: rsync installed
2026-07-30T00:14:19Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:19Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:19Z INFO: OK: source exists: /hive/code-server/config
2026-07-30T00:14:19Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/code-server
2026-07-30T00:14:19Z INFO: OK: free space 1.9TB >= need ~3.4GB
2026-07-30T00:14:19Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:19Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:19Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:19Z INFO: ---- Inventory ----
2026-07-30T00:14:19Z Inventory
2026-07-30T00:14:19Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:19Z Inventory
2026-07-30T00:14:19Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-code-server.json
2026-07-30T00:14:19Z INFO: ---- Verify destination ----
2026-07-30T00:14:19Z Verify destination
2026-07-30T00:14:19Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:19Z Verify destination
2026-07-30T00:14:19Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/code-server && ensure ownership/permissions
2026-07-30T00:14:19Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/code-server (parent=/mnt/monarch/appdata)
2026-07-30T00:14:19Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:19Z Verification destination complete
2026-07-30T00:14:19Z INFO: Destination verification OK for code-server → /mnt/monarch/appdata/code-server
2026-07-30T00:14:19Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/code-server-code-server-20260730T001419Z.json
2026-07-30T00:14:19Z docker inspect saved for code-server
2026-07-30T00:14:19Z INFO: [dry-run] would stop containers: code-server
2026-07-30T00:14:19Z INFO: ---- Copy configuration ----
2026-07-30T00:14:19Z Copy configuration
2026-07-30T00:14:19Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:19Z Copy configuration
2026-07-30T00:14:19Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/code-server/config/ → /mnt/monarch/appdata/code-server/
2026-07-30T00:14:20Z Copy complete (dry-run)
2026-07-30T00:14:20Z INFO: ---- Verify copy ----
2026-07-30T00:14:20Z Verify copy
2026-07-30T00:14:20Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:20Z Verification
2026-07-30T00:14:20Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:20Z Verification complete (target missing dry-run)
2026-07-30T00:14:20Z INFO: ---- Update compose ----
2026-07-30T00:14:20Z Update compose
2026-07-30T00:14:20Z Started service=code-server execute=0 apply_compose=0
2026-07-30T00:14:20Z Compose update planning
2026-07-30T00:14:20Z INFO: Proposed rewrite: /hive/code-server/config → /mnt/monarch/appdata/code-server
2026-07-30T00:14:20Z INFO: Validating CURRENT compose: services/code-server/compose.yml
2026-07-30T00:14:20Z WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
2026-07-30T00:14:20Z INFO: Validating PROPOSED compose
2026-07-30T00:14:20Z WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
2026-07-30T00:14:20Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/compose.yml
2026-07-30T00:14:20Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/code-server/compose.diff
2026-07-30T00:14:20Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:20Z Compose updated=false (proposed only)
2026-07-30T00:14:20Z INFO: [dry-run] would start compose project services/code-server/compose.yml
2026-07-30T00:14:20Z Finished
2026-07-30T00:14:20Z INFO: Finished code-server → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-code-server.json
2026-07-30T00:14:20Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] code-server
2026-07-30T00:14:20Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### hermes.log

```
2026-07-30T00:14:21Z Started service=hermes execute=0 apply_compose=0
2026-07-30T00:14:21Z Started
2026-07-30T00:14:21Z INFO: === run-migration service=hermes execute=0 apply_compose=0 ===
2026-07-30T00:14:21Z INFO: ---- Preflight ----
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z Started service=hermes execute=0 apply_compose=0
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z INFO: OK: compose exists: services/hermes/compose.yml
2026-07-30T00:14:21Z INFO: OK: docker daemon reachable
2026-07-30T00:14:21Z INFO: OK: docker compose available
2026-07-30T00:14:21Z INFO: OK: rsync installed
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:21Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:21Z INFO: OK: destination empty: /mnt/monarch/appdata/hermes
2026-07-30T00:14:21Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:21Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:21Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:21Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:21Z INFO: ---- Inventory ----
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z Started service=hermes execute=0 apply_compose=0
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-hermes.json
2026-07-30T00:14:21Z INFO: Service already on appdata — path check only
2026-07-30T00:14:21Z INFO: ---- Compose path check ----
2026-07-30T00:14:21Z Compose path check
2026-07-30T00:14:21Z Finished
```

### homepage.log

```
2026-07-30T00:12:04Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:12:04Z Inventory
2026-07-30T00:12:04Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-homepage.json
2026-07-30T00:14:18Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:14:18Z Inventory
2026-07-30T00:14:18Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-homepage.json
2026-07-30T00:14:20Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:14:20Z Started
2026-07-30T00:14:20Z INFO: === run-migration service=homepage execute=0 apply_compose=0 ===
2026-07-30T00:14:20Z INFO: ---- Preflight ----
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z INFO: OK: compose exists: services/homepage/compose.yaml
2026-07-30T00:14:20Z INFO: OK: docker daemon reachable
2026-07-30T00:14:20Z INFO: OK: docker compose available
2026-07-30T00:14:20Z INFO: OK: rsync installed
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:20Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:20Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/homepage
2026-07-30T00:14:20Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:20Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:20Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:20Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:20Z INFO: ---- Inventory ----
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:20Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:20Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-homepage.json
2026-07-30T00:14:20Z INFO: ---- Verify destination ----
2026-07-30T00:14:20Z Verify destination
2026-07-30T00:14:20Z Started service=homepage execute=0 apply_compose=0
2026-07-30T00:14:20Z Verify destination
2026-07-30T00:14:20Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/homepage && ensure ownership/permissions
2026-07-30T00:14:20Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/homepage (parent=/mnt/monarch/appdata)
2026-07-30T00:14:20Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:20Z Verification destination complete
2026-07-30T00:14:20Z INFO: Destination verification OK for homepage → /mnt/monarch/appdata/homepage
2026-07-30T00:14:20Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/homepage-homepage-20260730T001420Z.json
2026-07-30T00:14:20Z docker inspect saved for homepage
2026-07-30T00:14:20Z INFO: [dry-run] would stop containers: homepage
2026-07-30T00:14:20Z INFO: [dry-run] would start compose project services/homepage/compose.yaml
2026-07-30T00:14:20Z Finished
2026-07-30T00:14:20Z INFO: Finished homepage → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-homepage.json
2026-07-30T00:14:20Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] homepage
2026-07-30T00:14:20Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### honcho.log

```
2026-07-30T00:14:21Z Started service=honcho execute=0 apply_compose=0
2026-07-30T00:14:21Z Started
2026-07-30T00:14:21Z INFO: === run-migration service=honcho execute=0 apply_compose=0 ===
2026-07-30T00:14:21Z INFO: ---- Preflight ----
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z Started service=honcho execute=0 apply_compose=0
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z INFO: OK: compose exists: services/honcho/compose.yml
2026-07-30T00:14:21Z INFO: OK: docker daemon reachable
2026-07-30T00:14:21Z INFO: OK: docker compose available
2026-07-30T00:14:21Z INFO: OK: rsync installed
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:21Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:21Z INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/honcho
2026-07-30T00:14:21Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:21Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:21Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:21Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:21Z INFO: ---- Inventory ----
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z Started service=honcho execute=0 apply_compose=0
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-honcho.json
2026-07-30T00:14:21Z INFO: Service already on appdata — path check only
2026-07-30T00:14:21Z INFO: ---- Compose path check ----
2026-07-30T00:14:21Z Compose path check
2026-07-30T00:14:21Z Finished
```

### hotio.log

```
2026-07-30T00:14:28Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:28Z Started
2026-07-30T00:14:28Z INFO: === run-migration service=hotio execute=0 apply_compose=0 ===
2026-07-30T00:14:28Z INFO: ---- Preflight ----
2026-07-30T00:14:28Z Preflight
2026-07-30T00:14:28Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:28Z Preflight
2026-07-30T00:14:28Z INFO: OK: compose exists: services/Hotio/compose.yml
2026-07-30T00:14:28Z INFO: OK: docker daemon reachable
2026-07-30T00:14:28Z INFO: OK: docker compose available
2026-07-30T00:14:28Z INFO: OK: rsync installed
2026-07-30T00:14:28Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:28Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:28Z INFO: OK: source exists: /hive/Hotio/config
2026-07-30T00:14:28Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/hotio
2026-07-30T00:14:28Z INFO: OK: free space 1.9TB >= need ~124MB
2026-07-30T00:14:28Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:28Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:28Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:28Z INFO: ---- Inventory ----
2026-07-30T00:14:28Z Inventory
2026-07-30T00:14:28Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:28Z Inventory
2026-07-30T00:14:28Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-hotio.json
2026-07-30T00:14:28Z INFO: ---- Verify destination ----
2026-07-30T00:14:28Z Verify destination
2026-07-30T00:14:28Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:28Z Verify destination
2026-07-30T00:14:28Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/hotio && ensure ownership/permissions
2026-07-30T00:14:28Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/hotio (parent=/mnt/monarch/appdata)
2026-07-30T00:14:28Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:28Z Verification destination complete
2026-07-30T00:14:28Z INFO: Destination verification OK for hotio → /mnt/monarch/appdata/hotio
2026-07-30T00:14:28Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/hotio-qbittorrent-20260730T001428Z.json
2026-07-30T00:14:28Z docker inspect saved for qbittorrent
2026-07-30T00:14:28Z INFO: [dry-run] would stop containers: qbittorrent
2026-07-30T00:14:28Z INFO: ---- Copy configuration ----
2026-07-30T00:14:28Z Copy configuration
2026-07-30T00:14:28Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:28Z Copy configuration
2026-07-30T00:14:28Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/Hotio/config/ → /mnt/monarch/appdata/hotio/
2026-07-30T00:14:29Z Copy complete (dry-run)
2026-07-30T00:14:29Z INFO: ---- Verify copy ----
2026-07-30T00:14:29Z Verify copy
2026-07-30T00:14:29Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:29Z Verification
2026-07-30T00:14:29Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:29Z Verification complete (target missing dry-run)
2026-07-30T00:14:29Z INFO: ---- Update compose ----
2026-07-30T00:14:29Z Update compose
2026-07-30T00:14:29Z Started service=hotio execute=0 apply_compose=0
2026-07-30T00:14:29Z Compose update planning
2026-07-30T00:14:29Z INFO: Proposed rewrite: /hive/Hotio/config → /mnt/monarch/appdata/hotio
2026-07-30T00:14:29Z INFO: Validating CURRENT compose: services/Hotio/compose.yml
2026-07-30T00:14:29Z INFO: CURRENT compose config OK
2026-07-30T00:14:29Z INFO: Validating PROPOSED compose
2026-07-30T00:14:29Z INFO: PROPOSED compose config OK
2026-07-30T00:14:29Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/hotio/compose.yml
2026-07-30T00:14:29Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/hotio/compose.diff
2026-07-30T00:14:29Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:29Z Compose updated=false (proposed only)
2026-07-30T00:14:29Z INFO: [dry-run] would start compose project services/Hotio/compose.yml
2026-07-30T00:14:29Z Finished
2026-07-30T00:14:29Z INFO: Finished hotio → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-hotio.json
2026-07-30T00:14:29Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] hotio
2026-07-30T00:14:29Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### jellyfin.log

```
2026-07-30T00:12:06Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:06Z Started
2026-07-30T00:12:06Z INFO: === run-migration service=jellyfin execute=0 apply_compose=0 ===
2026-07-30T00:12:06Z INFO: ---- Preflight ----
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z INFO: OK: compose exists: services/jellyfin/compose.yml
2026-07-30T00:12:06Z INFO: OK: docker daemon reachable
2026-07-30T00:12:06Z INFO: OK: docker compose available
2026-07-30T00:12:06Z INFO: OK: rsync installed
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:06Z INFO: OK: source exists: /hive/jellyfin/config
2026-07-30T00:12:07Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/jellyfin
2026-07-30T00:12:08Z INFO: OK: free space 1.9TB >= need ~12GB
2026-07-30T00:12:08Z WARN: git working tree not clean (warning only)
2026-07-30T00:12:08Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:12:08Z Preflight complete critical=0 warnings=1
2026-07-30T00:12:08Z INFO: ---- Inventory ----
2026-07-30T00:12:08Z Inventory
2026-07-30T00:12:08Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:08Z Inventory
2026-07-30T00:12:09Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-jellyfin.json
2026-07-30T00:12:09Z INFO: ---- Verify destination ----
2026-07-30T00:12:09Z Verify destination
2026-07-30T00:12:09Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:09Z Verify destination
2026-07-30T00:12:09Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/jellyfin && ensure ownership/permissions
2026-07-30T00:12:09Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/jellyfin (parent=/mnt/monarch/appdata)
2026-07-30T00:12:09Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:12:09Z Verification destination complete
2026-07-30T00:12:09Z INFO: Destination verification OK for jellyfin → /mnt/monarch/appdata/jellyfin
2026-07-30T00:12:09Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/jellyfin-jellyfin-20260730T001209Z.json
2026-07-30T00:12:09Z docker inspect saved for jellyfin
2026-07-30T00:12:09Z INFO: [dry-run] would stop containers: jellyfin
2026-07-30T00:12:09Z INFO: ---- Copy configuration ----
2026-07-30T00:12:09Z Copy configuration
2026-07-30T00:12:09Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:09Z Copy configuration
2026-07-30T00:12:09Z INFO: [dry-run] rsync -aHAX --info=progress2 -n /hive/jellyfin/config/ → /mnt/monarch/appdata/jellyfin/
2026-07-30T00:12:10Z Copy complete (dry-run)
2026-07-30T00:12:10Z INFO: ---- Verify copy ----
2026-07-30T00:12:10Z Verify copy
2026-07-30T00:12:10Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:10Z Verification
2026-07-30T00:12:10Z WARN: Target missing (expected before execute copy)
2026-07-30T00:12:10Z Verification complete (target missing dry-run)
2026-07-30T00:12:10Z INFO: ---- Update compose ----
2026-07-30T00:12:10Z Update compose
2026-07-30T00:12:10Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:12:10Z Compose update planning
2026-07-30T00:12:10Z INFO: Proposed rewrite: /hive/jellyfin/config → /mnt/monarch/appdata/jellyfin
2026-07-30T00:12:10Z INFO: Validating CURRENT compose: services/jellyfin/compose.yml
2026-07-30T00:12:10Z ERROR: docker compose config FAILED on CURRENT compose — abort
2026-07-30T00:14:23Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:23Z Started
2026-07-30T00:14:23Z INFO: === run-migration service=jellyfin execute=0 apply_compose=0 ===
2026-07-30T00:14:23Z INFO: ---- Preflight ----
2026-07-30T00:14:23Z Preflight
2026-07-30T00:14:23Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:23Z Preflight
2026-07-30T00:14:23Z INFO: OK: compose exists: services/jellyfin/compose.yml
2026-07-30T00:14:23Z INFO: OK: docker daemon reachable
2026-07-30T00:14:23Z INFO: OK: docker compose available
2026-07-30T00:14:23Z INFO: OK: rsync installed
2026-07-30T00:14:23Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:23Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:23Z INFO: OK: source exists: /hive/jellyfin/config
2026-07-30T00:14:24Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/jellyfin
2026-07-30T00:14:24Z INFO: OK: free space 1.9TB >= need ~12GB
2026-07-30T00:14:24Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:24Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:24Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:24Z INFO: ---- Inventory ----
2026-07-30T00:14:24Z Inventory
2026-07-30T00:14:24Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:24Z Inventory
2026-07-30T00:14:25Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-jellyfin.json
2026-07-30T00:14:25Z INFO: ---- Verify destination ----
2026-07-30T00:14:25Z Verify destination
2026-07-30T00:14:25Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:25Z Verify destination
2026-07-30T00:14:25Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/jellyfin && ensure ownership/permissions
2026-07-30T00:14:25Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/jellyfin (parent=/mnt/monarch/appdata)
2026-07-30T00:14:25Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:25Z Verification destination complete
2026-07-30T00:14:25Z INFO: Destination verification OK for jellyfin → /mnt/monarch/appdata/jellyfin
2026-07-30T00:14:25Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/jellyfin-jellyfin-20260730T001425Z.json
2026-07-30T00:14:25Z docker inspect saved for jellyfin
2026-07-30T00:14:25Z INFO: [dry-run] would stop containers: jellyfin
2026-07-30T00:14:25Z INFO: ---- Copy configuration ----
2026-07-30T00:14:25Z Copy configuration
2026-07-30T00:14:25Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:25Z Copy configuration
2026-07-30T00:14:25Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/jellyfin/config/ → /mnt/monarch/appdata/jellyfin/
2026-07-30T00:14:26Z Copy complete (dry-run)
2026-07-30T00:14:26Z INFO: ---- Verify copy ----
2026-07-30T00:14:26Z Verify copy
2026-07-30T00:14:26Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:26Z Verification
2026-07-30T00:14:26Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:26Z Verification complete (target missing dry-run)
2026-07-30T00:14:26Z INFO: ---- Update compose ----
2026-07-30T00:14:26Z Update compose
2026-07-30T00:14:26Z Started service=jellyfin execute=0 apply_compose=0
2026-07-30T00:14:26Z Compose update planning
2026-07-30T00:14:26Z INFO: Proposed rewrite: /hive/jellyfin/config → /mnt/monarch/appdata/jellyfin
2026-07-30T00:14:26Z INFO: Validating CURRENT compose: services/jellyfin/compose.yml
2026-07-30T00:14:26Z WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
2026-07-30T00:14:26Z INFO: Validating PROPOSED compose
2026-07-30T00:14:26Z WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
2026-07-30T00:14:26Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/compose.yml
2026-07-30T00:14:26Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/jellyfin/compose.diff
2026-07-30T00:14:26Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:26Z Compose updated=false (proposed only)
2026-07-30T00:14:26Z INFO: [dry-run] would start compose project services/jellyfin/compose.yml
2026-07-30T00:14:26Z Finished
2026-07-30T00:14:26Z INFO: Finished jellyfin → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-jellyfin.json
2026-07-30T00:14:26Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] jellyfin
2026-07-30T00:14:26Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### n8n.log

```
2026-07-30T00:14:21Z Started service=n8n execute=0 apply_compose=0
2026-07-30T00:14:21Z Started
2026-07-30T00:14:21Z INFO: === run-migration service=n8n execute=0 apply_compose=0 ===
2026-07-30T00:14:21Z INFO: ---- Preflight ----
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z Started service=n8n execute=0 apply_compose=0
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z INFO: OK: compose exists: services/n8n/compose.yml
2026-07-30T00:14:21Z INFO: OK: docker daemon reachable
2026-07-30T00:14:21Z INFO: OK: docker compose available
2026-07-30T00:14:21Z INFO: OK: rsync installed
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:21Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:21Z INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/n8n
2026-07-30T00:14:21Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:21Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:21Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:21Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:21Z INFO: ---- Inventory ----
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z Started service=n8n execute=0 apply_compose=0
2026-07-30T00:14:21Z Inventory
2026-07-30T00:14:21Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-n8n.json
2026-07-30T00:14:22Z INFO: Service already on appdata — path check only
2026-07-30T00:14:22Z INFO: ---- Compose path check ----
2026-07-30T00:14:22Z Compose path check
2026-07-30T00:14:22Z Finished
```

### nzbget.log

```
2026-07-30T00:14:26Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:26Z Started
2026-07-30T00:14:26Z INFO: === run-migration service=nzbget execute=0 apply_compose=0 ===
2026-07-30T00:14:26Z INFO: ---- Preflight ----
2026-07-30T00:14:26Z Preflight
2026-07-30T00:14:26Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:26Z Preflight
2026-07-30T00:14:26Z INFO: OK: compose exists: services/NZBget/compose.yml
2026-07-30T00:14:26Z INFO: OK: docker daemon reachable
2026-07-30T00:14:26Z INFO: OK: docker compose available
2026-07-30T00:14:26Z INFO: OK: rsync installed
2026-07-30T00:14:26Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:26Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:26Z INFO: OK: source exists: /hive/NZBget/config
2026-07-30T00:14:28Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/nzbget
2026-07-30T00:14:28Z INFO: OK: free space 1.9TB >= need ~154GB
2026-07-30T00:14:28Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:28Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:28Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:28Z INFO: ---- Inventory ----
2026-07-30T00:14:28Z Inventory
2026-07-30T00:14:28Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:28Z Inventory
2026-07-30T00:14:28Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-nzbget.json
2026-07-30T00:14:28Z INFO: ---- Verify destination ----
2026-07-30T00:14:28Z Verify destination
2026-07-30T00:14:28Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:28Z Verify destination
2026-07-30T00:14:28Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/nzbget && ensure ownership/permissions
2026-07-30T00:14:28Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/nzbget (parent=/mnt/monarch/appdata)
2026-07-30T00:14:28Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:28Z Verification destination complete
2026-07-30T00:14:28Z INFO: Destination verification OK for nzbget → /mnt/monarch/appdata/nzbget
2026-07-30T00:14:28Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/nzbget-nzbget-20260730T001428Z.json
2026-07-30T00:14:28Z docker inspect saved for nzbget
2026-07-30T00:14:28Z INFO: [dry-run] would stop containers: nzbget
2026-07-30T00:14:28Z INFO: ---- Copy configuration ----
2026-07-30T00:14:28Z Copy configuration
2026-07-30T00:14:28Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:28Z Copy configuration
2026-07-30T00:14:28Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/NZBget/config/ → /mnt/monarch/appdata/nzbget/
2026-07-30T00:14:28Z Copy complete (dry-run)
2026-07-30T00:14:28Z INFO: ---- Verify copy ----
2026-07-30T00:14:28Z Verify copy
2026-07-30T00:14:28Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:28Z Verification
2026-07-30T00:14:28Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:28Z Verification complete (target missing dry-run)
2026-07-30T00:14:28Z INFO: ---- Update compose ----
2026-07-30T00:14:28Z Update compose
2026-07-30T00:14:28Z Started service=nzbget execute=0 apply_compose=0
2026-07-30T00:14:28Z Compose update planning
2026-07-30T00:14:28Z INFO: Proposed rewrite: /hive/NZBget/config → /mnt/monarch/appdata/nzbget
2026-07-30T00:14:28Z INFO: Validating CURRENT compose: services/NZBget/compose.yml
2026-07-30T00:14:28Z INFO: CURRENT compose config OK
2026-07-30T00:14:28Z INFO: Validating PROPOSED compose
2026-07-30T00:14:28Z INFO: PROPOSED compose config OK
2026-07-30T00:14:28Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/nzbget/compose.yml
2026-07-30T00:14:28Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/nzbget/compose.diff
2026-07-30T00:14:28Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:28Z Compose updated=false (proposed only)
2026-07-30T00:14:28Z INFO: [dry-run] would start compose project services/NZBget/compose.yml
2026-07-30T00:14:28Z Finished
2026-07-30T00:14:28Z INFO: Finished nzbget → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-nzbget.json
2026-07-30T00:14:28Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] nzbget
2026-07-30T00:14:28Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### ollama.log

```
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Started
2026-07-30T00:12:06Z INFO: === run-migration service=ollama execute=0 apply_compose=0 ===
2026-07-30T00:12:06Z INFO: ---- Preflight ----
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z INFO: OK: compose exists: services/ollama/compose.yml
2026-07-30T00:12:06Z INFO: OK: docker daemon reachable
2026-07-30T00:12:06Z INFO: OK: docker compose available
2026-07-30T00:12:06Z INFO: OK: rsync installed
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:06Z INFO: OK: source exists: /hive/ollama
2026-07-30T00:12:06Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/ollama
2026-07-30T00:12:06Z INFO: OK: free space 1.9TB >= need ~71GB
2026-07-30T00:12:06Z WARN: git working tree not clean (warning only)
2026-07-30T00:12:06Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:12:06Z Preflight complete critical=0 warnings=1
2026-07-30T00:12:06Z INFO: ---- Inventory ----
2026-07-30T00:12:06Z Inventory
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Inventory
2026-07-30T00:12:06Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-ollama.json
2026-07-30T00:12:06Z INFO: ---- Verify destination ----
2026-07-30T00:12:06Z Verify destination
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Verify destination
2026-07-30T00:12:06Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/ollama && ensure ownership/permissions
2026-07-30T00:12:06Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/ollama (parent=/mnt/monarch/appdata)
2026-07-30T00:12:06Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:12:06Z Verification destination complete
2026-07-30T00:12:06Z INFO: Destination verification OK for ollama → /mnt/monarch/appdata/ollama
2026-07-30T00:12:06Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/ollama-ollama-20260730T001206Z.json
2026-07-30T00:12:06Z docker inspect saved for ollama
2026-07-30T00:12:06Z INFO: [dry-run] would stop containers: ollama
2026-07-30T00:12:06Z INFO: ---- Copy configuration ----
2026-07-30T00:12:06Z Copy configuration
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Copy configuration
2026-07-30T00:12:06Z INFO: [dry-run] rsync -aHAX --info=progress2 -n /hive/ollama/ → /mnt/monarch/appdata/ollama/
2026-07-30T00:12:06Z Copy complete (dry-run)
2026-07-30T00:12:06Z INFO: ---- Verify copy ----
2026-07-30T00:12:06Z Verify copy
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Verification
2026-07-30T00:12:06Z WARN: Target missing (expected before execute copy)
2026-07-30T00:12:06Z Verification complete (target missing dry-run)
2026-07-30T00:12:06Z INFO: ---- Update compose ----
2026-07-30T00:12:06Z Update compose
2026-07-30T00:12:06Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:12:06Z Compose update planning
2026-07-30T00:12:06Z INFO: Proposed rewrite: /hive/ollama → /mnt/monarch/appdata/ollama
2026-07-30T00:12:06Z INFO: Validating CURRENT compose: services/ollama/compose.yml
2026-07-30T00:12:06Z ERROR: docker compose config FAILED on CURRENT compose — abort
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Started
2026-07-30T00:14:22Z INFO: === run-migration service=ollama execute=0 apply_compose=0 ===
2026-07-30T00:14:22Z INFO: ---- Preflight ----
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z INFO: OK: compose exists: services/ollama/compose.yml
2026-07-30T00:14:22Z INFO: OK: docker daemon reachable
2026-07-30T00:14:22Z INFO: OK: docker compose available
2026-07-30T00:14:22Z INFO: OK: rsync installed
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:22Z INFO: OK: source exists: /hive/ollama
2026-07-30T00:14:22Z INFO: OK: destination does not exist yet (will mkdir in verify-destination): /mnt/monarch/appdata/ollama
2026-07-30T00:14:22Z INFO: OK: free space 1.9TB >= need ~71GB
2026-07-30T00:14:22Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:22Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:22Z Preflight complete critical=0 warnings=1
2026-07-30T00:14:22Z INFO: ---- Inventory ----
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-ollama.json
2026-07-30T00:14:22Z INFO: ---- Verify destination ----
2026-07-30T00:14:22Z Verify destination
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Verify destination
2026-07-30T00:14:22Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/ollama && ensure ownership/permissions
2026-07-30T00:14:22Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/ollama (parent=/mnt/monarch/appdata)
2026-07-30T00:14:22Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:22Z Verification destination complete
2026-07-30T00:14:22Z INFO: Destination verification OK for ollama → /mnt/monarch/appdata/ollama
2026-07-30T00:14:22Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/ollama-ollama-20260730T001422Z.json
2026-07-30T00:14:22Z docker inspect saved for ollama
2026-07-30T00:14:22Z INFO: [dry-run] would stop containers: ollama
2026-07-30T00:14:22Z INFO: ---- Copy configuration ----
2026-07-30T00:14:22Z Copy configuration
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Copy configuration
2026-07-30T00:14:22Z INFO: [dry-run] rsync -aHAX -n --info=stats2 /hive/ollama/ → /mnt/monarch/appdata/ollama/
2026-07-30T00:14:22Z Copy complete (dry-run)
2026-07-30T00:14:22Z INFO: ---- Verify copy ----
2026-07-30T00:14:22Z Verify copy
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Verification
2026-07-30T00:14:22Z WARN: Target missing (expected before execute copy)
2026-07-30T00:14:22Z Verification complete (target missing dry-run)
2026-07-30T00:14:22Z INFO: ---- Update compose ----
2026-07-30T00:14:22Z Update compose
2026-07-30T00:14:22Z Started service=ollama execute=0 apply_compose=0
2026-07-30T00:14:22Z Compose update planning
2026-07-30T00:14:22Z INFO: Proposed rewrite: /hive/ollama → /mnt/monarch/appdata/ollama
2026-07-30T00:14:22Z INFO: Validating CURRENT compose: services/ollama/compose.yml
2026-07-30T00:14:22Z WARN: CURRENT compose config failed (often missing .env) — continuing dry-run / propose
2026-07-30T00:14:22Z INFO: Validating PROPOSED compose
2026-07-30T00:14:22Z WARN: Proposed compose config failed (often missing .env off-host / incomplete env)
2026-07-30T00:14:22Z INFO: Wrote proposed compose: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/compose.yml
2026-07-30T00:14:22Z INFO: Wrote diff: /home/fatherfrank/projects/homelab/Validation/Phase10.5/proposed/ollama/compose.diff
2026-07-30T00:14:22Z INFO: Compose NOT applied (pass --apply-compose after review)
2026-07-30T00:14:22Z Compose updated=false (proposed only)
2026-07-30T00:14:22Z INFO: [dry-run] would start compose project services/ollama/compose.yml
2026-07-30T00:14:22Z Finished
2026-07-30T00:14:22Z INFO: Finished ollama → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-ollama.json
2026-07-30T00:14:22Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] ollama
2026-07-30T00:14:22Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

### open-webui.log

```
2026-07-30T00:14:22Z Started service=open-webui execute=0 apply_compose=0
2026-07-30T00:14:22Z Started
2026-07-30T00:14:22Z INFO: === run-migration service=open-webui execute=0 apply_compose=0 ===
2026-07-30T00:14:22Z INFO: ---- Preflight ----
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z Started service=open-webui execute=0 apply_compose=0
2026-07-30T00:14:22Z Preflight
2026-07-30T00:14:22Z INFO: OK: compose exists: services/ollama/compose.yml
2026-07-30T00:14:22Z INFO: OK: docker daemon reachable
2026-07-30T00:14:22Z INFO: OK: docker compose available
2026-07-30T00:14:22Z INFO: OK: rsync installed
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:22Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:22Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:22Z INFO: OK: destination already populated (already_migrated=yes): /mnt/monarch/appdata/open-webui
2026-07-30T00:14:22Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:22Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:22Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:22Z Preflight complete critical=0 warnings=2
2026-07-30T00:14:22Z INFO: ---- Inventory ----
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z Started service=open-webui execute=0 apply_compose=0
2026-07-30T00:14:22Z Inventory
2026-07-30T00:14:22Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-open-webui.json
2026-07-30T00:14:22Z INFO: Service already on appdata — path check only
2026-07-30T00:14:22Z INFO: ---- Compose path check ----
2026-07-30T00:14:22Z Compose path check
2026-07-30T00:14:22Z Finished
```

### portainer.log

```
2026-07-30T00:12:04Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:12:04Z Inventory
2026-07-30T00:12:06Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:12:06Z Started
2026-07-30T00:12:06Z INFO: === run-migration service=portainer execute=0 apply_compose=0 ===
2026-07-30T00:12:06Z INFO: ---- Preflight ----
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:12:06Z Preflight
2026-07-30T00:12:06Z INFO: OK: compose exists: services/portainer/compose.yaml
2026-07-30T00:12:06Z INFO: OK: docker daemon reachable
2026-07-30T00:12:06Z INFO: OK: docker compose available
2026-07-30T00:12:06Z INFO: OK: rsync installed
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch present
2026-07-30T00:12:06Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:12:06Z INFO: OK: source exists: /hive/portainer
2026-07-30T00:14:18Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:14:18Z Inventory
2026-07-30T00:14:21Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:14:21Z Started
2026-07-30T00:14:21Z INFO: === run-migration service=portainer execute=0 apply_compose=0 ===
2026-07-30T00:14:21Z INFO: ---- Preflight ----
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z Started service=portainer execute=0 apply_compose=0
2026-07-30T00:14:21Z Preflight
2026-07-30T00:14:21Z INFO: OK: compose exists: services/portainer/compose.yaml
2026-07-30T00:14:21Z INFO: OK: docker daemon reachable
2026-07-30T00:14:21Z INFO: OK: docker compose available
2026-07-30T00:14:21Z INFO: OK: rsync installed
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:21Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:21Z INFO: OK: source exists: /hive/portainer
```

### traefik.log

```
2026-07-30T00:12:04Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:12:04Z Inventory
2026-07-30T00:12:04Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-traefik.json
2026-07-30T00:14:18Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:14:18Z Inventory
2026-07-30T00:14:18Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-traefik.json
2026-07-30T00:14:20Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:14:20Z Started
2026-07-30T00:14:20Z INFO: === run-migration service=traefik execute=0 apply_compose=0 ===
2026-07-30T00:14:20Z INFO: ---- Preflight ----
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:14:20Z Preflight
2026-07-30T00:14:20Z INFO: OK: compose exists: services/traefik/compose.yaml
2026-07-30T00:14:20Z INFO: OK: docker daemon reachable
2026-07-30T00:14:20Z INFO: OK: docker compose available
2026-07-30T00:14:20Z INFO: OK: rsync installed
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch present
2026-07-30T00:14:20Z INFO: OK: /mnt/monarch appears mounted
2026-07-30T00:14:20Z INFO: OK: no source_config configured (verify/already-migrated service)
2026-07-30T00:14:20Z WARN: destination non-empty: /mnt/monarch/appdata/traefik
2026-07-30T00:14:20Z WARN: could not fully evaluate free space vs source
2026-07-30T00:14:20Z WARN: git working tree not clean (warning only)
2026-07-30T00:14:20Z INFO: OK: ZFS: all pools healthy
2026-07-30T00:14:20Z Preflight complete critical=0 warnings=3
2026-07-30T00:14:20Z INFO: ---- Inventory ----
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:20Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:14:20Z Inventory
2026-07-30T00:14:20Z INFO: Wrote /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/inventory-traefik.json
2026-07-30T00:14:20Z INFO: ---- Verify destination ----
2026-07-30T00:14:20Z Verify destination
2026-07-30T00:14:20Z Started service=traefik execute=0 apply_compose=0
2026-07-30T00:14:20Z Verify destination
2026-07-30T00:14:20Z INFO: [dry-run] would: mkdir -p /mnt/monarch/appdata/traefik && ensure ownership/permissions
2026-07-30T00:14:20Z INFO: [dry-run] destination plan: mkdir -p /mnt/monarch/appdata/traefik (parent=/mnt/monarch/appdata)
2026-07-30T00:14:20Z INFO: Filesystem type=btrfs avail=1.9T
2026-07-30T00:14:20Z WARN: Destination non-empty
2026-07-30T00:14:20Z Verification destination complete
2026-07-30T00:14:20Z INFO: Destination verification OK for traefik → /mnt/monarch/appdata/traefik
2026-07-30T00:14:20Z INFO: Saved docker inspect → /home/fatherfrank/projects/homelab/Validation/Phase10.5/inspect/traefik-traefik-20260730T001420Z.json
2026-07-30T00:14:20Z docker inspect saved for traefik
2026-07-30T00:14:20Z INFO: [dry-run] would stop containers: traefik
2026-07-30T00:14:20Z INFO: [dry-run] would start compose project services/traefik/compose.yaml
2026-07-30T00:14:20Z Finished
2026-07-30T00:14:20Z INFO: Finished traefik → /home/fatherfrank/projects/homelab/Validation/Phase10.5/reports/migration-traefik.json
2026-07-30T00:14:20Z INFO: Rollback: /home/fatherfrank/projects/homelab/scripts/migration/rollback.sh [--execute] traefik
2026-07-30T00:14:20Z INFO: NOTE: originals are NOT renamed to .old by this orchestrator; do that manually after soak.
```

## Notes from this host run

- `/mnt/monarch` is mounted (btrfs, ~1.9T free observed earlier).
- ZFS reported healthy.
- `docker compose config` may WARN when service `.env` is missing; apply still requires success under `--execute --apply-compose`.
- Git working tree dirty is expected while Phase 10.5 files are uncommitted.
- No `--execute` was used.
