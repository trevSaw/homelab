this was its response:
Below is a draft “architecture specification” that folds the constraints you just listed into the high‑level redesign we discussed.
I’ve broken it into the pieces you asked for (domains, directory layout, networking, secret handling, storage migration, backup & DR, and a concrete‑action checklist).

Where a suggestion would change the current behaviour (e.g. moving a config directory, adding a second network, or tightening a port‑exposure) I’ve highlighted it and asked for your explicit go‑ahead at the end of the document.
1. Logical Domain Model

Infrastructure
│
├─ proxy/
│   └─ traefik/                ← single Traefik v3 instance
│
├─ ai/
│   ├─ odysseus/
│   ├─ ollama/
│   └─ open‑webui/
│
├─ monitoring/
│   ├─ prometheus/
│   ├─ grafana/
│   └─ ntfy/
│
├─ storage/
│   ├─ zfs‑scrub/
│   └─ backup‑agent/
│
├─ media/
│   ├─ qbittorrent/
│   ├─ nzbget/
│   ├─ radarr/
│   ├─ sonarr/
│   ├─ readarr/
│   ├─ prowlarr/
│   └─ jellyfin/
│
├─ productivity/
│   ├─ nextcloud/
│   ├─ caldav‑server/
│   └─ beszel/
│
├─ automation/
│   ├─ home‑assistant/
│   └─ odysseus‑script‑host/
│
└─ development/
    ├─ code‑server/
    ├─ honcho/
    └─ docker‑osx/

Each domain gets its own top‑level folder under the repository root (/home/user/homelab/ in your case).
All compose files for a service live in that service’s folder (e.g. media/qbittorrent/docker-compose.yml).
2. Directory & Volume Layout
Domain / Service	Host Path (SSD) – /monarch	Host Path (HDD) – /hive	Docker Bind‑Mount (inside container)	Notes
proxy (traefik)	/monarch/traefik/config	–	/etc/traefik	All TLS, middleware, and static config on SSD.
ai → odysseus	/monarch/odysseus/data (metadata, DB)	–	/app/data	Existing ./data bind is kept, but moved to the SSD path.
ai → ollama	/monarch/ollama/.ollama	–	/root/.ollama	Already on SSD.
media → qbittorrent	/monarch/qbittorrent/config	/hive/downloads (actual torrent files)	/config	Config & fast‑metadata on SSD, large downloads stay on HDD.
media → nzbget	/monarch/nzbget/config	/hive/downloads	/config	Same pattern as qBittorrent.
media → radarr/sonarr/readarr/prowlarr	/monarch/<service>/config	–	/config	All non‑media data lives on SSD.
media → jellyfin	/monarch/jellyfin/config<br>/monarch/jellyfin/cache<br>/monarch/jellyfin/transcode	/hive/jellyfin/media (tv, movies, music, etc.)	/config<br>/cache<br>/transcode	Transcodes are IO‑heavy; placing them on SSD avoids HDD thrashing.
productivity → nextcloud	/monarch/nextcloud/config<br>/monarch/nextcloud/data (DB, metadata)	/hive/nextcloud/files (user files)	/var/www/html/config<br>/var/www/html/data	Keeps user content on HDD while DB & config stay on SSD.
development → code‑server	/monarch/code-server/config	–	/config	IDE settings, extensions, workspaces on SSD.
automation → odysseus‑script‑host	/monarch/odysseus/scripts	–	/scripts	Scripts run fast from SSD.
monitoring → prometheus	/monarch/prometheus/data	–	/prometheus	Time‑series DB on SSD for performance.
monitoring → grafana	/monarch/grafana/data	–	/var/lib/grafana	Same.
monitoring → ntfy	/monarch/ntfy/cache	–	/var/cache/ntfy	Small cache on SSD.

All bind‑mounts include the SELinux :z flag (or :Z if you prefer per‑mount labeling) to avoid permission problems on SELinux‑enabled hosts.
3. Networking Model
3.1 Global Networks
Network	Purpose	Who is attached
proxy	Traefik front‑end, TLS termination, public HTTP(s)	All services that need web UI access (Traefik routers & middleware).
internal	Private service‑to‑service traffic; not reachable from outside the host	All back‑end services (databases, AI models, monitoring agents, internal APIs).
vpn	Routes download traffic through the VPN container (or host‑level VPN).	Only the Media stack services that need to push/pull torrents or NZB files (qbittorrent, nzbget, radarr, sonarr, readarr, prowlarr).
gpu (optional)	GPU device reservation for Ollama	Ollama only – set driver: nvidia & cap_add: [GPU] if you use Docker’s --gpus.

