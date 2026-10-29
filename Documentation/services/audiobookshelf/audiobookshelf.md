# audiobookshelf

## Overview
- Purpose: Audiobook + podcast streaming server
- Category: Media
- Current lifecycle state: Draft/Review (Phase 20) — deployed for validation
- Importance level: Operational

## Repository Location
- Service directory: `services/audiobookshelf/`
- Compose file: `services/audiobookshelf/compose.yaml`
- Documentation path: `Documentation/services/audiobookshelf/audiobookshelf.md`

## Runtime Information
- Container names: audiobookshelf
- Restart policy: unless-stopped
- User: `1000:1000` (ABS ignores PUID/PGID; runs via `user:`)
- Environment files: `.env.example` (values inlined; no secrets)

## Operational Notes
- Audiobooks root: `/hive/library/Audiobooks` (shared with Chaptarr).
- Config + metadata on SSD: `/mnt/monarch/appdata/audiobookshelf`.
- Native iOS/Android apps, sleep timer, chapter nav, per-second progress.
- Kavita continues to serve eBooks/comics/manga.

## Known Issues
- NFS-backed config is unsupported (SQLite lock errors) — config must stay on local SSD.