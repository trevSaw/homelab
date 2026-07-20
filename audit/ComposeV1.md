======================================================================
COMPOSE AUDIT
======================================================================

## AUDIT METADATA
Audit Version : 4.0
Schema Version: 1.0
Generated     : 2026-07-08 12:18:54 UTC

## INVENTORY
Compose Files : 56

## METRICS
Search Paths :
/mnt/monarch/appdata
/hive

## MACHINE CHECKS
CHECK|ComposeFiles|PASS|56|1

## HEALTH SUMMARY
Health Score : 100

PASS : 1
WARNING : 0
CRITICAL : 0
UNKNOWN : 0

## AI PRIORITY
1. Plaintext secrets.
2. Missing restart policies.
3. Privileged containers.
4. Host networking.
5. Volume permissions.

## RAW EVIDENCE

================================================================
FILE: /mnt/monarch/appdata/odysseus-old/docker-compose.yml
================================================================
  File: /mnt/monarch/appdata/odysseus-old/docker-compose.yml
  Size: 6251      	Blocks: 16         IO Block: 4096   regular file
Device: 27h/39d	Inode: 276064      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-06-18 09:04:53.060205226 +0000
Modify: 2026-06-18 08:38:10.297870511 +0000
Change: 2026-06-18 08:38:10.297870511 +0000
 Birth: 2026-06-18 08:38:10.293870487 +0000

