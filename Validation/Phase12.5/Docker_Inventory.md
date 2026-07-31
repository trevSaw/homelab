# Docker Inventory — Phase 12.5

Total containers: 42 (all running at audit)

| Name | Image | Health | Networks | Compose SoT | Traefik | Ports |
|---|---|---|---|---|---|---|
| actual-server | `actualbudget/actual-server:25.10.0` | none | `big-bear-actual-server_default` | casaos/other | no | 5006->5006/tcp |
| authentik-db | `postgres:16-alpine` | healthy | `authentic_authentik` | repo | no | — |
| authentik-redis | `redis:alpine` | healthy | `authentic_authentik` | repo | no | — |
| authentik-server | `ghcr.io/goauthentik/server:2024.12.3` | healthy | `authentic_authentik,proxy` | repo | true | — |
| authentik-worker | `ghcr.io/goauthentik/server:2024.12.3` | healthy | `authentic_authentik,proxy` | repo | no | — |
| bazarr | `lscr.io/linuxserver/bazarr:1.2.2` | healthy | `hotio_default,proxy` | repo | true | 6767->6767/tcp |
| beszel | `henrygd/beszel:0.18.7` | none | `homelab` | repo | no | 8090->8090/tcp |
| beszel-agent | `henrygd/beszel-agent:0.18.7` | none | `host` | repo | no | — |
| big-bear-crafty | `registry.gitlab.com/crafty-controller/crafty-4:latest` | none | `big-bear-crafty` | casaos/other | no | 19132->19132/udp, 25500->25500/tcp, 25501->25501/tcp, 25502->25502/tcp, 25503->25503/tcp, 25504->25504/tcp, 25505->25505/tcp, 25506->25506/tcp, 25507->25507/tcp, 25508->25508/tcp, 25509->25509/tcp, 25510->25510/tcp, 25511->25511/tcp, 25512->25512/tcp, 25513->25513/tcp, 25514->25514/tcp, 25515->25515/tcp, 25516->25516/tcp, 25517->25517/tcp, 25518->25518/tcp, 25519->25519/tcp, 25520->25520/tcp, 25521->25521/tcp, 25522->25522/tcp, 25523->25523/tcp, 25524->25524/tcp, 25525->25525/tcp, 25526->25526/tcp, 25527->25527/tcp, 25528->25528/tcp, 25529->25529/tcp, 25530->25530/tcp, 25531->25531/tcp, 25532->25532/tcp, 25533->25533/tcp, 25534->25534/tcp, 25535->25535/tcp, 25536->25536/tcp, 25537->25537/tcp, 25538->25538/tcp, 25539->25539/tcp, 25540->25540/tcp, 25541->25541/tcp, 25542->25542/tcp, 25543->25543/tcp, 25544->25544/tcp, 25545->25545/tcp, 25546->25546/tcp, 25547->25547/tcp, 25548->25548/tcp, 25549->25549/tcp, 25550->25550/tcp, 25551->25551/tcp, 25552->25552/tcp, 25553->25553/tcp, 25554->25554/tcp, 25555->25555/tcp, 25556->25556/tcp, 25557->25557/tcp, 25558->25558/tcp, 25559->25559/tcp, 25560->25560/tcp, 25561->25561/tcp, 25562->25562/tcp, 25563->25563/tcp, 25564->25564/tcp, 25565->25565/tcp, 25566->25566/tcp, 25567->25567/tcp, 25568->25568/tcp, 25569->25569/tcp, 25570->25570/tcp, 25571->25571/tcp, 25572->25572/tcp, 25573->25573/tcp, 25574->25574/tcp, 25575->25575/tcp, 25576->25576/tcp, 25577->25577/tcp, 25578->25578/tcp, 25579->25579/tcp, 25580->25580/tcp, 25581->25581/tcp, 25582->25582/tcp, 25583->25583/tcp, 25584->25584/tcp, 25585->25585/tcp, 25586->25586/tcp, 25587->25587/tcp, 25588->25588/tcp, 25589->25589/tcp, 25590->25590/tcp, 25591->25591/tcp, 25592->25592/tcp, 25593->25593/tcp, 25594->25594/tcp, 25595->25595/tcp, 25596->25596/tcp, 25597->25597/tcp, 25598->25598/tcp, 25599->25599/tcp, 25600->25600/tcp, 8123->8123/tcp, 8443->8443/tcp |
| byparr-byparr-1 | `ghcr.io/thephaseless/byparr:latest` | healthy | `hotio_default` | casaos/other | no | — |
| calibre | `lscr.io/linuxserver/calibre:latest` | none | `proxy` | repo | true | — |
| calibre-web | `lscr.io/linuxserver/calibre-web:latest` | none | `proxy` | repo | true | — |
| code-server | `lscr.io/linuxserver/code-server:latest` | none | `ollama_ollama-net,proxy` | repo | true | — |
| hermes | `nousresearch/hermes-agent:latest` | none | `ollama_ollama-net,proxy` | appdata | true | — |
| homepage | `ghcr.io/gethomepage/homepage:latest` | healthy | `proxy` | repo | true | — |
| honcho-api | `honcho-api` | none | `ollama_ollama-net,proxy` | appdata | true | — |
| honcho-deriver | `honcho-deriver` | none | `ollama_ollama-net` | appdata | no | — |
| honcho-postgres | `pgvector/pgvector:pg15` | none | `ollama_ollama-net` | appdata | no | — |
| honcho-redis | `redis:8.2` | none | `ollama_ollama-net` | appdata | no | — |
| jellyfin | `ghcr.io/hotio/jellyfin:release-10.11.6` | healthy | `proxy` | repo | true | 8096->8096/tcp |
| jellyseerr | `ghcr.io/hotio/jellyseerr@sha256:794d5496988b69b67fab65daa9963de0dfbf6ada9103b81f95dc766e9b5d86f8` | healthy | `proxy` | repo | true | 5055->5055/tcp |
| kavita | `jvmilazz0/kavita:latest` | healthy | `proxy` | hive | true | — |
| linuxserver-lazylibrarian-app-1 | `linuxserver/lazylibrarian:version-3682faed` | none | `linuxserver-lazylibrarian_default` | casaos/other | no | 5299->5299/tcp |
| linuxserver-mariadb-app-1 | `linuxserver/mariadb:latest` | none | `linuxserver-mariadb_default` | casaos/other | no | 3308->3306/tcp |
| n8n | `docker.n8n.io/n8nio/n8n:latest` | none | `ai-assistant,homelab` | appdata | no | 5678->5678/tcp |
| nextcloud | `nextcloud:31` | none | `cloud_nextcloud_net,proxy` | hive | true | — |
| nextcloud-db | `mariadb:10.11` | none | `cloud_nextcloud_net` | hive | no | — |
| nzbget | `ghcr.io/hotio/nzbget@sha256:6815d7e4837b1b03771465ec67191a94e4eb67ebfdc7322d3394ebf8952eb879` | healthy | `container:2c19c2533bde5128518c0de02fbd07b402853ad5fbccc3159756750eefdcd106` | repo | no | — |
| odysseus-chromadb-1 | `docker.io/chromadb/chroma:latest` | none | `odysseus_default` | appdata | no | 8100->8000/tcp |
| odysseus-ntfy-1 | `docker.io/binwiederhier/ntfy` | none | `odysseus_default` | appdata | no | 8091->80/tcp |
| odysseus-odysseus-1 | `odysseus-odysseus` | none | `ollama_ollama-net` | appdata | no | 7000->7000/tcp |
| odysseus-searxng-1 | `docker.io/searxng/searxng:2026.5.31-7159b8aed` | healthy | `odysseus_default` | appdata | no | 8585->8080/tcp |
| ollama | `ollama/ollama:latest` | none | `ai-assistant,ollama_ollama-net` | hive | false | — |
| open-webui | `ghcr.io/open-webui/open-webui:main` | healthy | `ai-assistant,ollama_ollama-net,proxy` | hive | true | — |
| portainer | `portainer/portainer-ce:2.33.6` | none | `portainer_network` | repo | no | 9000->9000/tcp, 9445->9443/tcp |
| prowlarr | `ghcr.io/hotio/prowlarr:release-2.3.5.5327` | healthy | `hotio_default,proxy` | repo | true | 9696->9696/tcp |
| qbittorrent | `ghcr.io/hotio/qbittorrent:release-4.5.5` | healthy | `hotio_default` | repo | no | 6789->6789/tcp, 8080->8080/tcp, 8118->8118/tcp |
| radarr | `ghcr.io/hotio/radarr:release-5.22.4.9896` | healthy | `hotio_default,proxy` | repo | true | 7878->7878/tcp |
| readarr | `lscr.io/linuxserver/readarr:develop` | none | `hotio_default` | casaos/other | no | 8787->8787/tcp |
| sonarr | `lscr.io/linuxserver/sonarr:version-3.0.10.1566` | healthy | `host` | repo | no | — |
| traefik | `traefik:v3.6.7` | healthy | `proxy` | repo | true | 443->443/tcp, 80->80/tcp |
| uptimekuma | `louislam/uptime-kuma:1.23.10-alpine` | healthy | `proxy` | repo | no | 3001->3001/tcp |
