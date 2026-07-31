# Phase 12.3 — Recommendations for Jellyfin / Jellyseerr

Baseline before starting the **media consumption** layer. Do not treat these as executed work.

## Jellyfin (already partially aligned)

**Live today:** repo `services/jellyfin/`, appdata on Monarch, on `proxy`, Traefik `jellyfin.fatherfankscloud.uk` (HTTPS 302), still publishes `:8096`, image `:latest`.

**Recommend next:**

1. Pin image tag (same pattern as Radarr/Prowlarr)  
2. Confirm clients use Traefik hostname only, then drop host `:8096`  
3. Keep **proxy-only** (do not attach `hotio`)  
4. Document/authenticate via Authentik if UI should not be open on LAN trust alone  
5. Leave library paths on `/hive` (identity mounts OK); optional later move toward `/hive/media/...`  

## Jellyseerr (Overseerr role — not standardized)

**Live today:** CasaOS compose, `/DATA/AppData/jellyseerr`, networks `hotio_default` + `jellyfin_default`, host `:5055`, no Traefik. Canonical Overseerr role is **proxy-only**.

**Recommend next:**

1. Migrate SoT to `services/jellyseerr/` (or `overseerr/`) with Phase 12 pattern  
2. Move state to `/mnt/monarch/appdata/jellyseerr`  
3. Attach **`proxy` only**; remove `hotio` / `jellyfin_default` unless a documented DNS need remains  
4. Add Traefik router (`jellyseerr.<domain>`)  
5. Point Jellyseerr at Jellyfin / Sonarr / Radarr via Traefik URLs or Docker DNS on `proxy` after Sonarr is dual-homed  
6. Drop host `:5055` after Traefik soak  

## Sequencing suggestion

1. Finish Sonarr dual-home (unblocks clean Jellyseerr → Sonarr DNS)  
2. Jellyfin pin + Traefik-only  
3. Jellyseerr Phase 12 migration  
4. Bazarr / Lidarr only after consumption ingress is stable  