services:
  odysseus:
    build: .
    networks:
      - ollama-net
    ports:
      - "${APP_BIND:-127.0.0.1}:${APP_PORT:-7000}:7000"
    volumes:
      - ./data:/app/data:z
      - ./logs:/app/logs:z
      # Cookbook remote-server SSH identity. Odysseus can generate a key here;
      # add the shown public key to each remote server's authorized_keys.
      - ./data/ssh:/app/.ssh:z
      # Cookbook local model cache. Inside Docker, "Local" means the Odysseus
      # container, so persist its HuggingFace cache under ./data/huggingface.
      - ./data/huggingface:/app/.cache/huggingface:z
      # Cookbook-installed Python CLIs/packages (vLLM, llama-cpp-python, etc.)
      # land under /app/.local for the odysseus user. Persist them so a
      # container recreate does not silently remove installed serve engines.
      - ./data/local:/app/.local:z

      # Homelab audit access
      - /hive:/mnt/hive:ro
      - /mnt/monarch:/mnt/monarch:ro
    extra_hosts:
      # Lets the container reach local services on the Docker host, including
      # Ollama at http://host.docker.internal:11434.
      - "host.docker.internal:host-gateway"
    environment:
      - LLM_HOST=${LLM_HOST:-localhost}
      - LLM_HOSTS=${LLM_HOSTS:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-}
      - RESEARCH_LLM_ENDPOINT=${RESEARCH_LLM_ENDPOINT:-}
      - HF_TOKEN=${HF_TOKEN:-}
      - HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-}
      - SEARXNG_INSTANCE=http://searxng:8080
      - CHROMADB_HOST=chromadb
      - CHROMADB_PORT=8000
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/app.db}
      - AUTH_ENABLED=${AUTH_ENABLED:-true}
      - LOCALHOST_BYPASS=${LOCALHOST_BYPASS:-false}
      - ODYSSEUS_ADMIN_USER=${ODYSSEUS_ADMIN_USER:-admin}
      - ODYSSEUS_ADMIN_PASSWORD=${ODYSSEUS_ADMIN_PASSWORD:-}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost,http://127.0.0.1}
      - SECURE_COOKIES=${SECURE_COOKIES:-false}
      - EMBEDDING_URL=${EMBEDDING_URL:-}
      - EMBEDDING_MODEL=${EMBEDDING_MODEL:-}
      - EMBEDDING_API_KEY=${EMBEDDING_API_KEY:-}
      - FASTEMBED_MODEL=${FASTEMBED_MODEL:-sentence-transformers/all-MiniLM-L6-v2}
      - FASTEMBED_CACHE_PATH=${FASTEMBED_CACHE_PATH:-}
      - CLEANUP_INTERVAL_HOURS=${CLEANUP_INTERVAL_HOURS:-24}
      - ODYSSEUS_INPROCESS_POLLERS=${ODYSSEUS_INPROCESS_POLLERS:-1}
      - ODYSSEUS_INPROCESS_TASKS=${ODYSSEUS_INPROCESS_TASKS:-1}
      - ODYSSEUS_SCRIPT_HOST=${ODYSSEUS_SCRIPT_HOST:-localhost}
      - ODYSSEUS_CHAT_UPLOAD_MAX_BYTES=${ODYSSEUS_CHAT_UPLOAD_MAX_BYTES:-10485760}
      - DATA_BRAVE_API_KEY=${DATA_BRAVE_API_KEY:-}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - GOOGLE_PSE_CX=${GOOGLE_PSE_CX:-}
      - TAVILY_API_KEY=${TAVILY_API_KEY:-}
      - SERPER_API_KEY=${SERPER_API_KEY:-}
      # PUID / PGID — the user/group the container drops to before
      # running uvicorn (entrypoint also chowns /app/data + /app/logs
      # to match, so bind-mounted files stay editable from the host).
      # 1000 is the default first user on most Linux installs. If your
      # host user has a different id, override here or via .env, e.g.:
      #   PUID=1001
      #   PGID=1001
      # Find yours with:  id -u  /  id -g
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
    depends_on:
      searxng:
        condition: service_healthy
      chromadb:
        condition: service_started
    restart: unless-stopped

  chromadb:
    image: docker.io/chromadb/chroma:latest
    ports:
      - "${CHROMADB_BIND:-127.0.0.1}:8100:8000"
    volumes:
      - chromadb-data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=FALSE
    restart: unless-stopped

  searxng:
    # Pinned, not :latest — odysseus waits on searxng's healthcheck
    # (depends_on: condition: service_healthy), so a broken upstream `latest`
    # tag blocks the whole app from starting. 2026.6.2 crashes on boot with
    # `KeyError: 'default_doi_resolver'`, failing the healthcheck (issue #1414).
    # Bump this deliberately after verifying a newer tag boots clean.
    image: docker.io/searxng/searxng:2026.5.31-7159b8aed
    entrypoint:
      - /bin/sh
      - -c
      - |
        set -eu
        if [ ! -s /etc/searxng/settings.yml ] || grep -q 'odysseus-local-searxng-json-2026-05-30\|__SEARXNG_SECRET__' /etc/searxng/settings.yml; then
          secret="$${SEARXNG_SECRET:-}"
          if [ -z "$$secret" ]; then
            secret="$$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
          fi
          sed "s|__SEARXNG_SECRET__|$$secret|g" /tmp/searxng-settings.yml.template > /etc/searxng/settings.yml
        fi
        exec /usr/local/searxng/entrypoint.sh
    ports:
      - "127.0.0.1:8585:8080"
    volumes:
      - searxng-data:/etc/searxng
      - ./config/searxng/settings.yml:/tmp/searxng-settings.yml.template:ro,z
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
      - SEARXNG_SECRET=${SEARXNG_SECRET:-}
    # The official searxng image runs as the non-root `searxng` user, but its
    # entrypoint still needs to chown /etc/searxng on first boot, drop privs via
    # su-exec, and (with our wrapper above) write settings.yml into the named
    # volume. Without these capabilities the wrapper aborts at the redirection
    # with EACCES and the container fails its healthcheck with permission
    # errors during setup. Mirrors the cap set recommended by the upstream
    # searxng-docker compose file. See issue #721.
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\""]
      interval: 5s
      timeout: 6s
      retries: 20
      start_period: 10s
    restart: unless-stopped

  ntfy:
    image: docker.io/binwiederhier/ntfy
    command: serve
    ports:
      - "${NTFY_BIND:-127.0.0.1}:8091:80"
    volumes:
      - ntfy-cache:/var/cache/ntfy
    environment:
      - NTFY_BASE_URL=${NTFY_BASE_URL:-http://localhost:8091}
    restart: unless-stopped

volumes:
  searxng-data:
  chromadb-data:
  ntfy-cache:


networks:
  ollama-net:
    external: true
    name: ollama_ollama-net

================================================================
FILE: /mnt/monarch/appdata/odysseus/docker-compose.yml
================================================================
  File: /mnt/monarch/appdata/odysseus/docker-compose.yml
  Size: 6277      	Blocks: 16         IO Block: 4096   regular file
Device: 27h/39d	Inode: 276184      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-06-23 11:54:11.671264290 +0000
Modify: 2026-06-23 11:54:08.332244306 +0000
Change: 2026-06-23 11:54:08.332244306 +0000
 Birth: 2026-06-18 08:49:43.277940154 +0000

services:
  odysseus:
    build: .
    networks:
      - ollama-net
    ports:
      - "${APP_BIND:-127.0.0.1}:${APP_PORT:-7000}:7000"
    volumes:
      - ./data:/app/data:z
      - ./logs:/app/logs:z
      # Cookbook remote-server SSH identity. Odysseus can generate a key here;
      # add the shown public key to each remote server's authorized_keys.
      - ./data/ssh:/app/.ssh:z
      # Cookbook local model cache. Inside Docker, "Local" means the Odysseus
      # container, so persist its HuggingFace cache under ./data/huggingface.
      - ./data/huggingface:/app/.cache/huggingface:z
      # Cookbook-installed Python CLIs/packages (vLLM, llama-cpp-python, etc.)
      # land under /app/.local for the odysseus user. Persist them so a
      # container recreate does not silently remove installed serve engines.
      - ./data/local:/app/.local:z

      # Homelab audit access
      - /hive:/home/user/homelab/hive:z
      - /mnt/monarch:/home/user/homelab/monarch:z
    extra_hosts:
      # Lets the container reach local services on the Docker host, including
      # Ollama at http://host.docker.internal:11434.
      - "host.docker.internal:host-gateway"
    environment:
      - LLM_HOST=${LLM_HOST:-localhost}
      - LLM_HOSTS=${LLM_HOSTS:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-}
      - RESEARCH_LLM_ENDPOINT=${RESEARCH_LLM_ENDPOINT:-}
      - HF_TOKEN=${HF_TOKEN:-}
      - HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-}
      - SEARXNG_INSTANCE=http://searxng:8080
      - CHROMADB_HOST=chromadb
      - CHROMADB_PORT=8000
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./data/app.db}
      - AUTH_ENABLED=${AUTH_ENABLED:-true}
      - LOCALHOST_BYPASS=${LOCALHOST_BYPASS:-false}
      - ODYSSEUS_ADMIN_USER=${ODYSSEUS_ADMIN_USER:-admin}
      - ODYSSEUS_ADMIN_PASSWORD=${ODYSSEUS_ADMIN_PASSWORD:-}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost,http://127.0.0.1}
      - SECURE_COOKIES=${SECURE_COOKIES:-false}
      - EMBEDDING_URL=${EMBEDDING_URL:-}
      - EMBEDDING_MODEL=${EMBEDDING_MODEL:-}
      - EMBEDDING_API_KEY=${EMBEDDING_API_KEY:-}
      - FASTEMBED_MODEL=${FASTEMBED_MODEL:-sentence-transformers/all-MiniLM-L6-v2}
      - FASTEMBED_CACHE_PATH=${FASTEMBED_CACHE_PATH:-}
      - CLEANUP_INTERVAL_HOURS=${CLEANUP_INTERVAL_HOURS:-24}
      - ODYSSEUS_INPROCESS_POLLERS=${ODYSSEUS_INPROCESS_POLLERS:-1}
      - ODYSSEUS_INPROCESS_TASKS=${ODYSSEUS_INPROCESS_TASKS:-1}
      - ODYSSEUS_SCRIPT_HOST=${ODYSSEUS_SCRIPT_HOST:-localhost}
      - ODYSSEUS_CHAT_UPLOAD_MAX_BYTES=${ODYSSEUS_CHAT_UPLOAD_MAX_BYTES:-10485760}
      - DATA_BRAVE_API_KEY=${DATA_BRAVE_API_KEY:-}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY:-}
      - GOOGLE_PSE_CX=${GOOGLE_PSE_CX:-}
      - TAVILY_API_KEY=${TAVILY_API_KEY:-}
      - SERPER_API_KEY=${SERPER_API_KEY:-}
      # PUID / PGID — the user/group the container drops to before
      # running uvicorn (entrypoint also chowns /app/data + /app/logs
      # to match, so bind-mounted files stay editable from the host).
      # 1000 is the default first user on most Linux installs. If your
      # host user has a different id, override here or via .env, e.g.:
      #   PUID=1001
      #   PGID=1001
      # Find yours with:  id -u  /  id -g
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
    depends_on:
      searxng:
        condition: service_healthy
      chromadb:
        condition: service_started
    restart: unless-stopped

  chromadb:
    image: docker.io/chromadb/chroma:latest
    ports:
      - "${CHROMADB_BIND:-127.0.0.1}:8100:8000"
    volumes:
      - chromadb-data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=FALSE
    restart: unless-stopped

  searxng:
    # Pinned, not :latest — odysseus waits on searxng's healthcheck
    # (depends_on: condition: service_healthy), so a broken upstream `latest`
    # tag blocks the whole app from starting. 2026.6.2 crashes on boot with
    # `KeyError: 'default_doi_resolver'`, failing the healthcheck (issue #1414).
    # Bump this deliberately after verifying a newer tag boots clean.
    image: docker.io/searxng/searxng:2026.5.31-7159b8aed
    entrypoint:
      - /bin/sh
      - -c
      - |
        set -eu
        if [ ! -s /etc/searxng/settings.yml ] || grep -q 'odysseus-local-searxng-json-2026-05-30\|__SEARXNG_SECRET__' /etc/searxng/settings.yml; then
          secret="$${SEARXNG_SECRET:-}"
          if [ -z "$$secret" ]; then
            secret="$$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
          fi
          sed "s|__SEARXNG_SECRET__|$$secret|g" /tmp/searxng-settings.yml.template > /etc/searxng/settings.yml
        fi
        exec /usr/local/searxng/entrypoint.sh
    ports:
      - "127.0.0.1:8585:8080"
    volumes:
      - searxng-data:/etc/searxng
      - ./config/searxng/settings.yml:/tmp/searxng-settings.yml.template:ro,z
    environment:
      - SEARXNG_BASE_URL=http://localhost:8080/
      - SEARXNG_SECRET=${SEARXNG_SECRET:-}
    # The official searxng image runs as the non-root `searxng` user, but its
    # entrypoint still needs to chown /etc/searxng on first boot, drop privs via
    # su-exec, and (with our wrapper above) write settings.yml into the named
    # volume. Without these capabilities the wrapper aborts at the redirection
    # with EACCES and the container fails its healthcheck with permission
    # errors during setup. Mirrors the cap set recommended by the upstream
    # searxng-docker compose file. See issue #721.
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5).read(1)\""]
      interval: 5s
      timeout: 6s
      retries: 20
      start_period: 10s
    restart: unless-stopped

  ntfy:
    image: docker.io/binwiederhier/ntfy
    command: serve
    ports:
      - "${NTFY_BIND:-127.0.0.1}:8091:80"
    volumes:
      - ntfy-cache:/var/cache/ntfy
    environment:
      - NTFY_BASE_URL=${NTFY_BASE_URL:-http://localhost:8091}
    restart: unless-stopped

volumes:
  searxng-data:
  chromadb-data:
  ntfy-cache:


networks:
  ollama-net:
    external: true
    name: ollama_ollama-net

================================================================
FILE: /mnt/monarch/appdata/hermes/compose.yml
================================================================
  File: /mnt/monarch/appdata/hermes/compose.yml
  Size: 1036      	Blocks: 8          IO Block: 4096   regular file
Device: 27h/39d	Inode: 281112      Links: 1
Access: (0644/-rw-r--r--)  Uid: (10000/ UNKNOWN)   Gid: (10000/ UNKNOWN)
Access: 2026-06-20 05:04:02.065026214 +0000
Modify: 2026-06-20 05:03:54.445979765 +0000
Change: 2026-06-20 05:03:54.445979765 +0000
 Birth: 2026-06-20 04:15:43.886159676 +0000

services:
  hermes:
    image: nousresearch/hermes-agent:latest
    container_name: hermes

    restart: unless-stopped

    command:
      -  gateway
      -  run

    environment:
      TZ: Asia/Tokyo
      HERMES_DASHBOARD: "1"
     # HERMES_DASHBOARD_INSECURE: "true"
      HERMES_DASHBOARD_BASIC_AUTH_USERNAME: admin
      HERMES_DASHBOARD_BASIC_AUTH_PASSWORD: <passwordhere>
      OLLAMA_BASE_URL: http://ollama:11434

    volumes:
      - /mnt/monarch/appdata/hermes:/opt/data

    shm_size: 1g

    networks:
      - proxy
      - ollama-net

    labels:
      - traefik.enable=true

      - traefik.http.routers.hermes.rule=Host(`hermes.fatherfankscloud.uk`)
      - traefik.http.routers.hermes.entrypoints=websecure
      - traefik.http.routers.hermes.tls=true
      - traefik.http.routers.hermes.tls.certresolver=le

      - traefik.http.services.hermes.loadbalancer.server.port=9119

      - traefik.docker.network=proxy

networks:
  proxy:
    external: true

  ollama-net:
    external: true
    name: ollama_ollama-net

================================================================
FILE: /mnt/monarch/appdata/honcho/compose.yml
================================================================
  File: /mnt/monarch/appdata/honcho/compose.yml
  Size: 2207      	Blocks: 8          IO Block: 4096   regular file
Device: 27h/39d	Inode: 279851      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-06-25 12:11:46.132028376 +0000
Modify: 2026-06-20 05:04:53.451339387 +0000
Change: 2026-06-20 05:04:53.451339387 +0000
 Birth: 2026-06-20 03:50:28.445900611 +0000

services:

  api:
    build:
      context: .
      dockerfile: Dockerfile

    container_name: honcho-api

    restart: unless-stopped

    entrypoint: ["sh", "docker/entrypoint.sh"]

    depends_on:
      database:
        condition: service_started
      redis:
        condition: service_started

    environment:
      TZ: Asia/Tokyo
      DB_CONNECTION_URI: postgresql+psycopg://postgres:${POSTGRES_PASSWORD}@database:5432/postgres
      CACHE_URL: redis://redis:6379/0?suppress=true
      CACHE_ENABLED: "true"

    env_file:
      - .env

    networks:
      - ollama-net
      - proxy

    labels:
      - traefik.enable=true
      - traefik.http.routers.honcho.rule=Host(`honcho.fatherfankscloud.uk`)
      - traefik.http.routers.honcho.entrypoints=websecure
      - traefik.http.routers.honcho.tls=true
      - traefik.http.routers.honcho.tls.certresolver=le
      - traefik.http.services.honcho.loadbalancer.server.port=8000
      - traefik.docker.network=proxy

  deriver:
    build:
      context: .
      dockerfile: Dockerfile

    container_name: honcho-deriver

    restart: unless-stopped

    entrypoint:
      - /app/.venv/bin/python
      - -m
      - src.deriver

    depends_on:
      - api

    environment:
      TZ: Asia/Tokyo
      DB_CONNECTION_URI: postgresql+psycopg://postgres:${POSTGRES_PASSWORD}@database:5432/postgres
      CACHE_URL: redis://redis:6379/0?suppress=true
      CACHE_ENABLED: "true"

    env_file:
      - .env

    networks:
      - ollama-net

  database:
    image: pgvector/pgvector:pg15

    container_name: honcho-postgres

    restart: unless-stopped

    environment:
      TZ: Asia/Tokyo
      POSTGRES_DB: postgres
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata

    volumes:
      - /mnt/monarch/appdata/honcho/postgres:/var/lib/postgresql/data

    networks:
      - ollama-net

  redis:
    image: redis:8.2

    container_name: honcho-redis

    restart: unless-stopped

    volumes:
      - /mnt/monarch/appdata/honcho/redis:/data

    networks:
      - ollama-net

networks:

  proxy:
    external: true

  ollama-net:
    external: true
    name: ollama_ollama-net

================================================================
FILE: /mnt/monarch/appdata/n8n/compose.yml
================================================================
  File: /mnt/monarch/appdata/n8n/compose.yml
  Size: 842       	Blocks: 8          IO Block: 4096   regular file
Device: 27h/39d	Inode: 320884      Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-07-08 09:18:28.585695855 +0000
Modify: 2026-06-25 13:34:16.302277239 +0000
Change: 2026-06-25 13:34:16.302277239 +0000
 Birth: 2026-06-24 09:46:28.319421823 +0000

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped

    ports:
      - "5678:5678"

    environment:
      - TZ=Asia/Tokyo
      - GENERIC_TIMEZONE=Asia/Tokyo
      - N8N_HOST=mocha
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - N8N_SECURE_COOKIE=false
      - NODES_EXCLUDE:"[]"

      # Generate once:
      # openssl rand -hex 32
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}

      # Helpful for AI workflows
      - N8N_RUNNERS_ENABLED=true

    volumes:
      - /mnt/monarch/appdata/n8n:/home/node/.n8n
      - /mnt/monarch/appdata/n8n/workflows:/workflows
      - /mnt/monarch/appdata/n8n/reports:/reports

    networks:
      - homelab
      - ai-assistant

