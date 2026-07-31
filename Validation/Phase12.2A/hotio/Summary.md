# Validation — Hotio / qBittorrent (Phase 12.2A)

**Date:** 2026-07-31  
**Result:** PASS

## Before

- Image: `cr.hotio.dev/hotio/qbittorrent:latest` (OCI label 4.5.5)
- Config: `/mnt/monarch/appdata/hotio`
- WebUI `:8080` responding

## After

- Image: `ghcr.io/hotio/qbittorrent:release-4.5.5`
- Health: healthy
- WebUI `:8080` → 200
- Config/downloads mounts unchanged

## Artifacts

- `01_before.txt`
- `compose_before.yml` / `compose_after_config.yml`
- `02_compose_up.txt`
- `03_after_inspect.txt`
