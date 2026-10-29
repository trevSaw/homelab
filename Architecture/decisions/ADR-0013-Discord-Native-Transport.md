---
title: ADR-0013 Discord Native Transport
document_type: ADR
service: hermes
owner: Homelab
status: Accepted
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0011-KORA-Heavy-Coding-Hermes-Delegation-OpenCode-Go.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - Documentation/Phase4/Discord_Transport.md
  - services/hermes/README.md
---

# ADR-0013 — Discord as a Native Hermes Transport

## Status

**Accepted** (Phase 4, 2026-10-06).

## Context

KORA/Hermes is reached today through Open WebUI via the Hermes `api_server`
(OpenAI-compatible) platform. Phase 4 adds Discord as a second user interface.
The risk to avoid is a second entry path that bypasses KORA's governance, the
Phase 1 evidence semantics, the Phase 2 qBittorrent restrictions, or the Phase 3
Docker administration boundary — or that introduces a bespoke agent/bridge.

## Decision

Use the **native Hermes Discord platform plugin** (`plugins/platforms/discord`,
discord.py 2.7.1) — already shipped in the installed Hermes v0.21.4. Discord
connects as an **outbound Gateway/WebSocket** client; there is no public webhook,
no new inbound port, and no new container.

Discord is configured so that:

* It is **transport only** — it enters the same Hermes Gateway → KORA → Hermes
  Agent pipeline as Open WebUI.
* **KORA remains authoritative** — directives and Phase 1–3 governance apply
  unchanged; a Discord request gets no extra privilege.
* **Hermes remains the execution harness** — no Discord-specific agent, tool
  executor, task queue, or MCP.
* **Existing boundaries are unchanged** — no Docker socket in Hermes, no Docker
  TCP, `docker-admin` remains the only KORA-controlled Docker boundary,
  qBittorrent tools and OpenCode Go delegation are untouched.
* **Least privilege** — `platform_toolsets.discord` mirrors the `api_server`
  tool surface and excludes the native `discord`/`discord_admin` toolsets;
  server `server_actions` is empty.
* **Default deny authorization** — explicit `DISCORD_ALLOWED_USERS` (and/or
  `DISCORD_ALLOWED_CHANNELS`); `DISCORD_ALLOW_ALL_USERS` is not used;
  `require_mention` is on for server channels.

## Alternatives considered

| Option | Pros | Cons | Outcome |
| --- | --- | --- | --- |
| **Native Hermes Discord plugin** | Upstream-supported; same gateway/pipeline; built-in authz, threads, attachments, chunking, reconnect | none material | **Adopted** |
| Custom Discord bridge/bot | Full control | Duplicate runtime; new authz layer; bypass risk; maintenance | Rejected |
| Discord webhook → Hermes | Simple inbound | Public inbound endpoint; not a bidirectional transport; webhook secrets | Rejected |
| Discord MCP just for messages | Fits MCP model | Reimplements transport; not how Hermes platforms work | Rejected |

## Consequences

**Positive:** Discord is additive; all Phases 1–3 and the Open WebUI path are
unchanged; authorization and behavior are upstream-supported configuration, not
code.

**Negative:** A Discord bot token becomes a new secret to manage (gitignored
`.env` only), and enabling the MESSAGE CONTENT intent may be needed for full
message handling. No architecture change is introduced.

## Security

* Bot token only in the gitignored `services/hermes/.env`; never in compose,
  docs, logs, or tool output.
* Default-deny allowlist; no allow-all; mention required in server channels.
* Minimal bot permissions (no Administrator/Manage Server/Roles/Channels/Ban/
  Kick).
* Discord administration toolsets disabled.
* No Docker socket in Hermes; no public endpoint; outbound-only connectivity.

## Compliance

Aligns with the Security Standard (least privilege, explicit authorization,
secrets outside compose) and the Homelab Architecture Standard (single
authoritative gateway, existing boundaries preserved).