networks:
  homelab:
    external: true

  ai-assistant:
    external: true

================================================================
FILE: /mnt/monarch/appdata/beszel/compose.yml
================================================================
  File: /mnt/monarch/appdata/beszel/compose.yml
  Size: 339       	Blocks: 8          IO Block: 4096   regular file
Device: 27h/39d	Inode: 321160      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-06-25 12:11:46.133028381 +0000
Modify: 2026-06-24 10:25:04.235936275 +0000
Change: 2026-06-24 10:25:04.235936275 +0000
 Birth: 2026-06-24 10:25:04.234936269 +0000

services:
  beszel:
    image: henrygd/beszel:latest
    container_name: beszel
    restart: unless-stopped

    ports:
      - "8090:8090"

    environment:
      - APP_URL=http://mocha:8090

    volumes:
      - /mnt/monarch/appdata/beszel/beszel_data:/beszel_data

    networks:
      - homelab

networks:
  homelab:
    external: true

================================================================
FILE: /mnt/monarch/appdata/beszel_agent/compose.yml
================================================================
  File: /mnt/monarch/appdata/beszel_agent/compose.yml
  Size: 606       	Blocks: 8          IO Block: 4096   regular file
Device: 27h/39d	Inode: 321233      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-06-24 13:21:51.593804434 +0000
Modify: 2026-06-24 13:21:39.690736548 +0000
Change: 2026-06-24 13:21:39.690736548 +0000
 Birth: 2026-06-24 10:34:00.454144902 +0000

services:
  beszel-agent:
    image: henrygd/beszel-agent
    container_name: beszel-agent
    restart: unless-stopped
    network_mode: host
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./beszel_agent_data:/var/lib/beszel-agent
      # monitor other disks / partitions by mounting a folder in /extra-filesystems
      # - /mnt/disk/.beszel:/extra-filesystems/sda1:ro
    environment:
      LISTEN: 45876
      KEY: 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC7OEncn69b0yveSg29GrBJFzy+1bG/4rQoo6Ic+ZK4b'
      TOKEN: 21c9-e2488b6122-bb-2beefea25b38
      HUB_URL: http://mocha:8090

================================================================
FILE: /hive/Hotio/compose.yml
================================================================
  File: /hive/Hotio/compose.yml
  Size: 1983      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 65665       Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-09 11:56:31.460059502 +0000
Modify: 2025-03-04 04:47:00.107769629 +0000
Change: 2025-03-04 04:47:00.107769629 +0000
 Birth: 2023-07-27 02:04:38.037066639 +0000

name: hotio
services:
    qbittorrent:
        cap_add:
            - NET_ADMIN
        cpu_shares: 50
        command: []
        container_name: qbittorrent
        deploy:
            resources:
                limits:
                    memory: "18480103424"
        dns:
            - 10.64.0.1
            - 1.1.1.1
            - 1.0.0.1
        environment:
            PGID: "1000"
            PRIVOXY_ENABLED: "true"
            PUID: "1000"
            TZ: Etc/UTC
            UMASK: "002"
            VPN_ADDITIONAL_PORTS: 6789/tcp,6789/udp
            VPN_CONF: wg0
            VPN_ENABLED: "true"
            VPN_IP_CHECK_DELAY: "10"
            VPN_IP_CHECK_EXIT: "true"
            VPN_LAN_NETWOK: 192.168.0.0/24
            WEBUI_PORTS: 8080/tcp,8080/udp
        hostname: qbittorrent
        image: cr.hotio.dev/hotio/qbittorrent:latest
        networks:
            default: null
        ports:
            - mode: ingress
              target: 8080
              published: "8080"
              protocol: tcp
            - mode: ingress
              target: 8118
              published: "8118"
              protocol: tcp
            - mode: ingress
              target: 6789
              published: "6789"
              protocol: tcp
        restart: unless-stopped
        sysctls:
            net.ipv4.conf.all.src_valid_mark: "1"
            net.ipv6.conf.all.disable_ipv6: "1"
        volumes:
            - type: bind
              source: /hive/Hotio/config
              target: /config
              bind:
                create_host_path: true
            - type: bind
              source: /hive/downloads/completed
              target: /downloads
              bind:
                create_host_path: true
networks:
    default:
        name: hotio_default
x-casaos:
    author: self
    category: self
    hostname: ""
    icon: ""
    index: /
    is_uncontrolled: false
    port_map: ""
    scheme: http
    title:
        custom: qbittorrent

================================================================
FILE: /hive/Hotio/sonarr/compose.yml
================================================================
  File: /hive/Hotio/sonarr/compose.yml
  Size: 461       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 69757       Links: 1
Access: (0664/-rw-rw-r--)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2023-08-04 07:06:24.675625323 +0000
Modify: 2023-08-04 06:46:42.612317350 +0000
Change: 2023-08-04 06:46:42.640317433 +0000
 Birth: 2023-08-04 06:46:42.612317350 +0000

version: "3.9"

services:
  sonarr:
    container_name: sonarr
    image: cr.hotio.dev/hotio/sonarr:v4
    #network_mode: container:qbittorrent
    ports:
      - "8989:8989"
    environment:
      - PUID=1000
      - PGID=1000
      - UMASK=002
      - TZ=America/Denver
    volumes:
      - /hive/Hotio/sonarr/config:/config
      - /hive/NZBget/config/downloads/completed/Sonarr:/downloads #optional
      - /hive/jellyfin/tv:/tv
    restart: unless-stopped

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/compose/compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/compose/compose.yml
  Size: 1022      	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 1201490     Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:36.223203368 +0000
Modify: 2024-03-11 20:04:41.921172711 +0000
Change: 2026-01-29 13:46:36.223203368 +0000
 Birth: 2026-01-29 13:46:36.223203368 +0000

version: "3.9"
services: 
  app: 
    depends_on: 
      - db
    environment: 
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    image: nextcloud
    links: 
      - db
    ports: 
      - "8888:80"
      - "8443:443"
    restart: always
    volumes: 
      - "/your-pool/Cloud/nextcloud/nextcloud:/var/www/html"
      - "/your-pool/Cloud/nextcloud/apps:/var/www/html/custom_apps"
      - "/your-pool/Cloud/nextcloud/config:/var/www/html/config"
      - "/your-pool/Cloud/nextcloud/data:/var/www/html/data"
      - "/your-pool/Cloud/nextcloud/theme:/var/www/html/themes/<YOUR_CUSTOM_THEME>"
  db: 
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    environment: 
      - MYSQL_ROOT_PASSWORD= <passwordhere>
      - MYSQL_PASSWORD= <passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    image: "mariadb:10.5"
    restart: always
    volumes: 
      - "/your-pool/Cloud/nextcloud/db:/var/lib/mysql"

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/compose/nextcloud-data/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/compose/nextcloud-data/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 1219860     Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:44.303241534 +0000
Modify: 2024-03-11 20:04:53.021224290 +0000
Change: 2026-01-29 13:46:44.303241534 +0000
 Birth: 2026-01-29 13:46:44.303241534 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/apps/mail/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/apps/mail/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 1198555     Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:31.705182049 +0000
Modify: 2024-03-11 20:04:38.489156767 +0000
Change: 2026-01-29 13:46:31.705182049 +0000
 Birth: 2026-01-29 13:46:31.705182049 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/nextcloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/nextcloud/nextcloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 1247770     Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:47:01.218321596 +0000
Modify: 2024-03-11 20:05:14.481324081 +0000
Change: 2026-01-29 13:47:01.218321596 +0000
 Birth: 2026-01-29 13:47:01.218321596 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/Cloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/Cloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 1157748     Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:45:21.211851610 +0000
