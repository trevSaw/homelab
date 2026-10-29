# Jellyfin (Phase 12.4)

Media server. Config: `/mnt/monarch/appdata/jellyfin`. Libraries remain on `/hive/jellyfin/{tv,movie}`.

- Image: `ghcr.io/hotio/jellyfin:release-12.1` (upgraded from 10.11.6)
- Network: `proxy` only
- Traefik: `jellyfin.fatherfankscloud.uk`
- Host `:8096` transitional
- HW accel: `nvenc` via `runtime: nvidia` + `gpus: all` (NVIDIA T400). `/dev/dri` (VAAPI) also mounted as secondary.

## 12.x migration notes

- Major DB migration on first boot; cannot roll back without a full restore.
- Pre-upgrade backup: `/hive/backups/jellyfin/pre-12.1-<timestamp>/`.
- Old plugins preserved at `data/plugins.pre-12.1`; reinstall 12.x-compatible plugins from the stable repo.
- A full library scan is required after upgrade.

## Transcode fix (2026-09-22)

- Previously `encoding.xml` was set to `nvenc` but the container had **no NVIDIA runtime/devices**, so every 2160p/HEVC/10-bit transcode (and PGS subtitle burn-in) failed with `Cannot load libcuda.so.1`.
- Fixed by adding `runtime: nvidia` + `gpus: all` to the compose. Verified: NVDEC decode + `tonemap_cuda` + `h264_nvenc` encode works at ~47fps on the T400.
- This also fixes playback failures in Firefox/Brave for HEVC/Hi10P content and image-subtitle burn-in.

## Abyss Spotlight theme

- CSS import added to `branding.xml` (`@import .../AumGupta/abyss-jellyfin@main/abyss.css`).
- Spotlight web files are re-applied on every container start via the hotio startup hook.
- Hook: `config/init-hook-app` → mounted to `/etc/s6-overlay/init-hook-app` (hotio equivalent of linuxserver's `custom-cont-init.d`).
- Script: `config/custom-cont-init.d/abyss-spotlight.sh` (downloads `spotlight.{html,css,loader.js}` into the web dir + patches `index.html`).

```bash
cd services/jellyfin
cp .env.example .env
docker compose -f compose.yml up -d
```
