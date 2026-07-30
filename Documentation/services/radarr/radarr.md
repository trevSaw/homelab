# radarr

## Overview
- Purpose: Movie collection manager
- Category: Media
- Current lifecycle state: Imported (Phase 10.75) — still running from prior orchestrator until cutover
- Importance level: Operational

## Repository Location
- Service directory: `services/radarr/`
- Compose file: `services/radarr/compose.yaml`
- Documentation path: `Documentation/services/radarr/radarr.md`

## Runtime Information
- Container names: radarr
- Restart policy: unless-stopped
- Environment files: `.env.example` (and `.env` locally where secrets are required)

## Operational Notes
- Phase 10.75 imported compose into the repository without changing bind mounts or storage locations.
- Future Phase 11 may migrate config to `/mnt/monarch/appdata` using `scripts/migration/services.conf`.

## Known Issues
- See `Validation/Phase10.75/radarr/Diff.md` for live-vs-CasaOS differences captured at import.
