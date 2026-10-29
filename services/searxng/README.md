---
title: SearXNG Service README
document_type: README
service: searxng
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0014-SearXNG-Internal-Research-Service.md
  - Architecture/standards/DockerStandard.md
  - services/hermes/README.md
  - services/docker-admin/README.md
  - Documentation/Phase3/KORA_Controlled_Administration.md
---

# SearXNG (internal KORA/Hermes research service)

SearXNG is a self-hosted **metasearch** engine. This deployment is
**internal-only** and exists to give KORA/Hermes a private web-search backend
with no API keys and no third-party search dependency. It is **not** publicly
exposed and is **not** reachable from the LAN/WAN/Tailscale.

## Overview

| Item | Value |
| --- | --- |
| Purpose | Private metasearch backend for KORA/Hermes research |
| Lifecycle stage | Production (Phase 5, validated 2026-10-06) |
| Importance | Standard |
| Owner | Homelab |
| Image | `searxng/searxng:2026.5.31-7159b8aed` (pinned) |
| Container | `searxng` |
| Internal URL | `http://searxng:8080/` (Docker DNS, internal AI network) |
| Public exposure | **None** (no published ports, no Traefik route) |

```text
KORA (policy/orchestration)
   ↓ native Hermes `web` toolset (web_search → bundled searxng provider)
Hermes (uid 10000, no docker.sock)
   ↓ HTTP over internal `ollama_ollama-net`
searxng (127.0.0.1:8080 inside the container; JSON API enabled)
   ↓ outbound HTTPS
GitHub API (reliable) + best-effort general engines
```

## Required external resources

- **Network:** `ollama_ollama-net` (external, pre-existing AI service fabric).
  Hermes is already attached; no new network is created.
- **Volume:** none (all persistence is a bind mount — see §Storage).
- **Devices:** none.

## Deploy

Canonical deploy is through the Phase 3 `docker-admin` workflow (KORA policy
tool `kora.docker_compose_up`, project = `searxng`). The helper runs
`docker compose --project-directory services/searxng up -d --no-build` against
the canonical repository.

Prepare the host data directory (once, before first deploy):

```sh
mkdir -p /mnt/monarch/appdata/searxng
```

Manual equivalent (only for local verification; the canonical path is
`docker-admin`):

```sh
cd services/searxng
cp .env.example .env     # then set SEARXNG_SECRET: openssl rand -hex 32
docker compose config -q
docker compose up -d
```

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `SEARXNG_SECRET` | yes | Instance secret. Injected from the gitignored `.env`; overrides `server.secret_key`. **Never** committed. |
| `SEARXNG_BASE_URL` | no | Internal base URL (default `http://searxng:8080/`). |
| `TZ` | no | Log timezone (default `Asia/Tokyo`). |

Committed settings: `config/settings.yml` (mounted read-only at
`/etc/searxng/settings.yml`). It enables the **JSON** output format (required
for programmatic use) alongside HTML, disables the public-instance limiter, and
carries only the `ultrasecretkey` placeholder for the secret.

## Storage

| Host path | Container | Class | Notes |
| --- | --- | --- | --- |
| `/mnt/monarch/appdata/searxng` | `/var/cache/searxng` | SSD / app state | Engine ban state, favicon cache |
| `/home/fatherfrank/projects/homelab/services/searxng/config` | `/etc/searxng:ro` | config (git) | Committed, secret-free; **absolute path** (docker-admin deploy requirement), dir mount because the image declares `VOLUME /etc/searxng` |

No named/anonymous Docker volumes are used.

## Networking

- Attached only to **`ollama_ollama-net`** (external, existing AI fabric,
  `internal=false` so SearXNG can reach the public internet to run searches).
- **No** `ports:` mapping and `traefik.enable=false` — it cannot be reached from
  outside the Docker host, and no DNS/proxy record is created for it.
- Reuses an existing network, so no Architecture Standard network amendment is
  required.

## Security

- No published ports, no Traefik route, no host filesystem mount, no Docker
  socket.
- `cap_drop: [ALL]` with only `CHOWN`, `SETGID`, `SETUID`, `DAC_OVERRIDE`
  restored (required by the image entrypoint — see Exceptions).
