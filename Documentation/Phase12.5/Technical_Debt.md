# Technical Debt — Phase 12 Closeout

Authoritative list of known production debt after Phase 12. Items are **approved to remain** until scheduled.

| ID | Item | Severity | Ops risk | Complexity | Suggested future |
|---|---|---|---|---|---|
| TD-01 | Sonarr `network_mode: host` + `localhost` clients + no Traefik | **High** | Medium | Medium | Early maintenance / 12.x hotfix: dual-home + Traefik + DNS |
| TD-02 | NZBGet `network_mode: container:qbittorrent` (no `nzbget` DNS) | **High** | High if broken wrong | High | Dedicated VPN/DNS redesign |
| TD-03 | Transitional host ports (8096, 5055, 7878, 9696, 6767, …) | **Medium** | Low–Med | Low | Remove after Traefik-only confirmation |
| TD-04 | No Authentik middleware on most *arr/Jellyfin routers | **Medium** | Medium | Medium | Security hardening phase |
| TD-05 | Sonarr pinned on v3 | **Medium** | Medium (EOL) | Medium | Upgrade after TD-01 |
| TD-06 | Legacy Hive paths vs `/hive/media` | **Medium** | Low | High | Storage migration phase |
| TD-07 | Fleet remnants: CasaOS / `:latest` / compose outside `services/` | **Medium** | Medium | Medium–High | Per-service Phase 12-style waves |
| TD-08 | Readarr develop + hive config | **Medium** | Medium | Medium | Standardize or retire |
| TD-09 | AI stacks on hive/appdata compose, unpinned | **Medium** | Medium | High | **Phase 13** |
| TD-10 | Nextcloud on `/hive/cloud` | **Low–Med** | Low | High | Deferred platform work |
| TD-11 | Empty `jellyfin_default` network | **Low** | Low | Low | Delete when unused |
| TD-12 | Remote indexer flakiness (Prowlarr samples) | **Low** | Low | Low | Indexer hygiene |
| TD-13 | Jellyfin NVIDIA env without GPU device reservation | **Low** | Low | Low | Clarify VAAPI-only vs NVIDIA |

## Already remediated in Phase 12 (do not re-open without cause)

- Radarr download clients pointing at self-IP  
- Bazarr Radarr self-IP  
- Prowlarr→Radarr stale IPs  
- Traefik shared `.env` symlink wipe incident (fixed in 12.1)  
