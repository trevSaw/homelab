---
title: ADR-0017 Comic Book Management — Kapowarr
document_type: ADR
service: kapowarr
owner: Homelab
status: Draft
version: 0.1.0
related_documents:
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/HomelabArchitectureStandard.md
  - Architecture/media-stack-networking.md
  - Architecture/decisions/ADR-0009-Books-Audiobooks-Management-Chaptarr.md
  - services/kapowarr/README.md
  - Documentation/services/kavita/kavita.md
---

# ADR-0017 — Comic Book Management (Kapowarr)

## Status

**Draft** — pending Architecture Review Board sign-off. A Compose stack is added
under `services/kapowarr/` (lifecycle: Prepared / awaiting approval). This ADR
records the decision; it does not authorize deployment.

## Context

The homelab already serves comics/manga through **Kavita**
(`services/kavita`, `kav.fatherfankscloud.uk`), reading
`/hive/library/Kavita/Comics`. Acquisition of comics is currently manual; there
is no *arr-family manager for comics.

Existing fabric:

- **Kavita** — comic/manga/ebook reader; reads the library read-only and writes
  only its own config.
- **qBittorrent** (Hotio, `hotio_default`) — existing torrent client with a
  Mullvad VPN egress.
- **Prowlarr** — indexer manager for the *arr suite. Kapowarr V1.3.2 does not
  support Prowlarr (it uses a built-in GetComics indexer).
- **NZBGet** — existing Usenet client. Kapowarr V1.3.2 has no Usenet support.

This mirrors the earlier book/audiobook decision (ADR-0009, Chaptarr), which was
accepted for the analogous reason: a purpose-built manager for a media type not
covered by the rest of the suite.

## Decision

Adopt **Kapowarr V1.3.2** (`mrcas/kapowarr:v1.3.2`, pinned by version tag) as
the comic book manager, deployed as `services/kapowarr/`:

- **Runtime identity:** `PUID=1000`, `PGID=1000` (image entrypoint; no `user:`),
  `TZ=Etc/UTC`, matching the shared media convention.
- **Storage:** appdata `/mnt/monarch/appdata/kapowarr`; download staging
  `/hive/downloads/completed/kapowarr`; comics root
  `/hive/library/Kavita/Comics`.
- **Networks:** existing external `proxy` and `hotio_default`; no new network.
- **Ingress:** Traefik-only at `kapowarr.fatherfankscloud.uk`; no host port.
- **Downloader:** reuse the existing qBittorrent over Docker DNS
  (`http://qbittorrent:8080`). Kapowarr submits its fixed `kapowarr` category,
  which qBittorrent auto-creates on first use. A Remote Path Mapping of
  `/downloads/kapowarr` → `/app/temp_downloads` aligns the client and Kapowarr
  path views.
- **No Usenet:** NZBGet is deliberately not integrated (V1.3.2 limitation).
- **No Prowlarr:** not supported by V1.3.2.

The existing Kavita comics library remains the root. Because Kapowarr runs as
uid/gid 1000 and the tree is currently `root:root`, a one-time, separately
approved recursive ownership change to `1000:1000` is required. Kavita runs as
root and only reads the tree, no other service depends on root ownership, and
no extended ACLs are present, so the change is self-contained.

## Consequences

Positive:

- Reuses the existing proxy/hotio networking and qBittorrent/VPN egress; no new
  infrastructure, networks, or downloader configuration.
- Keeps a single comics library already served by Kavita.
- Pinned image and documented healthcheck/resource conventions.

Negative / accepted risks:

- Kapowarr is beta software; metadata matching and download search change
  frequently.
- The ownership change touches a live Kavita library (mitigated: Kavita is root
  and read-only on the library).
- The download staging area and comics root share the `hive` dataset, so imports
  are same-filesystem renames; a future dataset move would turn these into
  copies.

## Alternatives considered

- **Run Kapowarr as root** to avoid the ownership change: rejected — violates
  the non-root and uid-1000 shared-media conventions.
- **Create a separate 1000-owned comics library and register it in Kavita**:
  rejected — duplicates the library and adds complexity for no benefit.
- **Reuse `/hive/downloads/completed/Comics`**: rejected — it is not a
  qBittorrent category and contains legacy files; Kapowarr's Empty Download
  Folder operation would risk deleting them.

## References

- Upstream: `https://github.com/Casvt/Kapowarr` (release V1.3.2).
- `Architecture/media-stack-networking.md`
- `Architecture/standards/DockerStandard.md`
- ADR-0009 — Book & Audiobook Management (Chaptarr + Audiobookshelf)
