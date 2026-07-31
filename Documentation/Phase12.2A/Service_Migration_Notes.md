# Phase 12.2A — Service notes

## qBittorrent (Hotio)

- SoT: `services/Hotio/`
- Config: `/mnt/monarch/appdata/hotio`
- Downloads bind: `/hive/downloads/completed` → `/downloads`
- VPN: WireGuard via Hotio (`VPN_ENABLED`, `NET_ADMIN`); private keys in appdata only
- Also publishes `:6789` for NZBGet

## NZBGet

- SoT: `services/NZBget/`
- Config: `/mnt/monarch/appdata/nzbget`
- Downloads bind: `/hive/downloads` → `/downloads`
- Must run after `qbittorrent` (`network_mode: container:qbittorrent`)

## SABnzbd

Not used. No container on host. Do not add for Phase 12.2A.
