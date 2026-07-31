# Docker Networks — Phase 12.5

## `ai-assistant`

- Driver: `bridge`
- Subnet: `192.168.0.0/20`
- Containers (3): n8n, ollama, open-webui

## `ai_backend`

- Driver: `bridge`
- Subnet: `172.28.0.0/16`
- Containers (0): _(empty)_

## `ai_net`

- Driver: `bridge`
- Subnet: `172.23.0.0/16`
- Containers (0): _(empty)_

## `authentic_authentik`

- Driver: `bridge`
- Subnet: `192.168.16.0/20`
- Containers (4): authentik-db, authentik-redis, authentik-server, authentik-worker

## `big-bear-actual-server_default`

- Driver: `bridge`
- Subnet: `192.168.96.0/20`
- Containers (1): actual-server

## `big-bear-crafty`

- Driver: `bridge`
- Subnet: `172.26.0.0/16`
- Containers (1): big-bear-crafty

## `blububbles_default`

- Driver: `bridge`
- Subnet: `192.168.64.0/20`
- Containers (0): _(empty)_

## `bridge`

- Driver: `bridge`
- Subnet: `172.17.0.0/16`
- Containers (0): _(empty)_

## `cloud_nextcloud_net`

- Driver: `bridge`
- Subnet: `172.25.0.0/16`
- Containers (2): nextcloud, nextcloud-db

## `coder_default`

- Driver: `bridge`
- Subnet: `192.168.80.0/20`
- Containers (0): _(empty)_

## `cosmoos_default`

- Driver: `bridge`
- Subnet: `192.168.144.0/20`
- Containers (0): _(empty)_

## `cosmos-cosmos-mongo-ZYN-Ip8`

- Driver: `bridge`
- Subnet: `172.16.0.0/28`
- Containers (0): _(empty)_

## `homelab`

- Driver: `bridge`
- Subnet: `172.29.0.0/16`
- Containers (2): beszel, n8n

## `host`

- Driver: `host`
- Containers (2): beszel-agent, sonarr

## `hotio_default`

- Driver: `bridge`
- Subnet: `172.27.0.0/16`
- Containers (6): bazarr, byparr-byparr-1, prowlarr, qbittorrent, radarr, readarr

## `jellyfin_default`

- Driver: `bridge`
- Subnet: `172.18.0.0/16`
- Containers (0): _(empty)_

## `kavita_default`

- Driver: `bridge`
- Subnet: `172.21.0.0/16`
- Containers (0): _(empty)_

## `linuxserver-lazylibrarian_default`

- Driver: `bridge`
- Subnet: `172.31.0.0/16`
- Containers (1): linuxserver-lazylibrarian-app-1

## `linuxserver-mariadb_default`

- Driver: `bridge`
- Subnet: `172.30.0.0/16`
- Containers (1): linuxserver-mariadb-app-1

## `linuxserver-qdirstat_default`

- Driver: `bridge`
- Subnet: `192.168.128.0/20`
- Containers (0): _(empty)_

## `nextcloud_default`

- Driver: `bridge`
- Subnet: `172.20.0.0/16`
- Containers (0): _(empty)_

## `none`

- Driver: `null`
- Containers (0): _(empty)_

## `odysseus_default`

- Driver: `bridge`
- Subnet: `172.24.0.0/16`
- Containers (3): odysseus-chromadb-1, odysseus-ntfy-1, odysseus-searxng-1

## `ollama_ollama-net`

- Driver: `bridge`
- Subnet: `172.22.0.0/16`
- Containers (9): code-server, hermes, honcho-api, honcho-deriver, honcho-postgres, honcho-redis, odysseus-odysseus-1, ollama, open-webui

## `portainer_network`

- Driver: `bridge`
- Subnet: `192.168.160.0/20`
- Containers (1): portainer

## `proxy`

- Driver: `bridge`
- Subnet: `172.19.0.0/16`
- Containers (18): authentik-server, authentik-worker, bazarr, calibre, calibre-web, code-server, hermes, homepage, honcho-api, jellyfin, jellyseerr, kavita, nextcloud, open-webui, prowlarr, radarr, traefik, uptimekuma
