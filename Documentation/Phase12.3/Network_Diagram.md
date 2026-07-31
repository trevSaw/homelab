# Phase 12.3 — Network Diagram

**Date:** 2026-07-31  
**Live names:** `proxy`, `hotio_default` (logical `hotio`)

```text
                         Users / LAN
                              |
                         [ Traefik ]
                         proxy only
                         :80/:443
                              |
        +---------------------+----------------------+
        |                     |                      |
        v                     v                      v
   [ Jellyfin ]          [ Radarr ]             [ Prowlarr ]
   proxy                 proxy+hotio            proxy+hotio
   Traefik yes           Traefik yes            Traefik yes
   :8096 transitional    :7878 transitional     :9696 transitional
                              |                      |
                              +----------+-----------+
                                         |
                                         v
                                   hotio_default
                                    /         \
                                   v           v
                            [qbittorrent]   (nzbget shares
                             hotio only      qbittorrent netns)
                             :8080/:6789

   [ Sonarr ] ---- host network ---- localhost --> :8080/:6789
   appdata OK / Traefik no / not on proxy|hotio
   Prowlarr reaches Sonarr via 192.168.50.44:8989
```

## Intended end-state (not yet fully live)

```text
Sonarr, Radarr, Prowlarr = proxy + hotio + Traefik
qBittorrent, NZBGet     = hotio (NZBGet ideally named DNS)
Jellyfin, Overseerr     = proxy only
```
