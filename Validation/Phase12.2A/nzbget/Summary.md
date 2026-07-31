# Validation — NZBGet (Phase 12.2A)

**Date:** 2026-07-31  
**Result:** PASS

## Before

- Image: `ghcr.io/hotio/nzbget` (untagged / latest; OCI label 25.2)
- `network_mode: container:qbittorrent`
- Config: `/mnt/monarch/appdata/nzbget`
- WebUI `:6789` → 401 (auth)

## After

- Image digest pin matching prior live image
- Health: healthy
- NetworkMode: `container:<qbittorrent-id>`
- WebUI `:6789` → 401
- Config/downloads mounts unchanged

## Artifacts

- `01_before.txt`
- `compose_before.yml` / `compose_after_config.yml`
- `02_compose_up.txt`
- `03_after_inspect.txt`