- `security_opt: [no-new-privileges:true]`.
- Secrets only in the gitignored `.env`; `config/settings.yml` is secret-free.
- Outbound internet access is required for search; no inbound exposure.

## KORA integration (Phase 5 — complete)

KORA/Hermes consume SearXNG via Hermes' **native `web` toolset**, using the
bundled Hermes SearXNG provider (`plugins/web/searxng`) selected by
`SEARXNG_URL=http://searxng:8080` and `web.search_backend: searxng`. There is no
custom bridge and no bespoke `kora.*` tool. The `web` toolset is enabled for
both `api_server` (Open WebUI) and `discord`. See ADR-0015 and
`Validation/Phase5/KORA_Web_Research_Validation.md`.

### Engine selection

This host's public-IP egress is blocked / handed anti-bot junk by most general
engines, so `config/settings.yml` enables the **`github` engine** (official
GitHub API, no key) and re-categorises it into `general` as the dependable
software-discovery path, keeps `bing` best-effort, and disables the blocked
engines (google, duckduckgo, brave, startpage, mojeek, yahoo, qwant, presearch).
`web_extract` is intentionally unavailable (SearXNG is search-only); pages and
repos are fetched with `terminal`/delegation.

## Validation

1. `docker compose config -q` (or `kora.docker_compose_validate("searxng")`).
2. Container `running` and `healthy`.
3. `GET http://searxng:8080/healthz` returns `OK` from inside the AI network.
4. JSON search works: `GET http://searxng:8080/search?q=test&format=json`
   returns `results`/`number_of_results`.
5. Not reachable externally: no host port listener, no Traefik router.

Results (2026-10-06): `docker compose config -q` OK; deployed via
`docker-admin` (`ok=true`, exit 0); `running`/`healthy`; `/healthz` → `OK`;
JSON `search` returns results (`!bing` → 10); reachable from Hermes
(`http://searxng:8080`); no published ports; not on `proxy`. Engine-side
rate-limiting/CAPTCHA is environmental. Full report:
`Validation/Phase5/SearXNG_Validation.md`.

## Backup & restore

State is disposable cache. Backup (if desired):
`tar -C /mnt/monarch/appdata -czf searxng-$(date +%F).tgz searxng`.
Restore by extracting back while the container is stopped. The only critical
non-cache value is `SEARXNG_SECRET` in the gitignored `.env` (keep it in the
homelab secret store/backup).

## Upgrade

Bump the pinned tag in `compose.yaml` and `Versions.md`, then redeploy via
`docker-admin`. Do **not** move to `2026.6.2` (known boot failure,
`KeyError: 'default_doi_resolver'`). Verify `healthy` after any bump.

## Troubleshooting

- **Unhealthy / crash loop:** check `docker logs searxng`; a `KeyError:
  'default_doi_resolver'` means an untested tag was used — revert the tag.
- **Empty secret warning:** `SEARXNG_SECRET` missing from `.env`.
- **Search returns no results:** SearXNG requires outbound internet; confirm the
  container is not attached to an `internal: true` network and that host egress
  works. Some engines are often rate-limited/CAPTCHA'd; that is engine-side.
- **JSON 403/format denied:** `config/settings.yml` must list `json` under
  `search.formats`.

## Exceptions

| Field | Value |
| --- | --- |
| **Reason** | The official `searxng/searxng` image runs as its own (root) entrypoint user and uses the entrypoint to set ownership of the bind-mounted data dir and refresh the CA store before exec'ing the server. |
| **Risk** | The server process runs as the image default user rather than a non-root user; a vulnerability in result parsing could run with that user's rights inside the container. |
| **Mitigation** | `cap_drop: [ALL]` plus only the four caps the entrypoint needs; `no-new-privileges`; no socket; no host mount; no published ports; reachable only on the internal AI network. |
| **Rollback** | `docker-admin` does not expose deletion; stop/remove via host admin and remove `services/searxng/` + `/mnt/monarch/appdata/searxng`. |
| **Human Approval** | Approved — Homelab owner (2026-10-06). |

## Related

- ADR: `Architecture/decisions/ADR-0014-SearXNG-Internal-Research-Service.md`
- Pre-existing Odysseus-local SearXNG (separate, unchanged):
  `services/odysseus/docker-compose.yml` (bound `127.0.0.1:8585`). This
  deployment is intentionally decoupled from Odysseus.
