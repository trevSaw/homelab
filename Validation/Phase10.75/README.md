# Phase 10.75 — CasaOS Retirement / Repository Import

**Date:** 2026-07-30  
**Scope:** Inventory and import remaining non-repository Docker services into `services/`.  
**Non-goals:** No `/mnt/monarch/appdata` migration, no compose modernization beyond stripping CasaOS metadata / secret extraction, no container recreation.

## Contents

| File | Description |
|---|---|
| [Import_Report.md](./Import_Report.md) | What was imported and how |
| [Service_Inventory.md](./Service_Inventory.md) | Full live inventory of import candidates |
| [Missing_Services.md](./Missing_Services.md) | Intentionally skipped / not present |
| [Validation_Summary.md](./Validation_Summary.md) | Parse, mount parity, reachability |
| `<service>/` | Per-service import, validation, and diff notes |

## Outcome

CasaOS is **no longer required as the source of truth** for the imported services. Live containers still run under their prior CasaOS/Portainer/hive projects until an intentional cutover; the repository now holds matching compose definitions for governance and future Phase 11 migration.
