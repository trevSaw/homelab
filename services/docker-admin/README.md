---
title: docker-admin Service README
document_type: README
service: docker-admin
owner: Homelab
status: Active
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - Documentation/Phase3/KORA_Controlled_Administration.md
  - services/hermes/README.md
---

# docker-admin (KORA controlled administration boundary)

`docker-admin` is the **narrow, token-authenticated administration helper** that
lets KORA/Hermes inspect and (in a limited way) manage the homelab without
Hermes ever receiving the Docker socket.

```text
KORA (policy/orchestration)
   ↓ Hermes plugin tools (kora.docker_*)
Hermes (execution harness, uid 10000, NO docker.sock)
   ↓ HTTP + bearer token over internal `kora-admin` network
docker-admin (whitelist HTTP API, uid 1000, has docker.sock)
   ↓ fixed `docker` / `docker compose` argv
Docker daemon
```

## Why this exists

Phase 1 required *truthful* live-state reasoning; Phase 2 added narrow read-only
qBittorrent inspection. Phase 3 adds controlled homelab administration. The
Docker socket is effectively host-level privilege, so it is **not** given to
Hermes. Instead a single dedicated helper owns the socket and exposes only the
operations KORA actually needs, each built from validated arguments.

The helper is **not a generic Docker proxy**. There is no "run arbitrary docker
command" or "call arbitrary Docker API path" endpoint.

## Exposed operations

All endpoints require `Authorization: Bearer $DOCKER_ADMIN_TOKEN` except
`/healthz`.

| Method | Path | Purpose | Type |
| --- | --- | --- | --- |
| GET | `/healthz` | Liveness/version | read |
| GET | `/containers` | List containers (state/health/image/networks/ports) | read |
| GET | `/containers/<name>` | Inspect one container (state, health, networks, mounts, restart policy, env **keys only**) | read |
| GET | `/containers/<name>/logs?tail=N` | Recent logs | read |
| GET | `/images/<ref>` | Image info (tags/id/size/created/digests); accepts a container name | read |
| GET | `/networks` · `/networks/<name>` | Network list / inspect | read |
| GET | `/volumes` · `/volumes/<name>` | Volume list / inspect | read |
| POST | `/containers/<name>/restart` | Restart one container, then verify | **write** |
| POST | `/compose/validate` | `docker compose config --quiet` for one project | read |
| POST | `/compose/up` | `docker compose up -d --no-build` for one project (recreate/deploy), then report | **write** |

**Never exposed:** delete/remove (containers, images, volumes, networks), prune,
exec, attach, kill, build, pull, push, arbitrary `docker <anything>`, arbitrary
Docker API paths, raw `docker compose config` output (would resolve secrets).

**Control-plane protection:** the helper refuses to restart `hermes` or
`docker-admin`, and refuses to `compose up` `hermes`, `docker-admin` or the
deprecated `taskbridge`. Write endpoints require `{"confirm": true}`.

## Security posture

| Item | Value |
| --- | --- |
| Docker socket | Mounted here only (on the KORA admin path). Unrelated host services (portainer/traefik/beszel-agent/authentik-worker) already mount it for their own purposes; Phase 3 changes none of them. |
| Docker TCP | Never enabled (`/etc/docker/daemon.json` has no TCP; no 2375/2376 listener). |
| Published ports | None (`8765` is exposed only on the internal `kora-admin` network). |
| Hermes socket | Absent (`/var/run/docker.sock` does not exist in Hermes). |
| Container user | `1000:1000` (host repo owner, so read-only `/repo` `0600` `.env` files are readable for Compose substitution) + supplementary group `999` (host `docker` group) for socket access. Not root. |
| Hardening | `read_only` rootfs, `cap_drop: [ALL]`, `no-new-privileges`, tmpfs `/tmp`. |
| Repo mount | `/home/fatherfrank/projects/homelab` → `/repo:ro` (Compose validation/deploy needs `.env` substitution; the API never returns file contents). |
| Secret handling | The bearer token is generated once and stored in the gitignored `.env` here and in the Hermes volume file `/opt/data/docker-admin.token`. It is never logged, printed, or returned by any endpoint. Container env **values** are never returned (keys only). |

## Operate

```sh
cd services/docker-admin
printf 'DOCKER_ADMIN_TOKEN=%s\nTZ=Asia/Tokyo\n' "$(openssl rand -hex 32)" > .env
docker compose up -d --build
docker compose logs -f
```

Generate the shared token once, put the same value in
`services/docker-admin/.env` and write it to the Hermes volume file:

```sh
docker exec hermes sh -c 'umask 077; cat > /opt/data/docker-admin.token' <<<"$TOKEN"
```

Hermes joins the internal `kora-admin` network (see
`services/hermes/compose.yaml`). Bring `docker-admin` up before (re)creating
Hermes so the network exists.

### Deploy path constraint (bind mounts)

`/compose/up` runs `docker compose --project-directory /repo/services/<project>`,
where `/repo` is the canonical repo mounted **inside this helper**. The Docker
**daemon** resolves compose bind-mount sources on the **host**, not inside the
helper. Therefore compose files deployed through `docker-admin` **must use
absolute host bind paths** (e.g. `/mnt/monarch/appdata/...`,
`/home/fatherfrank/projects/homelab/...`). A relative source such as `./config`
is resolved to `/repo/services/<project>/config`, which does not exist on the
host — Docker silently creates a stray host `/repo/...` **directory**, and the
mount is empty/wrong. Verify with `docker inspect <container>` and remove any
stray host `/repo` tree. See `services/searxng/compose.yaml` for the pattern.

## Validation

Unit tests (no Docker, no writes):

```sh
python3 -m pytest services/docker-admin/tests -q
```

Live read check (runs inside Hermes, exercising the plugin path):

```sh
docker exec hermes /opt/hermes/.venv/bin/python3 -c \
  'import sys,json; sys.path.insert(0,"/opt/data/plugins"); import kora;
   print(json.loads(kora.handler_docker_list({}))["count"])'
```

The full Phase 3 validation transcript (read, write, and failure semantics) is
in `Documentation/Phase3/KORA_Controlled_Administration.md`.

## Deferred

Container/volume/network/image deletion, `docker system prune`, arbitrary exec
or shell, and Docker TCP/public exposure are intentionally **not** implemented.
Discord integration is deferred to Phase 4.
