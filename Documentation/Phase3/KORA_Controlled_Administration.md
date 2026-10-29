---
title: KORA Controlled Homelab Administration (Phase 3)
document_type: Implementation Report
service: hermes
owner: Homelab
status: Implemented
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - services/docker-admin/README.md
  - services/hermes/README.md
  - Documentation/Phase18/KORA_Controlled_Development_and_Validation.md
---

# KORA Controlled Homelab Administration (Phase 3)

**Status:** Implemented and validated (2026-10-06).

**Objective:** give KORA/Hermes the ability to perform *controlled* homelab
administration — inspect live container state, and perform a deliberately narrow
set of lifecycle operations — **without** giving Hermes the Docker socket and
without weakening KORA governance.

Discord is **not** part of this phase.

## 1. Audit summary (read-only)

| Question | Finding |
| --- | --- |
| Hermes runtime | `nousresearch/hermes-agent` v0.21.4, container `hermes`, agent runs as **uid 10000 (`hermes`)**. |
| Docker socket in Hermes | **Absent.** |
| Hermes mounts | `/opt/data` (rw, Hermes volume), `Architecture/ai/Council`, `Documentation`, `Architecture/standards`, `/home/fatherfrank/projects/docker-state` (all ro). No host root, no canonical repo. |
| Hermes networks | `proxy`, `ollama_ollama-net` (now also internal `kora-admin`). |
| Docker CLI in Hermes | Present at `/usr/bin/docker` but **no socket / no daemon reachable**. |
| Live Docker state | `scripts/docker-state-snapshot.sh` writes `ps/inspect/networks.txt`; snapshot was **stale (2026-08-15)** — not live. |
| Canonical repo access | Not mounted into Hermes (Phase 18.1 `.env` remediation). KORA edits the sanitized workspace clone; canonical apply is approval-gated via `scripts/kora-apply.sh`. |
| Existing deploy mechanism | None automated. `scripts/kora-apply.sh` is a human-run patch gate; no `docker compose up` automation. |
| Docker TCP | Not enabled; no public exposure. |
| Other socket holders | portainer, traefik, beszel-agent, authentik-worker (pre-existing, unchanged). |
| Task Bridge | Deprecated (Phase 22), container owns no socket; not extended. |

**Conclusion:** live Docker inspection and lifecycle control require *some*
component with daemon access. A host-side daemon was rejected (no passwordless
root/systemd available; less reproducible). The narrowest *repo-managed* option
is a single dedicated helper container that owns the socket and exposes a
whitelist HTTP API — **not** a generic proxy, and **not** the socket in Hermes.

## 2. Architecture

```text
KORA (policy / orchestration / intent)
   ↓ kora.docker_* plugin tools (Hermes tool runtime)
Hermes (execution harness, uid 10000, NO docker.sock)
   ↓ HTTP + bearer token, internal `kora-admin` network only
docker-admin (whitelist API, uid 1000, has docker.sock)
   ↓ fixed, validated `docker` / `docker compose` argv
Docker daemon (infrastructure target)
```

KORA remains the policy layer: every Docker capability is registered as a KORA
plugin tool, passes through `pre_tool_call` governance, and is described to the
model by the Phase 3 directive. Hermes executes; Docker is the target.

## 3. Capability matrix

| Capability | Required? | Read/Write | Mechanism | Risk |
| --- | --- | --- | --- | --- |
| Container status/list | yes | read | `kora.docker_list` → `GET /containers` | low |
| Container inspect | yes | read | `kora.docker_inspect` → `GET /containers/<name>` | low (env values redacted) |
| Container logs | yes | read | `kora.docker_logs` → `GET /containers/<name>/logs` | low (logs may contain app data) |
| Health status | yes | read | `kora.docker_health` → inspect projection | low |
| Image information | yes | read | `kora.docker_image` → `GET /images/<ref>` | low |
| Network inspection | yes | read | `kora.docker_networks` | low |
| Volume inspection | yes | read | `kora.docker_volumes` | low (paths only) |
| Restart container | yes | write | `kora.docker_restart` → `POST /containers/<name>/restart` | medium (disruptive; confirm + verify; control-plane denied) |
| Recreate service | yes | write | `kora.docker_compose_up` → `POST /compose/up` | medium (canonical config only; confirm + control-plane denied) |
| Compose validation | yes | read | `kora.docker_compose_validate` → `POST /compose/validate` | low |
| Compose editing | yes (repo workflow) | write | workspace clone + approval-gated `scripts/kora-apply.sh` | gated by human approval |
| Deploy Compose service | yes | write | `kora.docker_compose_up` (confirm) | medium |
| Remove container | **no** | — | not exposed | — |
| Remove volume | **no** | — | not exposed | — |
| Remove network | **no** | — | not exposed | — |
| Docker system prune | **no** | — | not exposed | — |
| `docker exec` / arbitrary command | **no** | — | not exposed | — |
| Arbitrary Docker API path | **no** | — | not exposed | — |

## 4. Docker socket decision

The socket **is required** for live inspection of image/volume/network/container
state and for lifecycle operations; there is no narrower way to obtain them.
It was **not** given to Hermes. It is mounted only into `docker-admin`, which:

* exposes a fixed whitelist (no generic proxy, no arbitrary API path),
* redacts env values and secret-looking labels,
* requires bearer auth on every endpoint except `/healthz`,
* requires `confirm: true` for writes,
* refuses control-plane targets (`hermes`, `docker-admin`; plus `taskbridge`
  for deploy),
* runs unprivileged with a read-only rootfs, all capabilities dropped, and
  `no-new-privileges`,
