---
title: ADR-0015 KORA External Web Research via SearXNG
document_type: ADR
service: kora
owner: Homelab
status: Accepted
version: 1.0.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0014-SearXNG-Internal-Research-Service.md
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0011-KORA-Heavy-Coding-Hermes-Delegation-OpenCode-Go.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - services/hermes/README.md
  - services/searxng/README.md
  - Validation/Phase5/KORA_Web_Research_Validation.md
---

# ADR-0015 — KORA External Web Research via SearXNG

## Status

**Accepted** (Phase 5, 2026-10-06).

## Context

SearXNG was deployed as an internal-only service (ADR-0014) but was not yet
reachable by KORA/Hermes. KORA needed a governed external web-research
capability, with a clear policy: local homelab facts use existing tools;
external/current facts use web search; deep repository/code research uses the
OpenCode Go delegation; SearXNG is discovery, never authority; prefer
upstream/official sources; Discord and Open WebUI must have the same capability.

The audit found that Hermes ships a **native `web` toolset** (`web_search`,
`web_extract`) with a **bundled SearXNG provider plugin**
(`plugins/web/searxng`), selected by `SEARXNG_URL` + `web.search_backend`, and
governed by KORA's existing `pre_tool_call` hook. It also found that the bundled
SearXNG provider is **search-only** (no URL extraction), and that the only
`web_extract` providers are third-party (keyless exa/parallel/firecrawl/keenable
or keyed). Finally, it found a defect: KORA's destructive-name guard matched the
substring `"rmi"` inside **`terminal`**, silently blocking all shell use (so
neither KORA nor delegated children could fetch a repository).

## Decision

Integrate SearXNG through Hermes' **native, supported mechanism** — no custom
bridge, no new MCP server:

1. `SEARXNG_URL=http://searxng:8080` (compose environment; non-secret).
2. `web.search_backend: searxng` in Hermes `config.yaml`.
3. `web.keyless_fallback: false` — do **not** silently route extraction to
   third-party keyless providers. `web_extract` is therefore unavailable;
   pages/repos are fetched with `terminal` (curl/git) or via delegation.
4. Enable the `web` toolset for **both** `platform_toolsets.api_server` and
   `platform_toolsets.discord` (same capability on both transports).
5. Add a KORA `RESEARCH_DIRECTIVE` encoding the policy (source selection,
   "SearXNG is discovery not authority", prefer upstream, no snippet-only
   claims, no invented versions).
6. Fix the `pre_tool_call` guard to match destructive **tokens**, not
   substrings, so `terminal` is not falsely blocked; destructive names
   (`*.remove`, `*.prune`, `*.exec`, ...) remain blocked.

SearXNG engine tuning: this host's egress IP is blocked/handed anti-bot junk by
most general engines. The `github` engine (official GitHub API, no key) is
enabled and re-categorised into `general` so `web_search` reliably discovers
software upstreams; `bing` is kept best-effort; blocked engines are disabled.

## Alternatives considered

| Option | Pros | Cons | Outcome |
| --- | --- | --- | --- |
| **Native Hermes `web` toolset + bundled searxng provider** | Fully supported, no bridge, no new process/supply chain, governed by KORA hook, per-platform parity | `web_extract` not self-hostable | **Adopted** |
| Custom SearXNG MCP server / bridge | Uniform MCP surface | New surface + supply chain; broader than needed; explicitly discouraged by the task | Rejected |
| Third-party search API (Brave/Tavily/…) | Managed quality | External dependency/key/cost; data leaves homelab; against self-hosted goal | Rejected |
| Enable keyless third-party `web_extract` | One-call page fetch | Sends URLs to unapproved third parties | Rejected (deferred; needs separate approval) |
| Leave `terminal` blocked | No shell exposure | Repo/page fetching impossible; contradicts KORA directives that reference terminal | Rejected (defect fix) |

## Consequences

**Positive:** KORA has genuine external web research through the self-hosted
SearXNG, selected by the runtime, with no custom bridge and no new privilege.
Discord and Open WebUI share the identical toolset. The terminal guard fix
restores the repo-fetch/`delegation` path that Phase 22 assumes. KORA remains
the governance layer (every tool call is authorized/recorded by `pre_tool_call`).

**Negative / limitations:** `web_extract` is unavailable (search-only backend),
so pages/repos are fetched via `terminal` or delegation. The local model
(`gpt-oss:20b-cloud`) is inconsistent at multi-step tool use and can fabricate
(e.g. it suggested an upstream image tag `1.3.5` that does not exist — upstream
tags stop at v1.3.2); the RESEARCH_DIRECTIVE explicitly forbids invented
versions. General-engine snippets from this IP are unreliable; the GitHub engine
is the dependable discovery path.

## Security

No Docker socket, no new runtime, no Task Bridge, no bypass of KORA. SearXNG is
internal-only (no published ports). The `web` tools are read-only discovery.
Enabling the already-configured `terminal` restores a capability that
`platform_toolsets` already granted and that KORA directives already assumed;
Hermes' own approval system still gates destructive commands (a delegated
`rm -rf` was held for approval during validation). Aligns with the Security
Standard and the Docker Compose Standard.

## Implementation Notes

- `services/hermes/compose.yaml` — `SEARXNG_URL` (default `http://searxng:8080`).
- `services/hermes/.env.example` — documented.
- Hermes `config.yaml` (appdata, backed up) — `web.search_backend: searxng`,
  `web.keyless_fallback: false`, `web` added to `api_server` + `discord`.
- `services/hermes/plugin/kora/__init__.py` — `RESEARCH_DIRECTIVE` added to
  `pre_llm_call`; token-based destructive guard in `pre_tool_call`.
- Validation: see `Validation/Phase5/KORA_Web_Research_Validation.md`.
