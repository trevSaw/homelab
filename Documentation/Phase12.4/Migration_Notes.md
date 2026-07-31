# Phase 12.4 — Migration Notes

## Jellyfin

- Already Phase 11/12-ish; standardization = pin + limits + label network affinity  
- Libraries stay `/hive/jellyfin/{tv,movie}`  
- HW: keep `/dev/dri` and NVIDIA_* env (VAAPI primary)  
- **`:8096` not removed** — Traefik works (302) but LAN clients/bookmarks still use host port; documented transitional  

## Jellyseerr

- Moved off CasaOS orphan `jellyfin_default`  
- `proxy`-only per Overseerr role  
- Integrations: `jellyfin:8096`, `radarr:7878`, Sonarr `192.168.50.44:8989` (host-net exception)  

## Bazarr

- Dual-home for UI (`proxy`) + *arr DNS (`hotio`)  
- Fixed Radarr `ip` from self-IP to `radarr`  
- Sonarr remains LAN IP until Sonarr re-home  

## Lidarr

Not deployed. No action.
