# Uchiyomi (manga / manhwa / webtoon acquisition + reader)

Uchiyomi is a self-hosted, multi-user manga/manhwa/webtoon **reader that also
fetches**. It owns a CBZ/CBR/image-folder library *and* pulls new chapters from
sources you enable, in one app. It is the "all-in-one *arr stack for manga":
discover → grab → monitor → serve → read in a single container plus sidecars.

Uchiyomi remains the **acquisition + sole writer** of its media. As of
2026-10-08 (ADR-0018) Kavita reads `/hive/comics/uchiyomi` **read-only** and
indexes it as a dedicated `Uchiyomi` library for mobile/offline reading. It does
**not** use Prowlarr, qBittorrent, NZBGet, NZBgeek or any external download
client, and Uchiyomi does not depend on Kavita (no API bridge; filesystem only).
See the "Kavita integration (implemented)" section below.

## Runtime

| Item | Value |
| --- | --- |
| Containers | `uchiyomi`, `uchiyomi-flaresolverr`, `uchiyomi-suwayomi` |
| App image | `ghcr.io/angelosha/uchiyomi` @ digest for v0.55.6 (see `Versions.md`) |
| Solver image | `ghcr.io/flaresolverr/flaresolverr:v3.5.2` (pinned by tag+digest) |
| Engine image | `ghcr.io/suwayomi/suwayomi-server:v2.3.2243` (pinned by tag+digest) |
| Restart policy | `unless-stopped` |
| Runtime user | `PUID=1000`, `PGID=1000` |
| Timezone | `TZ=Etc/UTC` |
| Library (owned) | `/hive/comics/uchiyomi/library` → `/library` |
| Downloads | `/hive/comics/uchiyomi/downloads` → `/library-dl` |
| Source pack | `/hive/comics/uchiyomi/sources` → `/sources` (read-only, empty) |
| App state (Postgres) | `/mnt/monarch/appdata/uchiyomi/data` → `/data` |
| App config (secrets) | `/mnt/monarch/appdata/uchiyomi/config` → `/config` |
| Image cache | `/mnt/monarch/appdata/uchiyomi/cache` → `/cache` |
| Backups | `/mnt/monarch/appdata/uchiyomi/backups` → `/backups` |
| Engine data | `/mnt/monarch/appdata/uchiyomi/suwayomi` → engine datadir |
| Networks | `proxy` (external, Traefik) + `uchiyomi_internal` (stack-private) |
| Host ports | **none** (Traefik-only ingress) |
| Web UI | `https://uchiyomi.fatherfankscloud.uk` via Traefik |
| Memory limits | app `1g`, solver `2g` (+`shm_size: 1gb`), engine `1536m` |

Ingress is Traefik-only; no host port is published. The solver and engine are
reachable only on `uchiyomi_internal`.

## Acquisition model (important)

Uchiyomi uses **its own downloader**. It does **not** use Prowlarr, Jackett,
qBittorrent, NZBGet, NZBgeek or any external indexer/download client, and none
should be wired to it. Nothing is fetched until a source is enabled.

Sources are added by three routes:

1. **Bundled MangaDex** (official public API) — works with no setup.
2. **Generic engines** (Madara / MangaThemesia / Manganato site families) — paste
   a site homepage under **Admin → Providers → Add a site**.
3. **Mihon/Tachiyomi extensions** — via the bundled `uchiyomi-suwayomi` engine;
   point **Admin → Extensions** at an extension repository you trust, then
   install extensions with a click.

Uchiyomi hosts no content and ships no default source or extension repository.
Running existing owned files is legitimate; fetching from third-party sites is
the operator's responsibility under those sites' terms and local law.

## Prerequisites

Host directories (owned `1000:1000`), already created:

```bash
mkdir -p /hive/comics/uchiyomi/{library,downloads,sources}
mkdir -p /mnt/monarch/appdata/uchiyomi/{data,config,cache,backups,sources,suwayomi}
chown -R 1000:1000 /hive/comics/uchiyomi /mnt/monarch/appdata/uchiyomi
```

The `proxy` external Docker network must already exist (shared with Traefik).

## Deployment

```bash
cd services/uchiyomi
cp .env.example .env          # already present; adjust if needed
docker compose config -q      # structural validation
docker compose up -d
docker compose ps
```

Then open `https://uchiyomi.fatherfankscloud.uk`, **create the admin account in
the browser** (there is no default password), and configure sources under
**Admin → Providers** / **Admin → Extensions**.

## Healthcheck

The app is probed at `GET /livez` (`/livez`, not `/healthz`, so a database blip
does not mark the app unhealthy); the solver at `GET :8191/`; the engine by
opening its socket and expecting HTTP `200`/`401`. These mirror upstream's own
probes.

## Backup and restore

- Back up `/mnt/monarch/appdata/uchiyomi` (embedded Postgres + config) and, if
  you want the downloaded chapters, `/hive/comics/uchiyomi/downloads`.
- The app keeps a nightly database dump in `/backups` (`BACKUP_KEEP=14`).
- Restore by placing appdata back and recreating the stack.

## Upgrade procedure

See `Versions.md`. In short: resolve the new version/digest, bump `compose.yaml`
and `Versions.md`, then `docker compose pull && docker compose up -d`. Volumes
and the database migrate themselves in place.

## Kavita integration (implemented, ADR-0018)

Kavita reads Uchiyomi's media directly from the shared filesystem — **no
duplication, no API bridge, no symlinks**. Uchiyomi remains the only writer.

| | Host path | Container path | Mode |
| --- | --- | --- | --- |
| Uchiyomi | `/hive/comics/uchiyomi/downloads` | `/library-dl` | rw |
| Uchiyomi | `/hive/comics/uchiyomi/library` | `/library` | rw |
| Kavita | `/hive/comics/uchiyomi` | `/uchiyomi` | **ro** |

- Kavita's `services/kavita/compose.yaml` adds the read-only mount and indexes
  `/uchiyomi` as the `Uchiyomi` library (type Manga, Archive + Images).
- Kavita never mounts Uchiyomi's Postgres/config/cache/backups, so its own DB and
  Kavita's libraries are unaffected.
- New chapters Uchiyomi writes are picked up on the next Kavita library scan
  (Kavita folder watching is disabled server-side).
- Do **not** point Kavita at `/library-dl` in isolation; the shared root
  `/uchiyomi` covers download and promoted content. Uchiyomi's `Move to library`
  (downloads → library) is optional and safe either way.

## Known limitations

- **Source availability is operator-supplied.** Korean manhwa/webtoon coverage
  depends on the extensions/sites you add (MangaDex covers a large share).
- **Webtoon/vertical handling is a first-class feature** (continuous vertical
  scroll, multi-chapter, pinch-zoom), unlike paged-first readers.
- Extensions run in a separate JVM container (~768 MB heap); they are not native.
- Uchiyomi edits only two metadata fields and never writes back to source sites;
  it is deliberately not a full library manager like Kavita.
- Upstream publishes only `latest`, so this repo pins by digest.