Modify: 2024-03-11 20:03:11.268752416 +0000
Change: 2026-01-29 13:45:21.212851615 +0000
 Birth: 2026-01-29 13:45:21.211851610 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/stuff/backupJan2026/nextcloud/old/Cloud/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/stuff/backupJan2026/nextcloud/old/Cloud/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 1188832     Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:26.388156981 +0000
Modify: 2024-03-11 20:04:28.957112498 +0000
Change: 2026-01-29 13:46:26.388156981 +0000
 Birth: 2026-01-29 13:46:26.388156981 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/AppData/nextcloud/var/www/html/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/AppData/nextcloud/var/www/html/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 148841      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-12 11:52:16.720214000 +0000
Modify: 2023-10-05 23:57:17.697813000 +0000
Change: 2026-01-12 11:52:16.720214082 +0000
 Birth: 2026-01-12 11:52:16.720214082 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/AppData/portainer/compose/17/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/17/docker-compose.yml
  Size: 1194      	Blocks: 12         IO Block: 1536   regular file
Device: 28h/40d	Inode: 127371      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.495366333 +0000
Modify: 2023-10-12 03:37:19.244060000 +0000
Change: 2026-01-12 11:52:08.513217138 +0000
 Birth: 2026-01-12 11:52:08.508217140 +0000

version: '3'
services:
  traefik:
    container_name: traefik
    image: traefik:2.6
    ports:
      - 80:80
      - 443:443
    #  - 8080:8080 # Dashboard port
    volumes:
      - /opt/appdata/traefik/:/etc/traefik/
    networks:
      - proxy # rename this to your custom docker network
    labels:
      traefik.http.routers.api.rule: Host(`trfk.fatherfankscloud.uk`)    # Define the subdomain for the traefik dashboard.
      traefik.http.routers.api.entryPoints: https    # Set the Traefik entry point.
      traefik.http.routers.api.service: api@internal    # Enable Traefik API.
      traefik.enable: true   # Enable Traefik reverse proxy for the Traefik dashboard.
    environment:
      DOCKER_HOST: dockersocket
      CF_DNS_API_TOKEN: gEFlLaxnUGRKJ_5gaPwmB835h1cIi5KFlv6l7JMF
    restart: unless-stopped
    depends_on:
      - dockersocket

  dockersocket:
    container_name: dockersocket
    image: tecnativa/docker-socket-proxy
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - proxy
    environment:
      CONTAINERS: 1
      POST: 0
    privileged: true
    restart: unless-stopped


networks:
  proxy:
    driver: bridge
    external: true
================================================================
FILE: /hive/AppData/portainer/compose/38/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/38/docker-compose.yml
  Size: 362       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 127387      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.588366705 +0000
Modify: 2024-03-11 21:56:48.875428000 +0000
Change: 2026-01-12 11:52:08.520217135 +0000
 Birth: 2026-01-12 11:52:08.520217135 +0000

version: '3.3'
services:
    kapowarr:
        container_name: kapowarr
        volumes:
            - '/hive/Kapowarr/db:/app/db'
            - '/hive/NZBget/config/downloads/completed:/app/temp_downloads'
            - '/hive/cloud/data/fatherfranku/files/Kavita/Comics:/comics-1'
        ports:
            - '5656:5656'
        image: 'mrcas/kapowarr:latest'
================================================================
FILE: /hive/AppData/portainer/compose/42/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/42/docker-compose.yml
  Size: 599       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 127375      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.533366485 +0000
Modify: 2025-03-13 00:57:57.453150000 +0000
Change: 2026-01-12 11:52:08.515217137 +0000
 Birth: 2026-01-12 11:52:08.515217137 +0000

version: '3.8'

services:
  docker-osx:
    container_name: bluebubbles-macos
    image: sickcodes/docker-osx:latest
    restart: unless-stopped
    devices:
      - "/dev/kvm"
    ports:
      - "50922:10022"
    volumes:
      - "/tmp/.X11-unix:/tmp/.X11-unix"
    environment:
      DISPLAY: "${DISPLAY:-:0.0}"
      GENERATE_UNIQUE: "true"
      CPU: "Haswell-noTSX"
      CPUID_FLAGS: "kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on"
      MASTER_PLIST_URL: "https://raw.githubusercontent.com/sickcodes/osx-serial-generator/master/config-custom-sonoma.plist"
      SHORTNAME: "sonoma"

================================================================
FILE: /hive/AppData/portainer/compose/35/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/35/docker-compose.yml
  Size: 900       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 127381      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.570366633 +0000
Modify: 2024-03-11 20:10:38.518839000 +0000
Change: 2026-01-12 11:52:08.517217136 +0000
 Birth: 2026-01-12 11:52:08.517217136 +0000

--- 
version: "2"
services: 
  app: 
    depends_on: 
      - db
    environment: 
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    image: nextcloud
    links: 
      - db
    ports: 
      - "8088:80"
    restart: always
    volumes: 
      - "/hive/cloud/nextcloud:/var/www/html"
      - "/hive/cloud/apps:/var/www/html/custom_apps"
      - "/hive/cloud/config:/var/www/html/config"
      - "/hive/cloud/data:/var/www/html/data"
      - "/hive/cloud/theme:/var/www/html/themes/<YOUR_CUSTOM_THEME>"
  db: 
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    environment: 
      - MYSQL_ROOT_PASSWORD=<passwordhere>
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    image: "mariadb:10.5"
    restart: always
    volumes: 
      - "/hive/cloud/db:/var/lib/mysql"
================================================================
FILE: /hive/AppData/portainer/compose/37/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/37/docker-compose.yml
  Size: 485       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 127385      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.587366701 +0000
Modify: 2024-03-11 21:40:11.153821000 +0000
Change: 2026-01-12 11:52:08.519217135 +0000
 Birth: 2026-01-12 11:52:08.519217135 +0000

version: '3.9'
services:
    kavita:
        image: jvmilazz0/kavita:latest
        container_name: kavita
        volumes:
            - /hive/cloud/data/fatherfranku/files/Kavita/manga:/manga
            - /hive/cloud/data/fatherfranku/files/Kavita/books:/books
            - /hive/cloud/data/fatherfranku/files/Kavita/comics:/comics
            - /hive/cloud/data/fatherfranku/files/Kavita/data:/kavita/config
        ports:
            - "5000:5000"
        restart: unless-stopped
================================================================
FILE: /hive/AppData/portainer/compose/43/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/43/docker-compose.yml
  Size: 554       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 127377      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.549366549 +0000
Modify: 2025-04-23 22:39:19.614258000 +0000
Change: 2026-01-12 11:52:08.516217137 +0000
 Birth: 2026-01-12 11:52:08.515217137 +0000

services:
  code-server:
    image: lscr.io/linuxserver/code-server:latest
    container_name: code-server
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - PASSWORD=<passwordhere> #optional
      - HASHED_PASSWORD= #optional
      - SUDO_PASSWORD=<passwordhere> #optional
      - SUDO_PASSWORD_HASH= #optional
      - PROXY_DOMAIN=coder.fatherfankscloud.uk #optional
      - DEFAULT_WORKSPACE=/config/workspace #optional
    volumes:
      - /hive/code-server/config:/config
    ports:
      - 8050:8443
    restart: unless-stopped
================================================================
FILE: /hive/AppData/portainer/compose/44/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/44/docker-compose.yml
  Size: 417       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 127379      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.551366557 +0000
Modify: 2025-04-26 19:40:54.930918000 +0000
Change: 2026-01-12 11:52:08.517217136 +0000
 Birth: 2026-01-12 11:52:08.516217137 +0000

---
version: "2.1"
services:
  flaresolverr:
    # DockerHub mirror flaresolverr/flaresolverr:latest
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - LOG_HTML=${LOG_HTML:-false}
      - CAPTCHA_SOLVER=${CAPTCHA_SOLVER:-none}
      - TZ=Europe/London
    ports:
      - "${PORT:-8191}:8191"
    restart: unless-stopped 

================================================================
FILE: /hive/AppData/portainer/compose/33/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/33/docker-compose.yml
  Size: 832       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 127383      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.585366692 +0000
Modify: 2024-02-11 06:44:55.563097000 +0000
Change: 2026-01-12 11:52:08.518217136 +0000
 Birth: 2026-01-12 11:52:08.518217136 +0000

name: nzbget
services:
  nzbget:
    cpu_shares: 90
    command: []
    container_name: nzbget
    deploy:
      resources:
        limits:
          memory: 25434M
    environment:
      - PGID=1000
      - PUID=1000
      - TZ=Denver
      - UMASK=002
    image: cr.hotio.dev/hotio/nzbget
    restart: unless-stopped
    volumes:
      - type: bind
        source: /hive/NZBget/config
        target: /config
        bind:
          create_host_path: true
      - type: bind
        source: /hive/downloads
        target: /downloads
        bind:
          create_host_path: true
    ports: []
    devices: []
    cap_add: []
    network_mode: container:qbittorrent
    privileged: false
x-casaos:
  author: self
  category: self
  hostname: ""
  icon: ""
  index: /
  port_map: "6789"
  scheme: http
  title:
    custom: NZBGet

================================================================
FILE: /hive/AppData/portainer/compose/39/docker-compose.yml
================================================================
  File: /hive/AppData/portainer/compose/39/docker-compose.yml
  Size: 408       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 127373      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.514366409 +0000
Modify: 2025-01-12 19:58:17.979880000 +0000
Change: 2026-01-12 11:52:08.514217137 +0000
 Birth: 2026-01-12 11:52:08.514217137 +0000

