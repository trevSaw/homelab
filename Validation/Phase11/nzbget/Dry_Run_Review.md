# NZBGet — Dry Run Review

**Date:** 2026-07-30  
**Decision:** **APPROVED** for execute

## Dry-run summary

| Item | Value |
|---|---|
| Source | `/hive/NZBget/config` |
| Destination | `/mnt/monarch/appdata/nzbget` |
| Full source tree | 140 GB / 281 files / 54 dirs (mostly excluded) |
| Migratable after excludes | **~1.3 MB** / 10 files |
| Excludes | `downloads/**`, `*.log`, `nzbget.log` |
| Keep on hive | `/hive/downloads`, `/hive/NZBget/config/downloads` |
| Compose change | `/hive/NZBget/config` → `/mnt/monarch/appdata/nzbget` only |
| Free SSD | 1.9 TB |

## Path / exclusion checks

- **Source correct:** live bind is `/hive/NZBget/config` → `/config`.
- **Destination correct:** `/mnt/monarch/appdata/nzbget` (does not exist yet).
- **Exclusions correct and critical:** nested `config/downloads` ≈ 110 GB and `nzbget.log` ≈ 30 GB must stay off SSD. Active download paths are already `MainDir=/downloads` → host `/hive/downloads`.
- **Compose scope:** single-line volume rewrite; `/hive/downloads` mount unchanged; `network_mode: container:qbittorrent` unchanged.

## Ownership / permissions

- Source: `fatherfrank:fatherfrank` (`drwxrwxr-x`), PUID/PGID=1000 — matches image.
- No recursive chown of `/mnt/monarch/appdata` will be performed.

## Operational notes (accepted)

1. Live stack is Portainer project `/data/compose/33` (file also at `/mnt/monarch/appdata/portainer/compose/33`). Execute will stop `nzbget` by name and start from `services/NZBget/compose.yml`.
2. Repo image is `ghcr.io/hotio/nzbget`; Portainer file still lists `cr.hotio.dev/hotio/nzbget`. Running container already uses `ghcr.io/hotio/nzbget:latest` — acceptable.
3. Extra live mount `/hive/NZBget/config/scripts` → `/scripts` is redundant once `/config` contains `scripts/` — not required in proposed compose.
4. NZBGet shares network namespace with `qbittorrent` — Hotio must remain up during this migration.
5. Rollback rename of source will move the full 140 GB tree (including excluded downloads/log) to `.old` — expected; do not delete.

## Proposed compose diff

```diff
-        source: /hive/NZBget/config
+        source: /mnt/monarch/appdata/nzbget
```

## Expected downtime

~1–3 minutes (stop → copy ~1.3 MB → apply compose → start). VPN/network for NZBGet continues to come from qbittorrent.

## STOP criteria for execute

- Verification file/dir/checksum mismatch
- Container fails to start or cannot reach WebUI via qbittorrent network (port 6789)
- Any write into `/hive/downloads` or attempt to copy excluded trees onto SSD
