# Phase 12.2A Known Exceptions

| Service | Exception | Reason | Risk | Mitigation |
|---|---|---|---|---|
| Hotio / qBittorrent | `cap_add: NET_ADMIN` + sysctls | WireGuard VPN inside container | Medium | Required for VPN; keep `VPN_ENABLED=true`; no privileged |
| Hotio / qBittorrent | Host ports `8080`, `8118`, `6789` | WebUI, Privoxy, and NZBGet (shared netns) | Low | LAN exposure; auth on WebUIs |
| Hotio / qBittorrent | `VPN_LAN_NETWOK` typo env key retained | Pre-existing Hotio env spelling in live stack | Low | Keep as-was to avoid VPN LAN behavior change; document |
| Hotio / qBittorrent | Folder name `Hotio` / appdata `hotio` | Historical; not renamed to `qbittorrent` | Low | Avoid blast radius; README clarifies |
| NZBGet | `network_mode: container:qbittorrent` | Routes Usenet traffic through Hotio VPN | Medium | Recreate Hotio then NZBGet; never detach without intentional redesign |
| NZBGet | Digest pin instead of floating tag | Exact prior live image (label 25.2); `release-25.2` is a different rebuild | Low | Documented in `Versions.md` |
| Layout | Compose under `services/` not `compose/<domain>/` | Same Phase 12.1 SoT freeze | Low | Consistent with pilot |

## Explicit non-service

| Item | Status |
|---|---|
| SABnzbd | **Not used** on this host. No container, no compose, no migration. Out of Phase 12.2A scope. |

## Non-exceptions (required practice)

- No secrets in git-tracked compose (VPN private keys remain under appdata `/config`)
- App config under `/mnt/monarch/appdata/<service>`
- Large downloads remain on `/hive/downloads*`
- Images pinned; `restart: unless-stopped`; memory limits set
- Healthchecks defined (both images provide `curl`)
