# Phase 11 — code-server Migration Report

**Service:** code-server  
**Batch:** 01  
**Final status:** READY FOR SOAK  
**Completed:** 2026-07-30T09:38:00Z

## Summary

code-server config migrated from `/hive/code-server/config` to `/mnt/monarch/appdata/code-server`. Compose volume rewritten. Entire `/hive/code-server` preserved as `/hive/code-server.old`.

## Paths

| Role | Path |
|------|------|
| Original tree | `/hive/code-server` |
| Rollback copy | `/hive/code-server.old` |
| New destination | `/mnt/monarch/appdata/code-server` |
| Authoritative compose | `services/code-server/compose.yml` |
| Compose backup | `Validation/Phase11/code-server/proposed/code-server/compose.yml.pre-migrate.bak` |
| Env (gitignored) | `services/code-server/.env` (`PASSWORD` only) |

## Compose change

```diff
-      - /hive/code-server/config:/config
+      - /mnt/monarch/appdata/code-server:/config
```

Repo RO workspace mounts (`/hive`, `/mnt/monarch/appdata`) remain enabled (were commented out on live hive compose).

## Execution timeline

| Step | Result |
|------|--------|
| Dry-run | SUCCESS (approved) |
| Create gitignored `.env` | SUCCESS |
| Execute copy `--checksum` | SUCCESS — 3.0GB, 41259 files; checksum match while stopped |
| Post-copy restart (old path) | Started; added `workspcae/monarch` mountpoint under source |
| Orchestrator smoke re-verify | FAIL (dir/checksum drift from live mountpoint) — **copy already verified** |
| Cutover stop + delta rsync | SUCCESS |
| Re-verify `--checksum` (stopped) | SUCCESS |
| `--apply-compose` + recreate | SUCCESS |
| Functional smoke | PASS — Traefik 302 |
| Rename `/hive/code-server` → `.old` | SUCCESS |

## Verification

- ~3.0GB; 41259 files / 6886 dirs after final sync
- Checksum inventory: **matches** (while stopped, pre-apply)
- Evidence under `reports/`, `inspect/`, `logs/`, `proposed/`

## Smoke test

See `Smoke_Test.md`.

## Rollback procedure

```bash
cp -a Validation/Phase11/code-server/proposed/code-server/compose.yml.pre-migrate.bak \
  services/code-server/compose.yml
mv /hive/code-server.old /hive/code-server
# Ensure services/code-server/.env still has PASSWORD
(cd services/code-server && docker compose -f compose.yml up -d)
# Or run from restored hive compose project if preferred
```

Keep `/hive/code-server.old` ≥ **7 days**. Do not delete automatically.

## Lessons learned

1. Orchestrator smoke step re-runs copy verification after restarting on the **old** path; live writes/mountpoints can fail that step even when the stopped-container copy verified cleanly.
2. Always stop + delta rsync + re-verify immediately before `--apply-compose` for writable app state.
3. code-server requires gitignored `.env` with `PASSWORD` before compose apply.
4. Do not commit or log the password value.

## Final decision

**READY FOR SOAK**

Leave `/hive/code-server.old` untouched for a minimum of seven (7) days before cleanup.