---
services:
  readarr:
    image: lscr.io/linuxserver/readarr:develop
    container_name: readarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    volumes:
      - /hive/readarr:/config
      - /hive/cloud/data/fatherfranku/files/Kavita/Books:/books #optional
      - /hive/downloads/completed/Readarr:/downloads #optional
    ports:
      - 8787:8787
    restart: unless-stopped
================================================================
FILE: /hive/ollama/compose.yml
================================================================
  File: /hive/ollama/compose.yml
  Size: 1599      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 743095      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-02-13 13:19:50.739767350 +0000
Modify: 2026-06-25 10:17:22.745902261 +0000
Change: 2026-06-25 10:17:22.745902261 +0000
 Birth: 2026-02-13 13:19:50.739767350 +0000

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - /hive/ollama:/root/.ollama
    environment:
      - OLLAMA_KV_CACHE_TYPE=q8_0
      - OLLAMA_CONTEXT_LENGTH=2048
      - OLLAMA_MAX_LOADED_MODELS=1
      - OLLAMA_NUM_PARALLEL=1
      - OLLAMA_API_KEY=df4ed965cd5b4fbcba115a15046acfdd.9H6LIn0-vMFn3h9itacE3TC-
      - CUDA_VISIBLE_DEVICES=-1

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]  
 # gpus: all
    mem_limit: 12g
    shm_size: "4gb"
    networks:
      - ollama-net
      - ai-assistant
    labels:
      - "traefik.enable=false"

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    depends_on:
      - ollama
    volumes:
      - /mnt/monarch/appdata/open-webui:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
    networks:
      - ollama-net
      - proxy
      - ai-assistant
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.openwebui.rule=Host(`chat.fatherfankscloud.uk`)"
      - "traefik.http.routers.openwebui.entrypoints=websecure"
      - "traefik.http.routers.openwebui.tls.certresolver=letsencrypt"
      - "traefik.http.services.openwebui.loadbalancer.server.port=8080"
      - "traefik.docker.network=proxy"

networks:
  ollama-net:
    driver: bridge

  proxy:
    external: true

  ai-assistant:
    external: true

================================================================
FILE: /hive/portainer/compose/42/docker-compose.yml
================================================================
  File: /hive/portainer/compose/42/docker-compose.yml
  Size: 599       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 221664      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.143848000 +0000
Modify: 2025-03-13 00:57:57.453150000 +0000
Change: 2026-01-13 11:35:56.143848282 +0000
 Birth: 2026-01-13 11:35:56.143848282 +0000

version: '3.8'

services:
  docker-osx:
    container_name: bluebubbles-macos
    image: sickcodes/docker-osx:latest
    restart: unless-stopped
    devices:
      - "/dev/kvm"
    ports:
      - "50922:10022"
    volumes:
      - "/tmp/.X11-unix:/tmp/.X11-unix"
    environment:
      DISPLAY: "${DISPLAY:-:0.0}"
      GENERATE_UNIQUE: "true"
      CPU: "Haswell-noTSX"
      CPUID_FLAGS: "kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on"
      MASTER_PLIST_URL: "https://raw.githubusercontent.com/sickcodes/osx-serial-generator/master/config-custom-sonoma.plist"
      SHORTNAME: "sonoma"

================================================================
FILE: /hive/portainer/compose/35/docker-compose.yml
================================================================
  File: /hive/portainer/compose/35/docker-compose.yml
  Size: 900       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 221670      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.146848000 +0000
Modify: 2024-03-11 20:10:38.518839000 +0000
Change: 2026-01-13 11:35:56.146848294 +0000
 Birth: 2026-01-13 11:35:56.146848294 +0000

--- 
version: "2"
services: 
  app: 
    depends_on: 
      - db
    environment: 
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    image: nextcloud
    links: 
      - db
    ports: 
      - "8088:80"
    restart: always
    volumes: 
      - "/hive/cloud/nextcloud:/var/www/html"
      - "/hive/cloud/apps:/var/www/html/custom_apps"
      - "/hive/cloud/config:/var/www/html/config"
      - "/hive/cloud/data:/var/www/html/data"
      - "/hive/cloud/theme:/var/www/html/themes/<YOUR_CUSTOM_THEME>"
  db: 
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    environment: 
      - MYSQL_ROOT_PASSWORD=<passwordhere>
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    image: "mariadb:10.5"
    restart: always
    volumes: 
      - "/hive/cloud/db:/var/lib/mysql"
================================================================
FILE: /hive/portainer/compose/38/docker-compose.yml
================================================================
  File: /hive/portainer/compose/38/docker-compose.yml
  Size: 362       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 221676      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.148848000 +0000
Modify: 2024-03-11 21:56:48.875428000 +0000
Change: 2026-01-13 11:35:56.148848302 +0000
 Birth: 2026-01-13 11:35:56.148848302 +0000

version: '3.3'
services:
    kapowarr:
        container_name: kapowarr
        volumes:
            - '/hive/Kapowarr/db:/app/db'
            - '/hive/NZBget/config/downloads/completed:/app/temp_downloads'
            - '/hive/cloud/data/fatherfranku/files/Kavita/Comics:/comics-1'
        ports:
            - '5656:5656'
        image: 'mrcas/kapowarr:latest'
================================================================
FILE: /hive/portainer/compose/37/docker-compose.yml
================================================================
  File: /hive/portainer/compose/37/docker-compose.yml
  Size: 485       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 221674      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.147848000 +0000
Modify: 2024-03-11 21:40:11.153821000 +0000
Change: 2026-01-13 11:35:56.148848302 +0000
 Birth: 2026-01-13 11:35:56.147848298 +0000

version: '3.9'
services:
    kavita:
        image: jvmilazz0/kavita:latest
        container_name: kavita
        volumes:
            - /hive/cloud/data/fatherfranku/files/Kavita/manga:/manga
            - /hive/cloud/data/fatherfranku/files/Kavita/books:/books
            - /hive/cloud/data/fatherfranku/files/Kavita/comics:/comics
            - /hive/cloud/data/fatherfranku/files/Kavita/data:/kavita/config
        ports:
            - "5000:5000"
        restart: unless-stopped
================================================================
FILE: /hive/portainer/compose/44/docker-compose.yml
================================================================
  File: /hive/portainer/compose/44/docker-compose.yml
  Size: 417       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 221668      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.145848000 +0000
Modify: 2025-04-26 19:40:54.930918000 +0000
Change: 2026-01-13 11:35:56.145848290 +0000
 Birth: 2026-01-13 11:35:56.145848290 +0000

---
version: "2.1"
services:
  flaresolverr:
    # DockerHub mirror flaresolverr/flaresolverr:latest
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - LOG_HTML=${LOG_HTML:-false}
      - CAPTCHA_SOLVER=${CAPTCHA_SOLVER:-none}
      - TZ=Europe/London
    ports:
      - "${PORT:-8191}:8191"
    restart: unless-stopped 

================================================================
FILE: /hive/portainer/compose/33/docker-compose.yml
================================================================
  File: /hive/portainer/compose/33/docker-compose.yml
  Size: 832       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 221672      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.147848000 +0000
Modify: 2024-02-11 06:44:55.563097000 +0000
Change: 2026-01-13 11:35:56.147848298 +0000
 Birth: 2026-01-13 11:35:56.147848298 +0000

name: nzbget
services:
  nzbget:
    cpu_shares: 90
    command: []
    container_name: nzbget
    deploy:
      resources:
        limits:
          memory: 25434M
    environment:
      - PGID=1000
      - PUID=1000
      - TZ=Denver
      - UMASK=002
    image: cr.hotio.dev/hotio/nzbget
    restart: unless-stopped
    volumes:
      - type: bind
        source: /hive/NZBget/config
        target: /config
        bind:
          create_host_path: true
      - type: bind
        source: /hive/downloads
        target: /downloads
        bind:
          create_host_path: true
    ports: []
    devices: []
    cap_add: []
    network_mode: container:qbittorrent
    privileged: false
x-casaos:
  author: self
  category: self
  hostname: ""
  icon: ""
  index: /
  port_map: "6789"
  scheme: http
  title:
    custom: NZBGet

================================================================
FILE: /hive/portainer/compose/39/docker-compose.yml
================================================================
  File: /hive/portainer/compose/39/docker-compose.yml
  Size: 408       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 221662      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.143848000 +0000
Modify: 2025-01-12 19:58:17.979880000 +0000
Change: 2026-01-13 11:35:56.143848282 +0000
 Birth: 2026-01-13 11:35:56.143848282 +0000

---
services:
  readarr:
    image: lscr.io/linuxserver/readarr:develop
    container_name: readarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    volumes:
      - /hive/readarr:/config
      - /hive/cloud/data/fatherfranku/files/Kavita/Books:/books #optional
      - /hive/downloads/completed/Readarr:/downloads #optional
    ports:
      - 8787:8787
    restart: unless-stopped
================================================================
FILE: /hive/portainer/compose/43/docker-compose.yml
================================================================
  File: /hive/portainer/compose/43/docker-compose.yml
  Size: 554       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 221666      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:35:56.144848000 +0000
Modify: 2025-04-23 22:39:19.614258000 +0000
Change: 2026-01-13 11:35:56.144848286 +0000
 Birth: 2026-01-13 11:35:56.144848286 +0000

services:
  code-server:
    image: lscr.io/linuxserver/code-server:latest
    container_name: code-server
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - PASSWORD=<passwordhere> #optional
      - HASHED_PASSWORD= #optional
      - SUDO_PASSWORD=<passwordhere>#optional
      - SUDO_PASSWORD_HASH= #optional
      - PROXY_DOMAIN=coder.fatherfankscloud.uk #optional
      - DEFAULT_WORKSPACE=/config/workspace #optional
    volumes:
      - /hive/code-server/config:/config
    ports:
      - 8050:8443
    restart: unless-stopped
