# Phase 11 — Honcho Migration Report

**Service:** honcho  
**Batch:** 03  
**Final status:** SOAK FAILED  
**Completed:** 2026-07-30T11:02:00Z

## Summary

Already-migrated inventory succeeded (data already under `/mnt/monarch/appdata/honcho`). Smoke **failed**: Postgres cannot open data files due to ownership/permissions (uid 1000 vs postgres role). No migration mutations were applied.

## Paths (confirmed)

| Role | Path |
|------|------|
| Postgres | `/mnt/monarch/appdata/honcho/postgres` |
| Redis | `/mnt/monarch/appdata/honcho/redis` |
| Compose project | `/mnt/monarch/appdata/honcho/compose.yml` |

## Required operator remediation (before READY FOR SOAK)

1. Schedule a Honcho maintenance window.
2. Stop stack; fix Postgres data ownership to the image’s `postgres` UID (often `999`) **or** align the compose user — only with a known-good backup.
3. Confirm `psql -U postgres -c 'SELECT 1'` succeeds.
4. Confirm `https://honcho.fatherfankscloud.uk/` responds.
5. Re-run Phase 11 Honcho smoke and update this report.

## Final decision

**SOAK FAILED**
