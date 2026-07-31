# Phase 12.3 — Remaining Technical Debt

Ordered by impact on the media platform.

| # | Debt | Impact | Suggested follow-up |
|---|---|---|---|
| 1 | Sonarr `network_mode: host` | Blocks canonical dual-home; forces `localhost` + LAN URLs | Phase: Sonarr re-home to `proxy`+`hotio`, Traefik, Docker DNS clients |
| 2 | NZBGet shared VPN netns | No `nzbget` DNS name | Dedicated VPN/DNS design or keep `qbittorrent:6789` as permanent exception |
| 3 | Transitional host ports on Radarr/Prowlarr | Extra attack/ops surface | Remove after Traefik hostnames used exclusively |
| 4 | No Authentik middleware on *arr Traefik routers | Auth depends on app Forms / LAN trust | Add forward-auth when ready |
| 5 | Sonarr still v3 pin | EOL/security trajectory | Plan v4 upgrade after network re-home |
| 6 | Legacy Hive paths (`/hive/jellyfin/...`, `/hive/downloads`) | Diverges from `/hive/media/...` target | Explicit path migration later |
| 7 | CasaOS leftovers / `/DATA` copies | Confusion vs repo SoT | Decommission after soak |
| 8 | Remote indexer flakiness (sample 400s) | Search quality, not fabric | Tune/disable bad indexers in Prowlarr |
| 9 | Jellyfin `:latest` + host `:8096` | Consumption layer incomplete | Pin + Traefik-only |
| 10 | Jellyseerr not on Phase 12 pattern | Wrong networks vs Overseerr role | Migrate to `proxy` + Traefik + appdata |

Items 1–3 are the automation-plane debt that most affect the next *arr work.
