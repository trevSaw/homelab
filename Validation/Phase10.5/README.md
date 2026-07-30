# Phase 10.5 — Migration Framework

Personal homelab (mocha). **Framework only** for Phase 10.5 — no live migrations in this phase.

## Policy

- App config/state → `/mnt/monarch/appdata/<service>`
- Large datasets stay on `/hive`
- **Exception:** Ollama config **and** models → `/mnt/monarch/appdata/ollama` (relocatable later via `services.conf`)

## Quick start (dry-run)

```bash
./scripts/migration/inventory.sh --all
./scripts/migration/compose-path-check.sh
./scripts/migration/run-migration.sh --dry-run code-server
```

Read the **summary block** at the end of each command. Full narrative: [Dry_Run_Review.md](Dry_Run_Review.md) (regenerate after hardening if desired).

## Documents

| File | Purpose |
|------|---------|
| [Migration_Inventory.md](Migration_Inventory.md) | Paths, drift, expected warnings |
| [Compose_Compatibility_Report.md](Compose_Compatibility_Report.md) | Mount classification + investigations |
| [Migration_Matrix.md](Migration_Matrix.md) | Order / risk / rollback |
| [Deployment_Checklist.md](Deployment_Checklist.md) | Operator checklist |
| [Phase10.5_Framework_Report.md](Phase10.5_Framework_Report.md) | Hardening summary |

## Scripts

Modular tools under `scripts/migration/`. Default `--dry-run`. Mutations need `--execute`. Compose writes need `--apply-compose`.

## Expected warnings

See inventory doc. Do not “fix” git-dirty or dry-run pending-verify warnings by suppressing them — they are intentional operator signals.
