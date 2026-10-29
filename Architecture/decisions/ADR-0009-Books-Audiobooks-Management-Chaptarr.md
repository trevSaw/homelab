---
title: ADR-0009 Book & Audiobook Management — Chaptarr
document_type: ADR
service: chaptarr
owner: Homelab
status: Draft
version: 0.1.0
last_reviewed: 2026-09-21
related_documents:
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/HomelabArchitectureStandard.md
  - services/readarr/README.md
  - services/chaptarr/README.md
  - services/audiobookshelf/README.md
---

# ADR-0009 — Book & Audiobook Management (Chaptarr + Audiobookshelf)

## Status

**Draft** — pending Architecture Review Board sign-off. Compose stacks added under
`services/chaptarr/` and `services/audiobookshelf/` for validation (lifecycle: Draft/Review).

## Context

The homelab needs automated acquisition of **eBooks and audiobooks** (including
publisher audiobook-drama editions such as Graphic Audio releases, e.g. *Red Rising:
Saga*) and a listening/reading frontend.

Existing state:

- **Readarr** (`services/readarr`) was the intended manager, but the upstream project
  was **retired June 2025**; its metadata servers are dead, so it can no longer
  reliably search or match books. The container is stopped.
- **Kavita** (running) serves eBooks/comics/manga but has **no audiobook support** in
  the official image (`jvmilazz0/kavita:latest`); upstream explicitly declined an
  audiobook feature.
- Acquisition fabric already exists: **Prowlarr** (indexers), **qBittorrent** +
  **NZBGet** (download clients) on the `hotio_default` network.

## Decision

Adopt **Chaptarr** (`chaptarr/chaptarr`, pinned `0.9.958`) as the book/audiobook
manager — the active Readarr fork managing **eBooks and audiobooks in one instance**
with its own working metadata pipeline, narrator/edition-aware matching, multi-edition
support, and optional MP3→M4B conversion.

Pair it with **Audiobookshelf** (`ghcr.io/advplyr/audiobookshelf:v2.36.0`) as the
audiobook playback frontend, keeping **Kavita** as the eBook frontend.

```
Prowlarr (indexers) → Chaptarr (grab/rename both formats) → qBittorrent / NZBGet
        │
        ├── /hive/library/Kavita/Books   → Kavita          (eBooks)
        └── /hive/library/Audiobooks     → Audiobookshelf  (audiobooks)
```

Library layout (all on `/hive`, a single ZFS filesystem → hardlink-safe imports):

| Role | Host path | Container path |
|---|---|---|
| Chaptarr config | `/mnt/monarch/appdata/chaptarr` | `/config` |
| Downloads | `/hive/downloads/completed/Readarr` | `/downloads` |
| eBooks | `/hive/library/Kavita/Books` | `/ebooks` |
| Audiobooks | `/hive/library/Audiobooks` | `/audiobooks` |
| Audiobookshelf config | `/mnt/monarch/appdata/audiobookshelf/config` | `/config` |
| Audiobookshelf metadata | `/mnt/monarch/appdata/audiobookshelf/metadata` | `/metadata` |

**Retire Readarr:** mark lifecycle **Deprecated**; do not start. No DB migration to
Chaptarr exists (incompatible metadata providers) — point Chaptarr at the library
folders and let it re-match.

## Alternatives Considered

| Alternative | Verdict | Rationale |
|---|---|---|
| **Lidarr** | Rejected | Music manager only; cannot manage books/audiobooks. |
| **Readarr** (continue) | Rejected | Retired upstream; metadata servers dead; cannot search/match. |
| **Chaptarr + Kavita fork** (LeviBickel nightly) | Rejected for now | Single-frontend option, but a beta nightly fork diverging from upstream; audiobook UX weaker than Audiobookshelf. |
| **Jellyfin for audiobook playback** | Rejected for now | No new frontend, but weak resume/audiobook UX on long files. |
| **Chaptarr + Audiobookshelf** | **Adopted** | Best-in-class playback (native mobile apps, sleep timer, chapters, per-second progress); Chaptarr-native integration; Kavita unchanged for eBooks. |

## Consequences

**Positive**

- One manager handles both formats; metadata matching actually works (own pipeline).
- Graphic Audio / audiobook-drama editions can be stored as distinct editions with
  narrator tags.
- Playback frontends are purpose-built; no regression to existing Kavita setup.
- Reuses existing Prowlarr/download-client fabric; hardlinks work on single ZFS `/hive`.

**Negative**

- **Two** frontends for books (Kavita for eBooks, Audiobookshelf for audio) instead of one.
- Chaptarr is **beta** software; its metadata pipeline is actively developed and may
  mis-match obscure editions (Graphic Audio titles may need manual/interactive search).
- Chaptarr does not inherit Readarr's existing DB/config.
- Audiobookshelf config must remain on local SSD (SQLite lock issues over NFS).

## Implementation Notes

1. Deploy `services/chaptarr` and `services/audiobookshelf` per Docker Compose
   Standard v1.0 (pinned images, healthchecks, logging rotation, resource limits,
   Traefik labels on `proxy`, Chaptarr on `proxy` + `hotio`).
2. Create host dirs and set ownership `1000:1000` (`PUID/PGID`, `UMASK=002`).
3. Prowlarr: add Chaptarr as a Readarr-compatible app; sync book indexers.
4. Chaptarr: root folders, quality profiles (ebook: EPUB preferred; audiobook:
   M4B/MP3 in a separate profile), download clients (`qbittorrent:8080`; NZBGet via
   shared netns `qbittorrent:6789`).
5. Audiobookshelf: create admin, add `/audiobooks` library; optionally enable the
   Chaptarr → Audiobookshelf refresh integration.
6. Kavita: verify `/hive/library/Kavita/Books` scan (unchanged).
7. Validation: `docker compose config` and `scripts/validate.sh` must pass before
   promotion to Production.

## Rollback

- Stop Chaptarr/Audiobookshelf containers; re-enable nothing for Readarr (retired).
- eBooks remain readable via Kavita regardless; audiobooks remain files on `/hive`.
- Remove ADR status to Draft↔Archived if the fabric is later replaced.