All containers must attach to at least one of the three core networks (proxy, internal, vpn).
The media stack is the only place where a service attaches to both proxy and vpn (as you explicitly required).
3.2 Example – Media Service Definition

# media/qbittorrent/docker-compose.yml
services:
  qbittorrent:
    image: cr.hotio.dev/hotio/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    ports: []                     # no host‑port exposure, Traefik will expose it
    environment:
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
      - TZ=Etc/UTC
      - UMASK=002
      - VPN_ENABLED=true
      - VPN_CONF=wg0
    volumes:
      - /monarch/qbittorrent/config:/config:z
      - /hive/downloads:/downloads:z   # large files stay on HDD
    networks:
      - proxy    # for Traefik UI
      - vpn      # for routing traffic through VPN
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.qbittorrent.rule=Host(`qb.fatherfankscloud.uk`)"
      - "traefik.http.routers.qbittorrent.entrypoints=websecure"
      - "traefik.http.routers.qbittorrent.tls.certresolver=letsencrypt"
      - "traefik.http.services.qbittorrent.loadbalancer.server.port=8080"
networks:
  proxy:
    external: true
  vpn:
    external: true

The same pattern is reproduced for NZBGet, Radarr, Sonarr, Readarr, and Prowlarr.
3.3 Dual‑Network Rationale

Keeping the Media services on the vpn network ensures all outbound traffic for downloads (tracker communication, indexer API calls, etc.) traverses the VPN container.
Attaching to the proxy network only exposes the HTTP UI, which Traefik proxies with TLS termination. No other inbound traffic reaches the VPN network, preserving the isolation you need.
4. Secret Management ( .env / .env.example )
4.1 Policy

    Never put a secret directly into a docker‑compose.yml.

    Every stack gets two files in its folder:
        .env.example – checked‑in. Lists every variable the stack expects (with empty values or short comments).
        .env – not checked‑in (.gitignore entry added globally). Contains the actual values.

    The compose file references variables only via ${VAR} syntax – never via - VAR=value.

4.2 Example – Nextcloud

# productivity/nextcloud/docker-compose.yml
version: "3.9"
services:
  app:
    image: nextcloud:27.0.3-apache
    container_name: nextcloud
    restart: unless-stopped
    ports: []                          # UI via Traefik only
    env_file: .env
    environment:
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_HOST=db
      - NEXTCLOUD_TRUSTED_DOMAINS=${DEFAULT_DOMAIN}
    volumes:
      - /monarch/nextcloud/config:/var/www/html/config:z
      - /hive/nextcloud/data:/var/www/html/data:z
    networks:
      - internal
      - proxy
    labels:
      - "traefik.enable=true"
      - "traifik.http.routers.nextcloud.rule=Host(`nc.fatherfankscloud.uk`)"
      - "traefik.http.routers.nextcloud.entrypoints=websecure"
      - "traefik.http.routers.nextcloud.tls.certresolver=letsencrypt"
      - "traefik.http.services.nextcloud.loadbalancer.server.port=80"
  db:
    image: mariadb:10.5
    container_name: nextcloud-db
    restart: unless-stopped
    env_file: .env
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - /monarch/nextcloud/db:/var/lib/mysql:z
    networks:
      - internal
networks:
  internal:
    external: true
  proxy:
    external: true

The .env.example that lives next to it would contain:

# .env.example
MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
MYSQL_PASSWORD=
DEFAULT_DOMAIN=example.com

Add a global .gitignore entry:*

# .gitignore (root of repo)
**/.env

5. Resource Limits & Healthchecks
Service	CPU	Memory	Healthcheck (example)
ollama	0.75	12g (already set)	curl -f http://localhost:11434/api/version
curl -f http://localhost:11434/api/version || exit 1 | | odysseus | 0.5 | 2g | CMD-SHELL curl -f http://localhost:7000/health || exit 1 | | qbittorrent | 0.3 | 512m | CMD-SHELL curl -f http://localhost:8080/api/v2/app/default || exit 1 | | jellyfin | 1.0 | 2g | CMD-SHELL curl -f http://localhost:8096/health || exit 1 | | prometheus | 0.5 | 1g | CMD-SHELL wget -qO- http://localhost:9090/-/ready || exit 1 | | grafana | 0.3 | 512m | CMD-SHELL curl -f http://localhost:3000/api/health || exit 1 | | code‑server | 0.4 | 1g | CMD-SHELL curl -f http://localhost:8443/healthz || exit 1 | | All others | 0.2 ‑ 0.5 | 256m ‑ 512m | Add a simple TCP check ( CMD-SHELL test "$(nc -z localhost $PORT && echo ok)" = ok || exit 1 ) |

