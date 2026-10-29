# Kapowarr (comic book manager)

Kapowarr builds and manages a digital comic book library, fitting the *arr
family of tools. It searches (via its built-in GetComics indexer), downloads
(direct links and/or an external torrent client), imports, renames and
optionally converts issues into a root folder that Kavita serves.

This directory is the repository source of truth for the Kapowarr Compose
stack. It is prepared for approval; it is **not** deployed by this document.

## Runtime

| Item | Value |
| --- | --- |
| Container name | `kapowarr` |
| Image | `mrcas/kapowarr:v1.3.2` (pinned; see `Versions.md`) |
| Restart policy | `unless-stopped` |
| Runtime user | `PUID=1000`, `PGID=1000` (via image entrypoint; no `user:` key) |
| Timezone | `TZ=Etc/UTC` |
| Config | `/mnt/monarch/appdata/kapowarr` → `/app/db` |
| Download staging | `/hive/downloads/completed/kapowarr` → `/app/temp_downloads` |
| Comics root | `/hive/library/Kavita/Comics` → `/comics` |
| Networks | `proxy` (external) and `hotio` → live `hotio_default` (external) |
| Host ports | none (Traefik-only ingress) |
| Web UI | `https://kapowarr.fatherfankscloud.uk` via Traefik |
| Memory limit | `512M` (no CPU limit) |

There is **no published host port**. Ingress is Traefik-only, consistent with
the Docker Compose Standard (omit `ports:` unless a temporary debugging need is
documented).

## External resources

Required external Docker networks (pre-created on the host):

- `proxy`
- `hotio_default` (referenced in Compose as `hotio`)

No new network is introduced.

Required external paths (must exist before first start; see Prerequisites):

- `/mnt/monarch/appdata/kapowarr`
- `/hive/downloads/completed/kapowarr`
- `/hive/library/Kavita/Comics`

## Prerequisites

1. **Kapowarr appdata** — `mkdir -p /mnt/monarch/appdata/kapowarr`, owned
   `1000:1000`.
2. **Download staging** — `mkdir -p /hive/downloads/completed/kapowarr`, owned
   `1000:1000` (writable by both qBittorrent at `PUID=1000` and Kapowarr).
3. **Comics root ownership** — `/hive/library/Kavita/Comics` is the Kapowarr
   root and must be writable by uid/gid 1000. It is currently `root:root`.
   Recursively change ownership to `1000:1000` in a separately approved step.

   Rationale for the ownership change:

   - Kapowarr runs as `1000:1000`.
   - The tree is currently `root:root` (`755`), so `1000` cannot write it.
   - Kavita runs as `root` and only reads the library, so it is unaffected.
   - No other service depends on root ownership of this tree.
   - The tree has no extended ACLs (ZFS `acltype=off`; `getfacl` shows POSIX
     mode bits only), so a recursive `chown` is the complete fix.
   - uid/gid 1000 is the established shared-media convention
     (`/hive/library` is 775 `fatherfrank`; `Books`/`fanfic` are 1000-owned).

   Do not otherwise alter contents, permissions, ACLs or directory structure.
   Do not move, rename or delete existing comics.

## Deployment

Prepared and reviewed through the governance workspace, then applied behind the
approval gate and deployed through the controlled Docker mechanism. This stack
must not be started outside that process.

```bash
# After the workspace patch is approved and applied to the canonical repo:
cd services/kapowarr
docker compose -f compose.yaml config -q   # structural validation
# Deployment is performed via the approved controlled mechanism, not manually.
```

## Manual post-deployment configuration (Kapowarr UI)

These are performed in the Kapowarr web UI after the container is running.
None of them belong in Compose.

1. **Download Client → qBittorrent**
   - Base URL: `http://qbittorrent:8080` (Docker DNS on `hotio_default`).
   - Username/password: enter here; stored in Kapowarr's database only.
   - Do **not** add a category field. Kapowarr automatically submits its fixed
     category `kapowarr`. qBittorrent creates that category automatically on the
     first torrent add; it is intentionally **not** created manually.
2. **Download Folder** — leave the default `/app/temp_downloads` (already mapped
   to `/hive/downloads/completed/kapowarr`).
3. **Remote Path Mappings** — add a mapping for the qBittorrent client:
   - Remote path: `/downloads/kapowarr`
   - Local path: `/app/temp_downloads`
4. **Root Folder** — add `/comics` (maps to `/hive/library/Kavita/Comics`).
5. **Indexers** — configure the built-in GetComics indexer as desired. Prowlarr
   is **not** integrated (V1.3.2 does not support Prowlarr).
6. Do **not** configure NZBGet (V1.3.2 has no Usenet support).
7. Optionally review Media Management (rename, extraction, conversion) and
   Download settings. The default seeding handling in V1.3.2 is **Copy**: for
   torrents, files are copied in for immediate import while the client keeps
   seeding until completion, after which the client's copy is removed. Leave the
   default unless there is a reason to change it.

## Healthcheck

The Compose healthcheck probes `GET http://127.0.0.1:5656/api/public`, which is
an unauthenticated endpoint returning HTTP 200, using `python3` (present in the
image). **This is a homelab healthcheck.** Kapowarr has no upstream Docker
`HEALTHCHECK` and no upstream health endpoint; this probe is not authoritative
upstream behaviour.

## Backup and restore

- Back up `/mnt/monarch/appdata/kapowarr` (database, including V1.3.2 database
  backups) and the library under `/hive/library/Kavita/Comics`.
- Restore by placing the appdata back and recreating the service through the
  approved deployment path.

## Upgrade procedure

1. Confirm the target upstream release and the one-minor-version-at-a-time
   requirement.
2. Update the tag in `compose.yaml` and `Versions.md`.
3. Recreate through the approved deployment path and verify the healthcheck.

## Known limitations / troubleshooting

- Beta software; comic metadata matching and the download-search system are
  actively developed.
- `http://qbittorrent:8080` requires the Kapowarr container to be on
  `hotio_default`; verify with `docker inspect kapowarr`.
- Because the download staging area and the comics root are on the same ZFS
  dataset (`hive`), import moves are same-filesystem renames. Placing either on
  a different dataset would change this to a copy.
- The download staging directory must never contain unrelated files: Kapowarr's
  "Empty Download Folder" operation deletes non-active files in it.

## Lifecycle

State: **Prepared / awaiting approval.** Infrastructure facts (image, ports,
volumes, networks, endpoint) are pinned; deployment is gated.
