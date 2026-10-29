---
title: ADR-0014 SearXNG Internal Research Service
document_type: ADR
service: searxng
owner: Homelab
status: Accepted
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - Architecture/standards/DockerStandard.md
  - services/searxng/README.md
  - services/hermes/README.md
---

# ADR-0014 — SearXNG Internal Research Service

## Status

**Accepted** (Phase 5, 2026-10-06).

## Context

KORA/Hermes needs a private web-search capability. The repository Service Index
already lists SearXNG as a *Planned* "Private metasearch engine — used by AI
agents", with Brave Search API as the rejected/alternative. Relying on a
third-party search API would introduce an external dependency and an API key,
and KORA currently has no web-research tool.

An Odysseus-local SearXNG already exists (`services/odysseus/docker-compose.yml`,
bound `127.0.0.1:8585`, attached only to `odysseus_default`). It is coupled to
Odysseus, is not a shared/canonical service, and exposes a host port.

KORA's established pattern for reaching homelab services is a narrow,
read-only `kora.*` plugin tool that calls the service's HTTP API over an
internal network (the Phase 2 qBittorrent precedent); MCP servers are a
separate, allowlisted surface.

## Decision

Stand up a dedicated, canonical **`services/searxng/`** deployment as the
internal-only research service for KORA/Hermes:

- Pin `searxng/searxng:2026.5.31-7159b8aed` (the tag already proven on this
  host; `2026.6.2` is known-bad on boot).
- Attach **only** to the existing external AI fabric `ollama_ollama-net`
  (Hermes is already a member). No new network, no `internal: true` (SearXNG
  needs outbound internet), no published ports, no Traefik route.
- Persist appstate to `/mnt/monarch/appdata/searxng`; keep settings in the
  committed, secret-free `services/searxng/config/settings.yml` with JSON output
  enabled; inject the secret via the gitignored `.env` (`SEARXNG_SECRET`).
- Deploy via the Phase 3 `docker-admin` workflow (`kora.docker_compose_up`,
  project `searxng`).
- Integrate KORA later via a read-only `kora.web_search` plugin tool (direct
  internal HTTP), **not** a new MCP server and **not** a Hermes
  `platform_toolsets` change. This ADR authorizes the service only; the tool is
  a separate, later-approved change.

## Alternatives considered

| Option | Pros | Cons | Outcome |
| --- | --- | --- | --- |
| Reuse the Odysseus-local SearXNG | No new container | Coupled to Odysseus; host-published port; not canonical; not a shared service | Rejected |
| Third-party search API (Brave, Tavily, …) | Managed quality | External dependency, API key/secret, cost/quota, data leaves homelab | Rejected |
| New dedicated `searxng` internal network (Hermes + searxng only) | Tighter isolation | New network requires an Architecture Standard amendment; unnecessary given the AI fabric already exists | Rejected |
| Attach to `kora-admin` (`internal: true`) | Existing network | `internal: true` blocks the outbound internet SearXNG requires | Rejected |
| **Dedicated service on existing `ollama_ollama-net`** | Canonical, internal-only, no new infra, secret-safe, deployable via Phase 3 | One more container on the AI fabric (no published port) | **Adopted** |
| Introduce a SearXNG MCP server | Uniform MCP surface | New MCP surface + `platform_toolsets` change; broader than needed; not the established KORA service-access pattern | Rejected (defer to plugin tool) |

## Consequences

**Positive:** KORA/Hermes gains a private, keyless web-search backend with no
public exposure; reuses existing network/governance; secret stays out of the
repo; canonical service decoupled from Odysseus; deployment uses the approved
Phase 3 path.

**Negative:** A second SearXNG instance runs on the host (the Odysseus-local one
is left unchanged to avoid breaking Odysseus); the container's server process
runs as the image default user (documented exception in the service README);
outbound internet access is required for search.

## Security

Internal-only: no published ports, no Traefik route, no host mount, no Docker
socket, `cap_drop: [ALL]` with the minimal image-required caps, and
`no-new-privileges`. Secret only in the gitignored `.env`. Aligns with the
Security Standard (least privilege, secrets outside Compose/version control) and
the Docker Compose Standard.

## Implementation Notes

- Files: `services/searxng/{compose.yaml,.env.example,.env,config/settings.yml,
  README.md,Versions.md}`; directory `/mnt/monarch/appdata/searxng` created
  before first deploy.
- Deploy: `kora.docker_compose_validate("searxng")` then
  `kora.docker_compose_up("searxng", confirm=true)`; verify health + JSON search.
- Follow-up (separate approval): `kora.web_search` plugin tool; and optionally
  repoint Odysseus' `SEARXNG_INSTANCE` at the shared instance to retire its
  duplicate.