You can add the limits under the deploy key (Docker‑Compose v3.8+):

deploy:
  resources:
    limits:
      cpus: "0.5"
      memory: "512M"

6. Image Pinning

Strategy:

    Pick the latest stable tag at the time you add the service and record that version in the compose file.
    When you deliberately want to upgrade, bump the tag and run docker compose pull && docker compose up -d.
    Keep a tiny versions.md file in each domain folder listing the current tags for audit purposes.

Sample snippet (Jellyfin):

image: ghcr.io/hotio/jellyfin:10.9.8

(Replace 10.9.8 with the exact version you verify works.)
7. Backup & Disaster‑Recovery (DR)
7.1 Scope
Included in Backup	Reason
All named volumes (searxng-data, chromadb-data, ntfy-cache, prometheus, grafana, nextcloud-db, jellyfin‑config, …)	Holds stateful data; cannot be recreated from scratch.
All bind‑mount config directories on SSD (/monarch/*/config, /monarch/*/data)	Small, fast‑changing files – easy to snapshot.
Traefik static config (/monarch/traefik)	TLS certificates, middleware definitions.
.env files (if you keep a copy on a secure backup medium)	Secret values needed for a full restore.
7.2 Process

    ZFS Snapshot – Run a recursive snapshot of the whole SSD dataset (monarch) and the HID‑mounted ZFS pool (hive) just for metadata (if you ever need to roll back configuration).
    Run

    zfs snapshot -r monarch@daily-$(date +%F)
    zfs snapshot -r hive@metadata-$(date +%F)   # optional, only configs reside on SSD

    Export – zfs send -R monarch@daily-$(date +%F) | gzip > /backup/monarch-$(date +%F).zfs.gz
    Store the .zfs.gz off‑site (e.g., a cheap cloud bucket or a second external drive).
    Retention – Keep 7 daily, 4 weekly, 6 monthly snapshots. Use a simple zfs destroy policy script.
    Restore – zfs receive -F monarch < backupfile will bring the SSD dataset back to the point‑in‑time state. Containers can then be started with docker compose up -d.

Because large media stays on /hive, you generally do not back up that pool daily – you rely on the inherent redundancy of your ZFS pool (mirrored vdevs, checksum protection). If you later decide you want a media backup, you can schedule a separate rsync job to an external NAS.
7.3 Documentation

Create a single backup/README.md in the repo that explains:

    Which directories are covered.
    How to run the snapshot script manually.
    How to restore from a snapshot.
    Where the off‑site copy lives and encryption method (e.g., gpg --symmetric).

8. Consistent Documentation Scaffold

Each service folder gets a README.md that follows this template:

# Service: <Name>
Domain: <Infrastructure / AI / Media …>

## Overview
<One‑sentence description>

## Architecture
- **Image**: `<image>:<tag>`
- **Networks**: `proxy`, `internal` (plus `vpn` for Media)
- **Volumes**: List host‑path → container‑path mapping
- **Ports**: Exposed via Traefik only (list router rule)

## Requirements
- SSD space: <X GB>
- HDD space (if applicable): <Y GB>
- GPU (if applicable): yes / no

## Installation
```bash
cd <domain>/<service>
docker compose up -d
```

## Configuration
- **Environment variables** – see `.env.example`
- **Traefik labels** – automatically generate a public URL `<subdomain>.fatherfankscloud.uk`

## Backup
- Data stored in `<SSD‑path>` is covered by the global ZFS snapshot.  
- Large media assets are not backed up here (see storage policy).

## Update Procedure
```bash
docker compose pull
docker compose up -d
```

## Troubleshooting
- Container not starting? `docker compose logs -f`  
- Healthcheck failing? Verify port accessibility from inside container.

## Disaster Recovery
- Restore the `monarch` dataset from the latest ZFS snapshot, then run `docker compose up -d` in the service folder.

All services share the same layout, making onboarding for new admins trivial.
9. Action Checklist (what still needs your OK)
#	Change	Impact	Do you approve?
1			