================================================================
FILE: /hive/portainer/compose/49/docker-compose.yml
================================================================
  File: /hive/portainer/compose/49/docker-compose.yml
  Size: 3666      	Blocks: 12         IO Block: 4096   regular file
Device: 28h/40d	Inode: 221525      Links: 1
Access: (0600/-rw-------)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-13 12:30:29.020639671 +0000
Modify: 2026-01-13 12:30:24.662620838 +0000
Change: 2026-01-13 12:30:24.662620838 +0000
 Birth: 2026-01-13 12:30:24.662620838 +0000

---
services:
  traefik:
    container_name: traefik
    image: "traefik:3.1"
    restart: always

    ports:
      - "80:80"
      - "443:443"

    labels:
      # Homepage (safe even if Homepage is not running)
      - "homepage.group=Tools"
      - "homepage.name=traefik"
      - "homepage.icon=traefik.png"
      - "homepage.href=https://traefik.${DEFAULT_DOMAIN}"
      - "homepage.weight=3"
      - "homepage.widget.type=traefik"
      - "homepage.widget.url=https://traefik.${DEFAULT_DOMAIN}"
      - "homepage.widget.username=admin"
      - "homepage.widget.password=${TRAEFIK_PASS}"

      # Traefik Dashboard
      - "traefik.enable=true"
      - "traefik.http.middlewares.auth.basicauth.users=admin:${TRAEFIK_DASHBOARD_PASS}"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.middlewares=auth"
      - "traefik.http.routers.dashboard.rule=Host(`traefik.${DEFAULT_DOMAIN}`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.tls.certresolver=le"

      # Authentik Forward Auth (disabled for now)
      # - "traefik.http.middlewares.authentik.forwardauth.address=http://authentik-server:9000/outpost.goauthentik.io/auth/traefik"
      # - "traefik.http.middlewares.authentik.forwardauth.trustForwardHeader=true"
      # - "traefik.http.middlewares.authentik.forwardauth.authResponseHeaders=X-authentik-username,X-authentik-groups,X-authentik-entitlements,X-authentik-email,X-authentik-name,X-authentik-uid,X-authentik-jwt,X-authentik-meta-jwks,X-authentik-meta-outpost,X-authentik-meta-provider,X-authentik-meta-app,X-authentik-meta-version"

    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ${PATH_CONFIG}/traefik:/etc/traefik

    environment:
      # Global
      - TRAEFIK_GLOBAL_CHECKNEWVERSION=true
      - TRAEFIK_GLOBAL_SENDANONYMOUSUSAGE=false

      # API & Dashboard
      - TRAEFIK_API=true
      - TRAEFIK_API_DASHBOARD=true
      - TRAEFIK_API_INSECURE=false

      # Log
      - TRAEFIK_LOG_LEVEL=DEBUG

      # Entry Points
      - TRAEFIK_ENTRYPOINTS_web_ADDRESS=:80
      - TRAEFIK_ENTRYPOINTS_web_HTTP_REDIRECTIONS_ENTRYPOINT_TO=websecure
      - TRAEFIK_ENTRYPOINTS_web_HTTP_REDIRECTIONS_ENTRYPOINT_SCHEME=https

      - TRAEFIK_ENTRYPOINTS_websecure_ADDRESS=:443
      - TRAEFIK_ENTRYPOINTS_websecure_HTTP_TLS_CERTRESOLVER=le
      - TRAEFIK_ENTRYPOINTS_websecure_HTTP_TLS_DOMAINS_0_MAIN=${DEFAULT_DOMAIN}
      - TRAEFIK_ENTRYPOINTS_websecure_HTTP_TLS_DOMAINS_0_SANS=*.${DEFAULT_DOMAIN}

      # Providers
      - TRAEFIK_PROVIDERS_DOCKER=true
      - TRAEFIK_PROVIDERS_DOCKER_ENDPOINT=unix:///var/run/docker.sock
      - TRAEFIK_PROVIDERS_DOCKER_WATCH=true
      - TRAEFIK_PROVIDERS_DOCKER_EXPOSEDBYDEFAULT=false
      - TRAEFIK_PROVIDERS_DOCKER_NETWORK=proxy

      # Server Transport
      - TRAEFIK_SERVERSTRANSPORT_INSECURESKIPVERIFY=true

      # Certificate Resolver (Cloudflare DNS challenge)
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_EMAIL=${ACME_EMAIL}
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_STORAGE=/etc/traefik/acme.json
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_DNSCHALLENGE=true
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_DNSCHALLENGE_PROVIDER=cloudflare
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_DNSCHALLENGE_DELAYBEFORECHECK=0
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_DNSCHALLENGE_RESOLVERS=1.1.1.1,9.9.9.9
      - TRAEFIK_CERTIFICATESRESOLVERS_le_ACME_KEYTYPE=EC256

      # Cloudflare API
      - CLOUDFLARE_DNS_API_TOKEN
      - TZ

    networks:
      - proxy

networks:
  proxy:
    name: proxy
    external: true

================================================================
FILE: /hive/portainer/compose/50/docker-compose.yml
================================================================
  File: /hive/portainer/compose/50/docker-compose.yml
  Size: 191       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 732126      Links: 1
Access: (0600/-rw-------)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-04-28 23:36:08.752901216 +0000
Modify: 2026-04-28 23:36:08.752901216 +0000
Change: 2026-04-28 23:36:08.752901216 +0000
 Birth: 2026-04-28 23:36:08.752901216 +0000

services:
  byparr:
    image: ghcr.io/thephaseless/byparr:latest
    restart: unless-stopped
    init: true
    networks:
      - hotio_default

networks:
  hotio_default:
    external: true
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/38/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/38/docker-compose.yml
  Size: 362       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 222608      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.588366000 +0000
Modify: 2024-03-11 21:56:48.875428000 +0000
Change: 2026-01-13 11:33:55.589366709 +0000
 Birth: 2026-01-13 11:33:55.588366705 +0000

version: '3.3'
services:
    kapowarr:
        container_name: kapowarr
        volumes:
            - '/hive/Kapowarr/db:/app/db'
            - '/hive/NZBget/config/downloads/completed:/app/temp_downloads'
            - '/hive/cloud/data/fatherfranku/files/Kavita/Comics:/comics-1'
        ports:
            - '5656:5656'
        image: 'mrcas/kapowarr:latest'
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/42/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/42/docker-compose.yml
  Size: 599       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 222596      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.517366000 +0000
Modify: 2025-03-13 00:57:57.453150000 +0000
Change: 2026-01-13 11:33:55.534366489 +0000
 Birth: 2026-01-13 11:33:55.517366421 +0000

version: '3.8'

services:
  docker-osx:
    container_name: bluebubbles-macos
    image: sickcodes/docker-osx:latest
    restart: unless-stopped
    devices:
      - "/dev/kvm"
    ports:
      - "50922:10022"
    volumes:
      - "/tmp/.X11-unix:/tmp/.X11-unix"
    environment:
      DISPLAY: "${DISPLAY:-:0.0}"
      GENERATE_UNIQUE: "true"
      CPU: "Haswell-noTSX"
      CPUID_FLAGS: "kvm=on,vendor=GenuineIntel,+invtsc,vmware-cpuid-freq=on"
      MASTER_PLIST_URL: "https://raw.githubusercontent.com/sickcodes/osx-serial-generator/master/config-custom-sonoma.plist"
      SHORTNAME: "sonoma"

================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/35/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/35/docker-compose.yml
  Size: 900       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 222602      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.552366000 +0000
Modify: 2024-03-11 20:10:38.518839000 +0000
Change: 2026-01-13 11:33:55.570366633 +0000
 Birth: 2026-01-13 11:33:55.552366561 +0000

--- 
version: "2"
services: 
  app: 
    depends_on: 
      - db
    environment: 
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    image: nextcloud
    links: 
      - db
    ports: 
      - "8088:80"
    restart: always
    volumes: 
      - "/hive/cloud/nextcloud:/var/www/html"
      - "/hive/cloud/apps:/var/www/html/custom_apps"
      - "/hive/cloud/config:/var/www/html/config"
      - "/hive/cloud/data:/var/www/html/data"
      - "/hive/cloud/theme:/var/www/html/themes/<YOUR_CUSTOM_THEME>"
  db: 
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    environment: 
      - MYSQL_ROOT_PASSWORD=<passwordhere>
      - MYSQL_PASSWORD=<passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    image: "mariadb:10.5"
    restart: always
    volumes: 
      - "/hive/cloud/db:/var/lib/mysql"
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/17/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/17/docker-compose.yml
  Size: 1194      	Blocks: 12         IO Block: 1536   regular file
Device: 28h/40d	Inode: 222592      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.480366000 +0000
Modify: 2023-10-12 03:37:19.244060000 +0000
Change: 2026-01-13 11:33:55.495366333 +0000
 Birth: 2026-01-13 11:33:55.480366273 +0000

version: '3'
services:
  traefik:
    container_name: traefik
    image: traefik:2.6
    ports:
      - 80:80
      - 443:443
    #  - 8080:8080 # Dashboard port
    volumes:
      - /opt/appdata/traefik/:/etc/traefik/
    networks:
      - proxy # rename this to your custom docker network
    labels:
      traefik.http.routers.api.rule: Host(`trfk.fatherfankscloud.uk`)    # Define the subdomain for the traefik dashboard.
      traefik.http.routers.api.entryPoints: https    # Set the Traefik entry point.
      traefik.http.routers.api.service: api@internal    # Enable Traefik API.
      traefik.enable: true   # Enable Traefik reverse proxy for the Traefik dashboard.
    environment:
      DOCKER_HOST: dockersocket
      CF_DNS_API_TOKEN: gEFlLaxnUGRKJ_5gaPwmB835h1cIi5KFlv6l7JMF
    restart: unless-stopped
    depends_on:
      - dockersocket

  dockersocket:
    container_name: dockersocket
    image: tecnativa/docker-socket-proxy
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - proxy
    environment:
      CONTAINERS: 1
      POST: 0
    privileged: true
    restart: unless-stopped


