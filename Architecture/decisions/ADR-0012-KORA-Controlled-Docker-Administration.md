---
title: ADR-0012 KORA Controlled Docker Administration
document_type: ADR
service: kora
owner: Homelab
status: Accepted
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0011-KORA-Heavy-Coding-Hermes-Delegation-OpenCode-Go.md
  - Documentation/Phase3/KORA_Controlled_Administration.md
  - services/docker-admin/README.md
  - Architecture/standards/SecurityStandard.md
---

# ADR-0012 — KORA Controlled Docker Administration

## Status

**Accepted** (Phase 3, 2026-10-06).

## Context

KORA/Hermes could reason about live state (Phase 1) and inspect qBittorrent
read-only (Phase 2), but could not inspect live Docker state or perform any
homelab administration. Container-level evidence came from a host-generated,
easily-stale snapshot (`/opt/data/docker-state`), and there was no deploy path.

Docker control requires access to `/var/run/docker.sock`, which is effectively
host-level privilege. Giving the socket to Hermes would let a model-driven tool
surface reach arbitrary `docker` operations (exec, delete, prune, host mounts).

## Decision

Add a single dedicated helper container, `docker-admin`, as the only Docker
socket holder on the KORA administration path, exposing a **fixed, whitelisted,
token-authenticated HTTP API**. Hermes/KORA never receive the socket. The helper
builds validated `docker` / `docker compose` argv and offers no generic proxy,
no `exec`, and no deletion/prune operations.

KORA gains dedicated plugin tools (`kora.docker_*`) that call the helper. Read
operations are automatic; `restart` and `compose up` require `confirm: true` and
cannot target the control plane (`hermes`, `docker-admin`). Compose deploy uses
only the canonical repository (mounted read-only), preserving the repository as
the configuration source of truth. KORA governance (`pre_tool_call`,
directives) continues to apply.

## Alternatives considered

| Option | Pros | Cons | Outcome |
| --- | --- | --- | --- |
| Extend host-side `scripts/kora-apply.sh` / host daemon | No container has the socket | No passwordless root/systemd available; less reproducible; hard to make synchronous live reads | Rejected |
| Host snapshot only (status quo) | Zero new privilege | Stale, no writes, no live evidence | Insufficient |
| `docker-socket-proxy` style generic proxy | Off-the-shelf | Method-level gating cannot separate restart from exec; no per-operation policy; "generic" surface | Rejected |
| **Narrow purpose-built helper (`docker-admin`)** | Repo-managed, reproducible, explicit whitelist, no generic surface, control-plane guards | One container owns the socket; repo `.env` readable by the helper | **Adopted** |
| Socket directly in Hermes | Simplest | Unacceptable blast radius; model reaches host privilege | Rejected |

## Consequences

**Positive:** live, truthful Docker inspection; controlled restart/recreate;
Compose validation/deploy from the canonical repo; socket stays out of Hermes;
destructive operations absent by construction.

**Negative:** `docker-admin` is a privileged target (mitigated by whitelist,
auth, internal-only network, unprivileged user, read-only rootfs, capability
drop, `no-new-privileges`); the helper can read canonical `.env` files (needed
for Compose substitution) but the API never returns file contents or resolved
config.

## Security

See `Documentation/Phase3/KORA_Controlled_Administration.md` §8. No Docker TCP,
no public exposure, no host root mount, env values redacted, destructive
operations unavailable.

## Compliance

Aligns with the Security Standard (least privilege, secrets outside Compose) and
the Docker Compose Standard. The socket is a documented, reviewed exception
scoped to the administration helper.