* is reachable only on the internal `kora-admin` network (no published ports,
  no Traefik route, no Docker TCP).

The model never receives `docker <anything>`; it receives named KORA tools.

## 5. Operational workflow (repository → deploy → verify)

```text
inspect live state / canonical config
   ↓
edit the sanitized workspace clone (or canonical repo as a human)
   ↓
kora.docker_compose_validate(project)          # structural validation
   ↓
git diff → scripts/kora-apply.sh (human approval)   # canonical apply
   ↓
kora.docker_compose_up(project, confirm=true)  # recreate/deploy canonical config
   ↓
kora.docker_list / kora.docker_health          # verify resulting state
```

The canonical repository is the configuration source of truth; running Docker
state is evidence only. Deploy always uses the canonical compose files (the
helper mounts the repo read-only), so no running-state drift can be deployed.

## 6. Failure semantics (Phase 1 preserved)

`Tool failure ≠ system absence`. The helper returns structured errors and never
turns an inspection failure into a negative fact:

* `inspect-failed` / `logs-unavailable` / `admin-unreachable` →
  "cannot determine", never "container is absent".
* `restart` result includes `state_before` and a polled `state_after`; KORA is
  directed to report exactly what was observed.
* `compose validate` failure is an error, never a deployment.
* denied/blocked operations are reported as refusals, not retried indirectly.

## 7. Validation transcript (2026-10-06)

**Unit tests** (`python3 -m pytest services/docker-admin/tests -q`): 6 passed
(token required at startup, name validation, path-traversal guard, label
redaction, env-value redaction, control-plane protection).

**Read tests** (plugin path inside Hermes):

| Test | Result |
| --- | --- |
| `kora.docker_list` | 55 containers |
| `kora.docker_health("sonarr")` | `running` / `healthy` |
| `kora.docker_inspect("radarr")` | state `running`, health `healthy`, env **keys only** |
| `kora.docker_logs("sonarr", tail=3)` | 3 lines |
| `kora.docker_image("jellyfin")` | `ghcr.io/hotio/jellyfin:release-12.1` |
| `kora.docker_networks` / `kora.docker_volumes` | 29 networks / 13 volumes |
| `kora.docker_compose_validate("sonarr")` | `valid=true`, `services/sonarr/compose.yml` |
| `kora.docker_compose_validate("homepage")` / `("hermes")` | `valid=true` |

**End-to-end model test** (Open WebUI path: Open WebUI → Hermes api_server →
KORA → `gpt-oss:20b-cloud`): asked KORA for Sonarr's health; KORA emitted a real
tool call and answered *"The Sonarr container is healthy."* (digest:
`classification=operational, services_used=[tools]`).

**Write test** (safe non-critical service `homepage`, dashboard):
restart via `kora.docker_restart("homepage", confirm=true)`. Evidence:
`started_at` changed `2026-09-26T09:26:45Z → 2026-10-06T07:44:45Z`, health
returned `healthy`, and homepage answered `HTTP 200` from the `proxy` network.
A second restart requested through the live model succeeded
(`started_at → 2026-10-06T07:45:46Z`). Unrelated containers (sonarr, radarr,
jellyfin, qbittorrent) were untouched (`started_at` unchanged).

**Compose deploy test** (`kora.docker_compose_up`): `up -d --no-build` on the
`homepage` project reconciled it successfully (`ok=true, exit=0`, container
`running/healthy`, `started_at` unchanged — config already current). An invalid
service within a valid project returned `ok=false, exit=1` with
`no such service` and made no change. `compose up` of `hermes`/`docker-admin`
is refused (`deploy-target-denied`).

**Failure validation:**

| Case | Result |
| --- | --- |
| inspect missing container | `error/inspect-failed` (not "does not exist") |
| logs missing container | `error/logs-unavailable` |
| invalid name `../etc/passwd` | `error/invalid-or-missing-name` |
| restart without `confirm` | `error/confirmation-required` **and** blocked by `pre_tool_call` |
| restart `hermes` / `docker-admin` | `error/restart-target-denied` |
| `compose up` `hermes` | `error/deploy-target-denied` |
| validate missing project | `error/project-not-found` |
| project path traversal `../` | `error/invalid-or-missing-project` |
| admin helper down | `error/admin-unreachable` |

No destructive tests were performed; nothing was deleted, pruned, or removed.

## 8. Security boundary (explicit)

* **Docker socket:** present in `docker-admin` only (Hermes/KORA: absent).
* **Docker TCP:** absent; no public exposure.
* **Host root filesystem:** not mounted anywhere in this phase.
* **Hermes UID:** 10000 (`hermes`).
* **docker-admin UID:** 1000 (host repo owner; not root; socket via
  supplementary group 999). It needs the repo `.env` files (mode 0600) for
  Compose substitution, which is why it runs as the repo owner.
* **Exposed networks:** `docker-admin` on internal `kora-admin` only; Hermes on
  `proxy`, `ollama_ollama-net`, `kora-admin`.
* **Secret handling:** token only in gitignored `.env` + Hermes volume file; env
  values and secret-looking labels never returned; `docker compose config` full
  output never returned.
* **Arbitrary command/API access:** none.
* **Destructive operations:** none exposed.

## 9. Deferred

* Container/volume/network/image deletion, `prune`, `exec`, build/pull/push.
* Docker TCP / public API exposure.
* Automatic deployment without human confirmation.
* Traefik/DNS/Cloudflare write capabilities (out of scope).
* **Discord integration is deferred to Phase 4.**
