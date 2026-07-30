# crafty

## Overview
- Purpose: Crafty Controller (Minecraft server manager)
- Category: Games
- Current lifecycle state: Imported (Phase 10.75) — still running from prior orchestrator until cutover
- Importance level: Operational

## Repository Location
- Service directory: `services/crafty/`
- Compose file: `services/crafty/compose.yaml`
- Documentation path: `Documentation/services/crafty/crafty.md`

## Runtime Information
- Container names: big-bear-crafty
- Restart policy: unless-stopped
- Environment files: `.env.example` (and `.env` locally where secrets are required)

## Operational Notes
- Phase 10.75 imported compose into the repository without changing bind mounts or storage locations.
- Future Phase 11 may migrate config to `/mnt/monarch/appdata` using `scripts/migration/services.conf`.

## Known Issues
- See `Validation/Phase10.75/crafty/Diff.md` for live-vs-CasaOS differences captured at import.
