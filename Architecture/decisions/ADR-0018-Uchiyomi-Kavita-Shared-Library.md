---
title: ADR-0018 Uchiyomi → Kavita Shared Library
document_type: ADR
service: [uchiyomi, kavita]
owner: Homelab
status: Accepted
version: 1.0.0
related_documents:
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/HomelabArchitectureStandard.md
  - Architecture/decisions/ADR-0017-Kapowarr-Comic-Management.md
  - services/uchiyomi/README.md
  - services/kavita/README.md
  - Documentation/services/kavita/kavita.md
---

# ADR-0018 — Uchiyomi → Kavita Shared Library

## Status

**Accepted** — implemented and validated on `mocha` (2026-10-08). Companion to
ADR-0017 (Kapowarr), which shares the same "one library, one writer" model.

## Context

Uchiyomi (`services/uchiyomi`) is the manga/manhwa/webtoon **acquisition**
service: it discovers, downloads and organises chapters into CBZ files
(`Series/Chapter N.cbz`, each with a `ComicInfo.xml`). It is the only writer of
its media.

Kavita (`services/kavita`) is the **reader/serving** layer: it indexes a
library and serves it to clients (web PWA and OPDS/PSE-compatible mobile
readers) for home and offline reading.

At inspection time:

- Uchiyomi's acquired media lived on the host at
  `/hive/comics/uchiyomi/downloads` (bind mount → `/library-dl`), with an
  empty owned library at `/hive/comics/uchiyomi/library` (→ `/library`).
  Ownership was `1000:1000`.
- Uchiyomi's database (`/mnt/monarch/appdata/uchiyomi/data`, embedded Postgres)
  tracked 1 series / 207 CBZ books with `root=/library-dl`.
- Kavita read four existing libraries under `/hive/library/Kavita/` and had no
  visibility of Uchiyomi's media.
- The goal is **filesystem-level** sharing (not Uchiyomi's web UI, not an API
  bridge), so Kavita can index/serve the very files Uchiyomi downloaded and
  mobile clients can pull them for offline reading.

## Decision

Expose Uchiyomi's media root to Kavita as a **read-only bind mount** and add a
dedicated Kavita library. Uchiyomi remains the sole writer.

- **Shared media path (host):** `/hive/comics/uchiyomi`
- **Uchiyomi view:** `/hive/comics/uchiyomi/downloads` → `/library-dl` (rw),
  `/hive/comics/uchiyomi/library` → `/library` (rw) — unchanged.
- **Kavita view:** `/hive/comics/uchiyomi` → `/uchiyomi` **`:ro`** (one mount
  covering both `downloads/` and promoted `library/`); new in
  `services/kavita/compose.yaml`.
- **Kavita library:** `Uchiyomi`, type **Manga**, root `/uchiyomi`, file types
  Archive + Images, folder watching on. Created via the Kavita API; Kavita's
  own DB stores the library/metadata.
- **Ownership/permissions:** media stays `1000:1000`; Kavita runs as root and
  reads the tree read-only, so no ownership change is required.
- **Image pinning:** Kavita's `latest` tag is now pinned by manifest digest
  (`jvmilazz0/kavita@sha256:1f2acae…`) per repository convention.

Kavita is **not** given write access, and Uchiyomi's storage path/database is
left untouched. No sync service, API bridge, or symlink is introduced.

## Why the whole media root (not just `downloads/`)

Kavita aborts a scan if **any** library root folder is empty (a guard against
disconnected mounts). At decision time `/hive/comics/uchiyomi/library` was
empty, so a two-folder library could not scan. Mounting the single non-empty
root `/uchiyomi` also makes future promoted chapters under `library/`
immediately visible without a Kavita reconfiguration.

The root contains only Uchiyomi media (`downloads/`, `library/`,
`sources/`). It never exposes Uchiyomi's Postgres, config, cache or backups —
those live on `/mnt/monarch/appdata/uchiyomi` and are deliberately not mounted.

## Consequences

Positive:

- Single source of truth: Uchiyomi writes, Kavita reads; no duplication or
  copy of media.
- Least privilege: Kavita's new mount is read-only; Uchiyomi is unchanged.
- Kavita's existing libraries, config and DB are untouched; a new library was
  added, so nothing was moved.
- Mobile offline reading works through standard Kavita/OPDS plumbing: the OPDS
  feed advertises per-chapter CBZ acquisition links and PSE page streaming, so
  any OPDS-acquisition-capable iOS reader can cache chapters locally.

Negative / accepted risks:

- `/hive/comics/uchiyomi/downloads` is Uchiyomi's live download target. Kavita
  read-only scanning is safe, but a mid-write scan could log a transient
  archive error; Uchiyomi writes chapters as complete CBZ files.
- The mount is broader than the acquired-media subfolder (includes the empty
  `sources/` pack). This is inert and read-only.
- Kavita folder watching is disabled at the Kavita server level, so new
  downloads appear after a library scan (manual or scheduled), not instantly.

## Alternatives considered

- **Point Kavita at `/hive/comics/uchiyomi/downloads` only:** rejected — the
  library would not follow Uchiyomi's "move to library" promotion, and the
  empty promoted dir could later force a reconfiguration.
- **Two Kavita folders (`downloads` + `library`):** rejected at this time —
  Kavita aborts scans when a root is empty; `library/` is empty.
- **Symlink Uchiyomi media into Kavita's existing tree:** rejected — a direct
  bind mount is simpler and avoids symlink semantics across containers.
- **Change Uchiyomi's storage path / re-download:** rejected — unnecessary and
  risks its database/subscription state.
- **Give Kavita write access:** rejected — Kavita only needs to read.

## References

- Uchiyomi: `services/uchiyomi/README.md`, `services/uchiyomi/compose.yaml`
- Kavita: `services/kavita/README.md`, `services/kavita/compose.yaml`
- ADR-0017 — Comic Book Management (Kapowarr)