networks:
  proxy:
    driver: bridge
    external: true
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/43/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/43/docker-compose.yml
  Size: 554       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 222598      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.536366000 +0000
Modify: 2025-04-23 22:39:19.614258000 +0000
Change: 2026-01-13 11:33:55.549366549 +0000
 Birth: 2026-01-13 11:33:55.536366497 +0000

services:
  code-server:
    image: lscr.io/linuxserver/code-server:latest
    container_name: code-server
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - PASSWORD=<passwordhere> #optional
      - HASHED_PASSWORD= #optional
      - SUDO_PASSWORD=<passwordhere> #optional
      - SUDO_PASSWORD_HASH= #optional
      - PROXY_DOMAIN=coder.fatherfankscloud.uk #optional
      - DEFAULT_WORKSPACE=/config/workspace #optional
    volumes:
      - /hive/code-server/config:/config
    ports:
      - 8050:8443
    restart: unless-stopped
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/44/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/44/docker-compose.yml
  Size: 417       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 222600      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.551366000 +0000
Modify: 2025-04-26 19:40:54.930918000 +0000
Change: 2026-01-13 11:33:55.551366557 +0000
 Birth: 2026-01-13 11:33:55.551366557 +0000

---
version: "2.1"
services:
  flaresolverr:
    # DockerHub mirror flaresolverr/flaresolverr:latest
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - LOG_HTML=${LOG_HTML:-false}
      - CAPTCHA_SOLVER=${CAPTCHA_SOLVER:-none}
      - TZ=Europe/London
    ports:
      - "${PORT:-8191}:8191"
    restart: unless-stopped 

================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/33/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/33/docker-compose.yml
  Size: 832       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 222604      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.572366000 +0000
Modify: 2024-02-11 06:44:55.563097000 +0000
Change: 2026-01-13 11:33:55.585366692 +0000
 Birth: 2026-01-13 11:33:55.572366641 +0000

name: nzbget
services:
  nzbget:
    cpu_shares: 90
    command: []
    container_name: nzbget
    deploy:
      resources:
        limits:
          memory: 25434M
    environment:
      - PGID=1000
      - PUID=1000
      - TZ=Denver
      - UMASK=002
    image: cr.hotio.dev/hotio/nzbget
    restart: unless-stopped
    volumes:
      - type: bind
        source: /hive/NZBget/config
        target: /config
        bind:
          create_host_path: true
      - type: bind
        source: /hive/downloads
        target: /downloads
        bind:
          create_host_path: true
    ports: []
    devices: []
    cap_add: []
    network_mode: container:qbittorrent
    privileged: false
x-casaos:
  author: self
  category: self
  hostname: ""
  icon: ""
  index: /
  port_map: "6789"
  scheme: http
  title:
    custom: NZBGet

================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/39/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/39/docker-compose.yml
  Size: 408       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 222594      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.497366000 +0000
Modify: 2025-01-12 19:58:17.979880000 +0000
Change: 2026-01-13 11:33:55.514366409 +0000
 Birth: 2026-01-13 11:33:55.497366341 +0000

---
services:
  readarr:
    image: lscr.io/linuxserver/readarr:develop
    container_name: readarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    volumes:
      - /hive/readarr:/config
      - /hive/cloud/data/fatherfranku/files/Kavita/Books:/books #optional
      - /hive/downloads/completed/Readarr:/downloads #optional
    ports:
      - 8787:8787
    restart: unless-stopped
================================================================
FILE: /hive/.Trash-1000/files/portainer/compose/37/docker-compose.yml
================================================================
  File: /hive/.Trash-1000/files/portainer/compose/37/docker-compose.yml
  Size: 485       	Blocks: 12         IO Block: 512    regular file
Device: 28h/40d	Inode: 222606      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-01-13 11:33:55.586366000 +0000
Modify: 2024-03-11 21:40:11.153821000 +0000
Change: 2026-01-13 11:33:55.587366701 +0000
 Birth: 2026-01-13 11:33:55.586366697 +0000

version: '3.9'
services:
    kavita:
        image: jvmilazz0/kavita:latest
        container_name: kavita
        volumes:
            - /hive/cloud/data/fatherfranku/files/Kavita/manga:/manga
            - /hive/cloud/data/fatherfranku/files/Kavita/books:/books
            - /hive/cloud/data/fatherfranku/files/Kavita/comics:/comics
            - /hive/cloud/data/fatherfranku/files/Kavita/data:/kavita/config
        ports:
            - "5000:5000"
        restart: unless-stopped
================================================================
FILE: /hive/calibre-web/compose.yml
================================================================
  File: /hive/calibre-web/compose.yml
  Size: 1505      	Blocks: 12         IO Block: 1536   regular file
Device: 28h/40d	Inode: 1575772     Links: 1
Access: (0664/-rw-rw-r--)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-03-02 12:34:20.478145435 +0000
Modify: 2026-03-29 11:53:25.185244549 +0000
Change: 2026-03-29 11:53:25.185244549 +0000
 Birth: 2026-03-02 12:34:20.478145435 +0000

services:

  calibre:
    image: lscr.io/linuxserver/calibre:latest
    container_name: calibre
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Tokyo
      - DISABLE_SSL=true
    volumes:
      - /hive/calibre/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
      - /hive/library/Kavita/browser_cache:/config/browser_cache

    restart: unless-stopped
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.calibre-gui.rule=Host(`calibre.fatherfankscloud.uk`)"
      - "traefik.http.routers.calibre-gui.entrypoints=websecure"
      - "traefik.http.routers.calibre-gui.tls.certresolver=letsencrypt"
      - "traefik.http.services.calibre-gui.loadbalancer.server.port=8080"
    # Not exposed publicly (GUI only accessible locally)

  calibre-web:
    image: lscr.io/linuxserver/calibre-web:latest
    container_name: calibre-web
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Tokyo
    volumes:
      - /hive/calibre-web/config:/config
      - /hive/library/Kavita/fanfic/novelas:/books
    restart: unless-stopped
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.calibre.rule=Host(`calib.fatherfankscloud.uk`)"
      - "traefik.http.routers.calibre.entrypoints=websecure"
      - "traefik.http.routers.calibre.tls.certresolver=letsencrypt"
      - "traefik.http.services.calibre.loadbalancer.server.port=8083"

networks:
  proxy:
    external: true

================================================================
FILE: /hive/NZBget/compose.yml
================================================================
  File: /hive/NZBget/compose.yml
  Size: 1702      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 180515      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: ( 1000/fatherfrank)   Gid: (  113/  syslog)
Access: 2024-09-24 17:02:21.282275788 +0000
Modify: 2024-09-24 17:05:44.374391101 +0000
Change: 2024-09-24 17:05:44.374391101 +0000
 Birth: 2023-07-16 03:45:58.112591031 +0000

#name: nzbget
#services:
 # nzbget:
  #  cpu_shares: 90
   # command: []
    #container_name: nzbget
    #deploy:
     # resources:
      #  limits:
       #   memory: 25434M
#    environment:
#      - PGID=1000
#      - PUID=1000
#      - TZ=Denver
 #     - UMASK=002
 #   image: cr.hotio.dev/hotio/nzbget
 #   restart: unless-stopped
 #   volumes:
 #     - type: bind
 #       source: /hive/NZBget/config
 #       target: /config
 #       bind:
 #         create_host_path: true
 #     - type: bind
 #       source: /hive/downloads
 #       target: /downloads
 #       bind:
 #         create_host_path: true
 #   ports: []
 #   devices: []
 #   cap_add: []
 #   network_mode: container:qbittorrent
 #   privileged: false
#x-casaos:
#  author: self
#  category: self
#  hostname: ""
#  icon: ""
#  index: /
#  port_map: "6789"
#  scheme: http
#  title:
#    custom: NZBGet
name: nzbget
services:
  nzbget:
    cpu_shares: 90
    command: []
    container_name: nzbget
    deploy:
      resources:
        limits:
          memory: 25434M
    environment:
      - PGID=1000
      - PUID=1000
      - TZ=Denver
      - UMASK=002
    image: ghcr.io/hotio/nzbget
    restart: unless-stopped
    volumes:
      - type: bind
        source: /hive/NZBget/config
        target: /config
        bind:
          create_host_path: true
      - type: bind
        source: /hive/downloads
        target: /downloads
        bind:
          create_host_path: true
    ports: []
    devices: []
    cap_add: []
    network_mode: container:qbittorrent
    privileged: false
x-casaos:
  author: self
  category: self
  hostname: ""
  icon: ""
  index: /
  port_map: "6789"
  scheme: http
  title:
    custom: NZBGet

================================================================
FILE: /hive/library/Kavita/compose.yml
================================================================
  File: /hive/library/Kavita/compose.yml
  Size: 993       	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 1599465     Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-03-07 12:23:46.906051711 +0000
Modify: 2026-03-29 04:17:49.032870141 +0000
Change: 2026-03-29 04:17:49.032870141 +0000
 Birth: 2026-03-07 12:23:46.906051711 +0000

