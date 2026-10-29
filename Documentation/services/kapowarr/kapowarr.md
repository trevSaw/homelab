# kapowarr

## Overview
- Purpose: Comic book manager (comic acquisition + library automation)
- Category: Media
- Current lifecycle state: Prepared / awaiting approval (not deployed)
- Importance level: Operational

## Repository Location
- Service directory: `services/kapowarr/`
- Compose file: `services/kapowarr/compose.yaml`
- Documentation path: `Documentation/services/kapowarr/kapowarr.md`

## Runtime Information
- Container names: kapowarr
- Image: `mrcas/kapowarr:v1.3.2` (pinned; see `services/kapowarr/Versions.md`)
- Runtime identity: `PUID=1000`, `PGID=1000`, `TZ=Etc/UTC`
- Restart policy: unless-stopped
- Networks: `proxy` (external) + `hotio_default` (external, defined in Compose as `hotio`)
- Host ports: none (Traefik-only ingress)
- Traefik host: `kapowarr.fatherfankscloud.uk` (resolver `le`)
- Memory limit: 512M
- Environment files: `.env.example` (values inlined; no secrets)

## Storage
- Config/database: `/mnt/monarch/appdata/kapowarr` → `/app/db`
- Download staging: `/hive/downloads/completed/kapowarr` → `/app/temp_downloads`
- Comics root: `/hive/library/Kavita/Comics` → `/comics` (served by Kavita)

## Integrations
- qBittorrent (`http://qbittorrent:8080` on `hotio_default`): external torrent
  client. Kapowarr automatically submits category `kapowarr`; qBittorrent
  creates the category on first use. Remote path mapping in Kapowarr:
  `/downloads/kapowarr` (remote) → `/app/temp_downloads` (local).
- Kavita: reads `/hive/library/Kavita/Comics`. Filesystem-level integration only;
  no API link.
- Prowlarr: not integrated (Kapowarr V1.3.2 does not support Prowlarr).
- NZBGet: not integrated (V1.3.2 has no Usenet support).

## Health
- Homelab healthcheck: `GET http://127.0.0.1:5656/api/public` via `python3`.
- This is a homelab probe; Kapowarr has no upstream Docker `HEALTHCHECK` and no
  upstream health endpoint.

## Prerequisites
- Create `/mnt/monarch/appdata/kapowarr` (1000:1000).
- Create `/hive/downloads/completed/kapowarr` (1000:1000).
- Change ownership of `/hive/library/Kavita/Comics` recursively to `1000:1000`
  (separately approved). Kavita runs as root and only reads the library; no
  other service depends on root ownership; no extended ACLs are present.

## Manual post-deployment configuration
See `services/kapowarr/README.md` ("Manual post-deployment configuration").
High level: add qBittorrent client, leave download folder at
`/app/temp_downloads`, add the remote path mapping, add root folder `/comics`.

## Known Issues
- Beta software; metadata matching and download search are actively developed.
- Requires the comics root to be writable by uid/gid 1000.

## Evidence
- Upstream source/docs: Casvt/Kapowarr at tag V1.3.2 (compose, Dockerfile,
  entrypoint, docs, download-client code).
- Upstream release: GitHub release V1.3.2 (2026-09-14).
- Registry: Docker Hub `mrcas/kapowarr` tag `v1.3.2`.
- qBittorrent behaviour: qBittorrent 4.5.5 session source (auto-creates missing
  category on add; AutoTMM default true).
