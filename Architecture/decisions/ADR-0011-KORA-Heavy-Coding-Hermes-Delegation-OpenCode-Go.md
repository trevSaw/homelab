---
title: ADR-0011 KORA Heavy-Coding via Hermes Delegation + OpenCode Go
document_type: ADR
service: hermes
owner: Homelab
status: Accepted (Phase 22)
version: 1.0.0
last_reviewed: 2026-09-23
related_documents:
  - Architecture/decisions/ADR-0010-KORA-Execution-Worker-OpenCode-Task-Bridge.md
  - Documentation/Phase22/KORA_OpenCode_Go_Migration.md
  - services/hermes/README.md
  - Architecture/standards/DockerStandard.md
  - Architecture/standards/SecurityStandard.md
---

# ADR-0011 — Hermes as the Agent Harness with OpenCode Go as a Heavy-Coding Model Provider

## Status

**Accepted (Phase 22)** — Hermes upgraded to v0.21.4; delegation + OpenCode Go
configured; Task Bridge deprecated and pending removal after the Go path is
validated with a real OpenCode Go credential.

## Context

Phase 20 introduced the Task Bridge: a separate container running an OpenCode
CLI worker to give KORA real repository execution. Audits (Phase 20.5, the
"coding brain" audits) established that:

1. Hermes v0.17.0 already provides the full agent harness (terminal, process,
   files, git, MCP, skills, delegation) but lacked a strong coding model and
   the OpenCode Go session-header support.
2. OpenCode Go is an **external model provider** (OpenAI-compatible,
   `https://opencode.ai/zen/go/v1`), validated by upstream for Hermes builds
   containing PR #101864 (`x-opencode-session`), i.e. Hermes ≥ v0.21.1.
3. The canonical repository must **not** be bind-mounted into Hermes (Phase
   18.1 exposed 27 gitignored `.env` files); Hermes' native safety is a
   **write** safe-root (`HERMES_WRITE_SAFE_ROOT`), not a read sandbox.

The target architecture makes **Hermes the agent** and **OpenCode Go a model
provider**, removing the OpenCode CLI worker.

## Decision

- Upgrade Hermes from v0.17.0 to **v0.21.4** (digest-pinned) to obtain native
  OpenCode provider support and the `x-opencode-session` header.
- Keep **Ollama / gpt-oss:20b-cloud** as the normal/default model.
- Configure **Hermes delegation** (`delegation.provider: opencode-go`,
  `delegation.model: deepseek-v4-flash`) so KORA can delegate heavy coding/
  engineering work to a **Hermes child agent** backed by OpenCode Go. The child
  inherits the parent's tools, MCPs, filesystem, terminal, and skills (verified
  in v0.21.4: `_build_child_agent` + `inherit_mcp_toolsets`).
- The OpenCode Go credential lives in **Hermes** configuration
  (`OPENCODE_GO_API_KEY` in `services/hermes/.env`, gitignored); KORA never
  sees it.
- **Filesystem boundary:** Hermes works in the sanitized git workspace
  `/opt/data/homelab-workspace` (no `.env`, no secrets). The canonical
  repository remains unmounted; canonical changes go through the approval/
  apply gate `scripts/kora-apply.sh`.
- **Task Bridge is deprecated and targeted for removal** after the Go-backed
  Hermes path is validated with a real credential. No OpenCode CLI worker is
  part of the target architecture.

## Model Routing

```
general/light task → default model (Ollama gpt-oss:20b-cloud)
heavy coding/engineering task → KORA → delegate_task → Hermes child → OpenCode Go (deepseek-v4-flash)
```

Routing is a KORA prompt policy (plugin directive); the heavy model is fixed
server-side (DeepSeek Flash only, no fallback/rotation configured).

## Alternatives Considered

| Alternative | Verdict |
| --- | --- |
| Keep Task Bridge + OpenCode CLI worker | Obsolete; removed per this ADR (pending Go validation) |
| Mount canonical repo into Hermes | Rejected — Phase 18.1 `.env` exposure (27 files) |
| Run Hermes on Go as default model | Rejected — must keep gpt-oss default; cost/routing |
| OpenCode Go without Hermes upgrade (v0.17.0) | Rejected — lacks `x-opencode-session`; some Go backends 400 |

## Consequences

**Positive:** stronger coding intelligence inside the Hermes harness; no
OpenCode CLI process; key isolated from KORA; `.env` boundary preserved;
repository-governance apply gate retained.

**Negative / pending:** live Go validation requires a real `OPENCODE_GO_API_KEY`
(not yet present); Task Bridge remains running (deprecated) until that
validation passes; Hermes upgrade (v0.17.0→v0.21.4) required a `SOUL.md`
permission fix during migration.

## Implementation Notes

- Deployment changes: `services/hermes/compose.yaml` image digest → v0.21.4;
  Hermes `config.yaml` `delegation.{provider,model}` + `platform_toolsets.api_server`
  += `delegation`; KORA plugin directive → `DELEGATION_DIRECTIVE`.
- The Go key is `OPENCODE_GO_API_KEY` in `services/hermes/.env` (gitignored);
  `.env.example` holds a placeholder only.
- Rollback: restore `config.yaml.bak-delegation-*` / `.bak-prev0214-*`, revert
  the compose digest to v0.17.0, and remove `OPENCODE_GO_API_KEY`.
- Task Bridge removal (when Go path validated): stop/remove the container,
  delete `services/taskbridge/`, remove `mcp_servers.taskbridge` +
  `taskbridge` from `platform_toolsets.api_server`, retire Phase 20 docs/ADR.