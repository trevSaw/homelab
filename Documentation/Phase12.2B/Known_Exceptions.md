# Phase 12.2B Known Exceptions

| Service | Exception | Reason | Risk | Mitigation |
|---|---|---|---|---|
| Sonarr | `network_mode: host` | Native config uses `localhost` for NZBGet/qBittorrent | Medium | Documented; optional later move to `hotio_default` + update client hosts |
| Sonarr | Host port `8989` | WebUI (host network) | Low | LAN; auth was None on native — consider enabling later |
| Sonarr | Image pinned to Sonarr **v3** | Match native 3.0.10.1566; linuxserver legacy tag | Medium | Plan v4 upgrade as follow-up after soak |
| Sonarr | AuthenticationMethod `None` | Inherited from native config | Medium | Not changed in this migration; harden later |
| Layout | `compose.yml` under `services/` | Phase 12 SoT freeze | Low | Consistent with 12.1/12.2A |

## Non-exceptions

- App state on `/mnt/monarch/appdata/sonarr`
- Media/downloads remain on `/hive`
- Dedicated `.env` (no shared/symlink env)
- No secrets in git-tracked files
- `/hive/Hotio/sonarr` not used
