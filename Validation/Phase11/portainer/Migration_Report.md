# Phase 11 — Portainer Migration Report

**Service:** portainer  
**Batch:** 01  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T09:12:30Z

## Summary

Portainer config/state migrated from `/hive/portainer` to `/mnt/monarch/appdata/portainer`. Compose updated in-repo. Source preserved as `/hive/portainer.old`.

## Paths

| Role | Path |
|------|------|
| Original source | `/hive/portainer` |
| Rollback copy | `/hive/portainer.old` |
| New destination | `/mnt/monarch/appdata/portainer` |
| Authoritative compose | `services/portainer/compose.yaml` |
| Compose backup | `Validation/Phase11/portainer/proposed/portainer/compose.yaml.pre-migrate.bak` |

## Compose change

```diff
-      - /hive/portainer:/data
+      - /mnt/monarch/appdata/portainer:/data
```

No unrelated services modified.

## Execution timeline

| Step | Result |
|------|--------|
| Dry-run | SUCCESS (approved earlier; see `Dry_Run_Review.md`) |
| First execute attempt | STOPPED — destination mkdir permission denied |
| Remediation | `/mnt/monarch/appdata` writable as `fatherfrank`; Batch 01 dest dirs created |
| Execute copy `--checksum` | SUCCESS — checksum inventory matches |
| Post-copy restart (old path) | SUCCESS — still on `/hive/portainer` |
| Cutover stop + delta rsync | SUCCESS — 2 files refreshed (`portainer.db` etc.) |
| `--apply-compose` | SUCCESS |
| Recreate + smoke | PASS (API 200); Docker healthcheck unhealthy (pre-existing) |
| Rename source → `.old` | SUCCESS |

## Verification

- Migratable size ~2.6MB; excludes `compose/49,compose/50` (root-owned; expected)
- Source files=18 dirs=19; dest files=18 dirs=17 (exclude-related dir delta expected)
- Checksum inventory: **matches**
- Evidence under `reports/`, `inspect/`, `logs/`, `proposed/`

## Smoke test

See `Smoke_Test.md`. Functional endpoints OK. Docker `unhealthy` due to distroless image vs `CMD-SHELL` healthcheck.

## Rollback procedure

```bash
# 1. Restore compose from backup
cp -a Validation/Phase11/portainer/proposed/portainer/compose.yaml.pre-migrate.bak \
  services/portainer/compose.yaml

# 2. Restore source path name if needed
mv /hive/portainer.old /hive/portainer

# Or use framework helper:
./scripts/migration/rollback.sh --execute --phase-dir Validation/Phase11/portainer portainer

# 3. Recreate
(cd services/portainer && docker compose -f compose.yaml up -d)
```

Keep `/hive/portainer.old` for **≥ 7 days**. Do not delete automatically.

## Lessons learned

1. `/mnt/monarch/appdata` must be writable by the migration user before execute (or dest dirs pre-created).
2. Orchestrator restarts on the **old** path when compose is not applied; perform a final stop + delta rsync immediately before `--apply-compose`.
3. Live Portainer was previously managed from `/hive/portainer/compose.yaml`; post-migration authority is the repo compose under `services/portainer/`.
4. Portainer CE LTS healthcheck in repo compose needs a follow-up fix (no `/bin/sh` in image).

## Commands executed (high level)

```bash
mkdir -p /mnt/monarch/appdata/{portainer,homepage/images,code-server}
./scripts/migration/run-migration.sh --execute --checksum \
  --phase-dir Validation/Phase11/portainer portainer
docker stop portainer
rsync -aHAX --exclude=compose/49 --exclude=compose/50 \
  /hive/portainer/ /mnt/monarch/appdata/portainer/
./scripts/migration/update-compose.sh --execute --apply-compose \
  --phase-dir Validation/Phase11/portainer portainer
(cd services/portainer && docker compose -f compose.yaml up -d)
mv /hive/portainer /hive/portainer.old
```

## Final decision

**READY FOR SOAK**

Leave `/hive/portainer.old` untouched for a minimum of seven (7) days before cleanup.
