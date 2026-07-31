# Hotio (qbittorrent) — Dry Run Review

**Date:** 2026-07-30  
**Decision:** **APPROVED** for execute

## Dry-run summary

| Item | Value |
|---|---|
| Source | `/hive/Hotio/config` |
| Destination | `/mnt/monarch/appdata/hotio` |
| Size | **~21 MB** / 854 files / 15 dirs |
| Excludes | none (config only; downloads stay on hive) |
| Keep on hive | `/hive/downloads/completed` |
| Compose change | `/hive/Hotio/config` → `/mnt/monarch/appdata/hotio` only |
| Container | `qbittorrent` |
| Free SSD | 1.9 TB |

## Checks

- Source/destination paths match live mounts and `services.conf`.
- Compose diff is single volume rewrite; VPN (`VPN_ENABLED=true`), ports (8080/8118/6789), and `/hive/downloads/completed` mount unchanged.
- Ownership `fatherfrank:fatherfrank`, PUID/PGID 1000 — OK.
- WireGuard + Privoxy config included under `config/` — must be preserved (rsync `-aHAX`).

## Blast radius (accepted)

1. Stopping `qbittorrent` briefly drops **NZBGet** (uses `network_mode: container:qbittorrent`). Restart NZBGet after Hotio is healthy.
2. VPN tunnel re-establishes on start — expect short WebUI delay; verify port 8080 and 6789 (NZBGet) after.
3. Live project currently `/hive/Hotio/compose.yml`; execute starts from `services/Hotio/compose.yml`.

## Expected downtime

~2–5 minutes (stop → 21 MB copy → apply → VPN start → smoke).
