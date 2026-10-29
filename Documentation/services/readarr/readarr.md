# readarr

## Overview
- Purpose: Book manager (Readarr develop)
- Category: Media
- Current lifecycle state: **Deprecated** — retired upstream (June 2025); metadata servers dead. Container stopped. Replaced by `services/chaptarr` (ADR-0009).
- Importance level: Operational

## Repository Location
- Service directory: `services/readarr/`
- Compose file: `services/readarr/compose.yaml`
- Documentation path: `Documentation/services/readarr/readarr.md`

## Runtime Information
- Container names: readarr
- Restart policy: unless-stopped
- Environment files: `.env.example` (and `.env` locally where secrets are required)

## Operational Notes
- Phase 10.75 imported compose into the repository without changing bind mounts or storage locations.
- **Do not start** this container. Readarr is retired upstream; use Chaptarr (`services/chaptarr`). No DB migration exists between Readarr and Chaptarr — point Chaptarr at the library folders and let it re-match.

## Known Issues
- See `Validation/Phase10.75/readarr/Diff.md` for live-vs-CasaOS differences captured at import.
