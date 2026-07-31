# Phase 11 — Batch 06 Summary (Jellyfin)

**Date:** 2026-07-31  
**Label:** Stored as **Batch06** (Batch01–05 already exist). Scope: Jellyfin only.

## Overall summary

Jellyfin config migration **completed successfully** after the framework checksum locale bug was fixed. Cutover is live on `/mnt/monarch/appdata/jellyfin`. Batch is **READY FOR SOAK**.

## Services / execution order

| Order | Service | Result | Notes |
|---|---|---|---|
| 1 | Jellyfin | **READY FOR SOAK** | Config → appdata; ephemeral excludes; `.old` retained |

## Timings (approx.)

| Service | Copy size | Downtime |
|---|---|---|
| Jellyfin | 7.0 GB / 41,099 files (excludes ~3.5 GB) | ~few minutes (stop → copy → verify → compose → start) |

## Issues and resolutions

1. **Checksum false positive (initial abort)** — locale `sort` / Hangul path ordering. **Fixed** in framework (`LC_ALL=C` set comparison + Unicode regression suite). See [Framework_Fix_Checksum_Locale.md](../Framework_Fix_Checksum_Locale.md).
2. **Live drift after abort** — expected; resolved by deleting staged copy and re-copying with container stopped.
3. **Compose proposed validation missing `.env`** — `update-compose.sh` now stages project `.env` into the proposed dir for validation only.

## Outstanding warnings

- Leave `/hive/jellyfin/config.old` ≥ 7 days.
- Do **not** run recursive `chown` on `/mnt/monarch/appdata`.
- Live cache/transcodes/log dirs will refill on the SSD as Jellyfin runs — expected.

## Rollback summary

| Service | Rollback tree |
|---|---|
| Jellyfin | `/hive/jellyfin/config.old` |

## Recommended next actions

1. Soak Jellyfin ≥ 7 days; then cleanup `.old` only after confirming backups cover the new path.
2. Optionally migrate CasaOS *arr services once their `services.conf` + compose entries are validated for live cutover.
3. Do not delete `.old` automatically.

## Operator notes

- **Succeeded:** Jellyfin
- **Failed:** none
- **7-day soak:** **Yes — begin now**
- **Proceed to next batch:** Yes, after operator review; Jellyfin no longer blocks Batch 07 planning
