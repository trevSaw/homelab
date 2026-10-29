# chaptarr

## Overview
- Purpose: eBook + audiobook manager (Readarr successor)
- Category: Media
- Current lifecycle state: Draft/Review (Phase 20) — deployed for validation
- Importance level: Operational

## Repository Location
- Service directory: `services/chaptarr/`
- Compose file: `services/chaptarr/compose.yaml`
- Documentation path: `Documentation/services/chaptarr/chaptarr.md`

## Runtime Information
- Container names: chaptarr
- Restart policy: unless-stopped
- Environment files: `.env.example` (values inlined; no secrets)

## Operational Notes
- Replaces retired Readarr (ADR-0009). eBooks root: `/hive/library/Kavita/Books`; audiobooks root: `/hive/library/Audiobooks`; downloads: `/hive/downloads/completed/Readarr`.
- Playback frontends: Kavita (eBooks) and Audiobookshelf (audiobooks).
- Connect Prowlarr (Readarr-compatible app) and download clients (qBittorrent / NZBGet).

## Known Issues
- Beta software; pin image tag in `services/chaptarr/Versions.md`.
- No migration from Readarr DB — point at library folders and let Chaptarr match.