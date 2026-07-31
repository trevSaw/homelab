# Network Architecture — Phase 12 Closeout

Canonical media standard: `Architecture/media-stack-networking.md`.  
Live inventory: `Validation/Phase12.5/Docker_Networks.md`.

## Primary networks

### `proxy`

**Purpose:** Traefik ingress, HTTPS, Authentik, user-facing UIs.

**Attached (selected):** traefik, authentik-*, jellyfin, jellyseerr, radarr, prowlarr, bazarr, homepage, nextcloud, open-webui, calibre*, code-server, kavita, uptimekuma, hermes, honcho-api, …

### `hotio` / live `hotio_default`

**Purpose:** Media automation Docker DNS.

**Attached:** qbittorrent, radarr, prowlarr, bazarr, readarr, byparr-byparr-1  

**NZBGet:** not a first-class member — `network_mode: container:qbittorrent`.

### Other production networks

| Network | Purpose | Notes |
|---|---|---|
| `homelab` | Monitoring/automation helpers | Beszel, n8n |
| `authentic_authentik` | Authentik internal | DB/redis/server |
| `ollama_ollama-net` / `ai-assistant` | AI fabrics | Phase 13 territory |
| `portainer_network` | Portainer | 12.1 exception |
| `cloud_nextcloud_net` | Nextcloud | — |
| `jellyfin_default` | Empty at closeout | Was Jellyseerr remnant |
| CasaOS `*_default` | Legacy apps | Actual, Crafty, etc. |

## Diagram — media (as operated)

```text
                    [users]
                       |
                   [traefik]
                    proxy
         +------+------+------+------+
         |      |      |      |      |
      jellyfin jellyseerr radarr prowlarr bazarr
         |             |   \    /   |
         |             |    \  /    |
         |             |   hotio_default
         |             |    /      \
         |             | qbittorrent  (nzbget shares netns)
         |             |
      [sonarr]---- host ---- localhost --> :8080/:6789
```

## Intended media end-state (debt)

Sonarr joins `proxy`+`hotio`; NZBGet gains a DNS name without breaking VPN; transitional host ports removed after Traefik-only client soak.
