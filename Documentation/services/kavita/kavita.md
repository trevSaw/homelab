# kavita

## Overview
- Purpose: Comics/manga/ebook library and mobile/offline serving layer
- Category: Media
- Current lifecycle state: Imported (Phase 10.75); Uchiyomi media integration added (ADR-0018, 2026-10-08)
- Importance level: Operational

## Repository Location
- Service directory: `services/kavita/`
- Compose file: `services/kavita/compose.yaml`
- Documentation path: `Documentation/services/kavita/kavita.md`

## Runtime Information
- Container names: kavita
- Restart policy: unless-stopped
- Environment files: `.env.example` (and `.env` locally where secrets are required)

## Operational Notes
- Phase 10.75 imported compose into the repository without changing bind mounts or storage locations.
- Future Phase 11 may migrate config to `/mnt/monarch/appdata` using `scripts/migration/services.conf`.
- Image pinned by digest `jvmilazz0/kavita@sha256:1f2acae…` (Kavita v0.8.9.1); `latest` no longer used.
- Kavita mounts Uchiyomi's media root read-only and indexes it as the `Uchiyomi`
  library (see ADR-0018):
  - Host `/hive/comics/uchiyomi` → container `/uchiyomi` **ro**.
  - Uchiyomi (uid/gid 1000) is the sole writer; Kavita only reads and serves.
  - Kavita does **not** see Uchiyomi's database, config, cache, backups, or
    Docker internals (those live on `/mnt/monarch/appdata/uchiyomi`).
  - New downloads appear after a Kavita library scan (folder watching disabled
    at the Kavita server level).

## Mobile / offline reading
- Kavita serves the `Uchiyomi` library over its normal private ingress
  (`kav.fatherfankscloud.uk`, Traefik-only; no public exposure).
- OPDS catalog: `https://kav.fatherfankscloud.uk/api/opds/<apiKey>` advertises
  each chapter as an `opds-spec.org/acquisition/open-access` CBZ download plus
  PSE page-streaming links. OPDS-capable iOS readers can download chapters for
  offline reading; the CBZ bytes are byte-identical to Uchiyomi's originals.

## Known Issues
- See `Validation/Phase10.75/kavita/Diff.md` for live-vs-CasaOS differences captured at import.
- Kavita aborts a library scan if any library root folder is empty; the
  `Uchiyomi` library therefore uses the non-empty root `/uchiyomi`.