services:

  kavita:
    image: jvmilazz0/kavita:latest
    container_name: kavita
    restart: unless-stopped

    environment:
      - TZ=UTC
      - DOTNET_RUNNING_IN_CONTAINER=true

    volumes:
      # SSD (database + config)
      - /ssd/appdata/kavita/config:/kavita/config

      # HDD media
      - /hive/library/Kavita/Books:/books
      - /hive/library/Kavita/Comics:/comics
      - /hive/library/Kavita/Manga:/manga
      - /hive/library/Kavita/fanfic:/fanfic

    networks:
      - proxy

    labels:
      - "traefik.enable=true"

      # router
      - "traefik.http.routers.kavita.rule=Host(`kav.fatherfankscloud.uk`)"
      - "traefik.http.routers.kavita.entrypoints=websecure"
      - "traefik.http.routers.kavita.tls.certresolver=le"

      # service
      - "traefik.http.services.kavita.loadbalancer.server.port=5000"

      # optional middleware (good practice)
     # - "traefik.http.routers.kavita.middlewares=secureHeaders@file"

networks:
  proxy:
    external: true

================================================================
FILE: /hive/cloud/old/Cloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/cloud/old/Cloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 452169      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:45:21.206851587 +0000
Modify: 2024-03-11 20:03:11.268752416 +0000
Change: 2024-03-11 20:03:11.268752416 +0000
 Birth: 2024-03-11 20:03:11.268752416 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/cloud/old/Cloud/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/cloud/old/Cloud/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 484623      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:26.385156967 +0000
Modify: 2024-03-11 20:04:28.957112498 +0000
Change: 2024-03-11 20:04:28.957112498 +0000
 Birth: 2024-03-11 20:04:28.957112498 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/cloud/old/nextcloud/apps/mail/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/cloud/old/nextcloud/apps/mail/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 494292      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:31.703182040 +0000
Modify: 2024-03-11 20:04:38.489156767 +0000
Change: 2024-03-11 20:04:38.489156767 +0000
 Birth: 2024-03-11 20:04:38.489156767 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/cloud/old/nextcloud/nextcloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/cloud/old/nextcloud/nextcloud/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 544430      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:47:01.215321581 +0000
Modify: 2024-03-11 20:05:14.481324081 +0000
Change: 2024-03-11 20:05:14.481324081 +0000
 Birth: 2024-03-11 20:05:14.477324062 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/cloud/old/nextcloud/compose/compose.yml
================================================================
  File: /hive/cloud/old/nextcloud/compose/compose.yml
  Size: 1022      	Blocks: 12         IO Block: 1024   regular file
Device: 28h/40d	Inode: 497174      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:36.214203326 +0000
Modify: 2024-03-11 20:04:41.921172711 +0000
Change: 2024-03-11 20:04:41.921172711 +0000
 Birth: 2024-03-11 20:04:41.917172692 +0000

version: "3.9"
services: 
  app: 
    depends_on: 
      - db
    environment: 
      - MYSQL_PASSWORD= <passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    image: nextcloud
    links: 
      - db
    ports: 
      - "8888:80"
      - "8443:443"
    restart: always
    volumes: 
      - "/your-pool/Cloud/nextcloud/nextcloud:/var/www/html"
      - "/your-pool/Cloud/nextcloud/apps:/var/www/html/custom_apps"
      - "/your-pool/Cloud/nextcloud/config:/var/www/html/config"
      - "/your-pool/Cloud/nextcloud/data:/var/www/html/data"
      - "/your-pool/Cloud/nextcloud/theme:/var/www/html/themes/<YOUR_CUSTOM_THEME>"
  db: 
    command: "--transaction-isolation=READ-COMMITTED --binlog-format=ROW"
    environment: 
      - MYSQL_ROOT_PASSWORD= <passwordhere>
      - MYSQL_PASSWORD= <passwordhere>
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    image: "mariadb:10.5"
    restart: always
    volumes: 
      - "/your-pool/Cloud/nextcloud/db:/var/lib/mysql"

================================================================
FILE: /hive/cloud/old/nextcloud/compose/nextcloud-data/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
================================================================
  File: /hive/cloud/old/nextcloud/compose/nextcloud-data/apps/suspicious_login/vendor/league/flysystem/docker-compose.yml
  Size: 1562      	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 516612      Links: 1
Access: (0777/-rwxrwxrwx)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-01-29 13:46:44.299241515 +0000
Modify: 2024-03-11 20:04:53.021224290 +0000
Change: 2024-03-11 20:04:53.021224290 +0000
 Birth: 2024-03-11 20:04:53.021224290 +0000

---
version: "3"
services:
  webdav:
    image: bytemark/webdav
    restart: always
    ports:
      - "80:80"
    environment:
      AUTH_TYPE: Digest
      USERNAME: alice
      PASSWORD: <passwordhere>
  sftp:
    container_name: sftp
    restart: always
    image: atmoz/sftp
    volumes:
      - ./test_files/sftp/users.conf:/etc/sftp/users.conf
      - ./test_files/sftp/ssh_host_ed25519_key:/etc/ssh/ssh_host_ed25519_key
      - ./test_files/sftp/ssh_host_rsa_key:/etc/ssh/ssh_host_rsa_key
      - ./test_files/sftp/id_rsa.pub:/home/bar/.ssh/keys/id_rsa.pub
    ports:
      - "2222:22"
  ftp:
    container_name: ftp
    restart: always
    image: delfer/alpine-ftp-server
    environment:
      USERS: 'foo|pass|/home/foo/upload'
      ADDRESS: 'localhost'
    ports:
      - "2121:21"
      - "21000-21010:21000-21010"
  ftpd:
    container_name: ftpd
    restart: always
    environment:
      PUBLICHOST: localhost
      FTP_USER_NAME: foo
      FTP_USER_PASS: pass
      FTP_USER_HOME: /home/foo
    image: stilliard/pure-ftpd
    ports:
      - "2122:21"
      - "30000-30009:30000-30009"
    command: "/run.sh -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -P localhost"
  toxiproxy:
    container_name: toxiproxy
    restart: unless-stopped
    image: ghcr.io/shopify/toxiproxy
    command: "-host 0.0.0.0 -config /opt/toxiproxy/config.json"
    volumes:
      - ./test_files/toxiproxy/toxiproxy.json:/opt/toxiproxy/config.json:ro
    ports:
      - "8474:8474" # HTTP API
      - "8222:8222" # SFTP
      - "8121:8121" # FTP
      - "8122:8122" # FTPD

================================================================
FILE: /hive/jellyfin/compose.yml
================================================================
  File: /hive/jellyfin/compose.yml
  Size: 1113      	Blocks: 12         IO Block: 1536   regular file
Device: 28h/40d	Inode: 722998      Links: 1
Access: (0664/-rw-rw-r--)  Uid: ( 1000/fatherfrank)   Gid: ( 1000/fatherfrank)
Access: 2026-02-05 11:24:22.319749820 +0000
Modify: 2026-04-02 02:19:13.849599613 +0000
Change: 2026-04-02 02:19:13.849599613 +0000
 Birth: 2026-02-04 08:55:46.984785968 +0000

services:
  jellyfin:
    image: ghcr.io/hotio/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096"
    devices:
      - /dev/dri:/dev/dri
    env_file:
      - .env
    environment:
      PUID: "1000"
      PGID: "1000"
      TZ: Etc/UTC
      UMASK: "002"
      NVIDIA_DRIVER_CAPABILITIES: all
      NVIDIA_VISIBLE_DEVICES: all

    volumes:
      - /hive/jellyfin/config:/config
      - /hive/jellyfin/tv:/data/tvshows
      - /hive/jellyfin/movie:/data/movies

    networks:
      - proxy

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.jellyfin.rule=Host(`jellyfin.fatherfankscloud.uk`)"
      - "traefik.http.routers.jellyfin.entrypoints=websecure"

      - "traefik.http.routers.jellyfin.tls=true"
      - "traefik.http.routers.jellyfin.tls.certresolver=le"
     # - "traefik.http.routers.jellyfin.tls.domains[0].main=${DEFAULT_DOMAIN}"
     # - "traefik.http.routers.jellyfin.tls.domains[0].sans=*.${DEFAULT_DOMAIN}"

      - "traefik.http.services.jellyfin.loadbalancer.server.port=8096"

networks:
  proxy:
    external: true


================================================================
FILE: /hive/code-server/compose.yml
================================================================
  File: /hive/code-server/compose.yml
  Size: 919       	Blocks: 12         IO Block: 2048   regular file
Device: 28h/40d	Inode: 589868      Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-02-02 13:22:41.786593211 +0000
Modify: 2026-02-02 13:22:37.430575720 +0000
Change: 2026-02-02 13:22:37.430575720 +0000
 Birth: 2026-02-02 09:32:17.835858621 +0000

services:
  code-server:
    image: lscr.io/linuxserver/code-server:latest
    container_name: code-server
    restart: unless-stopped

    environment:
      PUID: 1000
      PGID: 1000
      TZ: Etc/UTC
      PASSWORD: <passwordhere>
      DEFAULT_WORKSPACE: /config/workspace
      CS_TRUSTED_ORIGINS: "https://code.fatherfankscloud.uk"

    volumes:
      - /hive/code-server/config:/config

    networks:
      - proxy

    labels:
      - "traefik.enable=true"

      # Router
      - "traefik.http.routers.code.rule=Host(`code.fatherfankscloud.uk`)"
      - "traefik.http.routers.code.entrypoints=websecure"
      - "traefik.http.routers.code.tls=true"
      - "traefik.http.routers.code.tls.certresolver=letsencrypt"

      # Service
      - "traefik.http.services.code.loadbalancer.server.port=8443"
      - "traefik.http.services.code.loadbalancer.server.scheme=http"

networks:
  proxy:
    external: true

======================================================================
AUDIT COMPLETE
======================================================================
./compose_audit.sh: line 100: 3: Bad file descriptor
