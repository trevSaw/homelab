# SearXNG Validation — Phase 5

**Date:** 2026-10-06
**Service:** `services/searxng/` (container `searxng`)
**ADR:** `Architecture/decisions/ADR-0014-SearXNG-Internal-Research-Service.md`
**Deploy path:** Phase 3 `docker-admin` workflow (`kora` `docker_compose_validate` /
`docker_compose_up`, project `searxng`)
**Result:** **PASS** (healthy, internal-only, reachable from Hermes)

## 1. Scope

Validate that the new internal-only SearXNG deployment is healthy, is not
publicly exposed, and is reachable from its intended internal consumer
(Hermes/KORA). No KORA research/tool configuration was changed.

## 2. Method

1. Prepared canonical files under `services/searxng/`; `docker compose config -q`.
2. `POST /compose/validate {"project":"searxng"}` → `valid=true`.
3. `POST /compose/up {"project":"searxng","confirm":true}` → `ok=true, exit=0`.
4. Post-deploy inspection + functional probes.

## 3. Evidence

| Check | Result |
| --- | --- |
| `docker compose config -q` | OK |
| `docker-admin` compose validate | `valid=true` (`services/searxng/compose.yaml`) |
| `docker-admin` compose up | `ok=true`, `exit_code=0` |
| Container state / health | `running` / `healthy` |
| `GET /healthz` (in-container) | `OK` |
| JSON search (`!bing searxng`, `format=json`) | 10 results returned |
| Reachability from Hermes (`uid 10000`) | `healthz: OK`; JSON `search` returned valid JSON |
| Published ports | none (`{"8080/tcp": null}`) |
| Network membership | `ollama_ollama-net` only (not `proxy`) |
| Traefik label | `traefik.enable=false` |
| Volume mounts | `config/ → /etc/searxng:ro` (abs host path); `/mnt/monarch/appdata/searxng → /var/cache/searxng` |
| Anonymous volumes | none |
| Secret in Compose/repo | none (`SEARXNG_SECRET` in gitignored `.env`, mode 0600) |
| Capabilities | `cap_drop: [ALL]` + `CHOWN,SETGID,SETUID,DAC_OVERRIDE`; `no-new-privileges` |
| Resource limits | 0.50 CPU / 512 MiB |

Sample identity:
`id=1157bb87b487…`, image `searxng/searxng:2026.5.31-7159b8aed`,
created `2026-10-06T09:49:10Z`.

## 4. Findings / remediation during deploy

Two issues were found and fixed before the passing result above.

### F1 — File-bind into an image-declared `VOLUME` (fixed)

The image declares `VOLUME /etc/searxng`. Binding the single file
`.../config/settings.yml` to `/etc/searxng/settings.yml` caused the target to
materialise as a **directory** inside the anonymous volume, and the entrypoint
crash-looped (`settings.yml is not a valid file`). It also created a
non-compliant **anonymous Docker volume**.
**Fix:** bind-mount the whole committed config directory
(`.../services/searxng/config → /etc/searxng:ro`).

### F2 — Relative bind sources break under `docker-admin` (fixed)

`docker-admin` runs `docker compose --project-directory /repo/services/<project>`
and the Docker **daemon** resolves bind sources on the **host**. A relative
`./config` source was resolved to `/repo/services/searxng/config`, which does not
exist on the host, so Docker created a stray host `/repo/.../settings.yml`
directory. 
**Fix:** use absolute host paths for all bind sources
(`/home/fatherfrank/projects/homelab/services/searxng/config`,
`/mnt/monarch/appdata/searxng`). Stray host `/repo` tree removed. Constraint
documented in `services/docker-admin/README.md` → *Deploy path constraint*.

## 5. Notes / limitations

- Several public engines return rate-limit/CAPTCHA (host IP shared with the
  pre-existing Odysseus-local SearXNG); Bing and Wikipedia work. This is
  engine-side/environmental, not a deployment defect.
- A second SearXNG remains in the Odysseus stack (unchanged). Consolidation
  (repoint Odysseus `SEARXNG_INSTANCE` to this service) is deferred.

## 6. Follow-ups (not done)

- KORA integration: a read-only `kora.web_search` plugin tool over the internal
  network (separate approval; no MCP/`platform_toolsets` change).
- Optional: consolidate the Odysseus-local SearXNG onto this instance.
