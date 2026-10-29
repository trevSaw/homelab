# Hermes + OpenCode Go — Heavy-Coding Migration (Phase 22)

**Status:** Implemented (config/delegation) 2026-09-23. Task Bridge removal is
pending live validation of the OpenCode Go path with a real credential.

## Target architecture

```text
Open WebUI ──► KORA ──► Hermes v0.21.4
                          │
              ┌───────────┴───────────┐
              │                       │
         GENERAL                   HEAVY
              │                       │
              ▼                       ▼
         Ollama                 Hermes child
     gpt-oss:20b-cloud               │
              │                       ▼
              │                OpenCode Go API
              │                       │
              │               deepseek-v4-flash
              │                       │
              └────── same Hermes tools/MCP/terminal/files/git ──────┘
                          │
                          ▼
                 /opt/data/homelab-workspace   (sanitized, no .env)
                          │
                          ▼
                 scripts/kora-apply.sh  (approval/apply gate)
                          │
                          ▼
                 canonical homelab repo   (never mounted into Hermes)
```

## What changed

1. **Hermes upgraded** v0.17.0 → **v0.21.4** (digest
   `sha256:6bece064…`), which includes native OpenCode provider support and the
   `x-opencode-session` header (PR #101864, required by OpenCode Go).
   Migration fix applied: `/opt/data/SOUL.md` made writable so v0.21.4 could
   replace the legacy comment-only scaffold (no custom persona was lost).
2. **OpenCode Go provider** configured via Hermes delegation:
   `delegation.provider: opencode-go`, `delegation.model: deepseek-v4-flash`.
   Endpoint `https://opencode.ai/zen/go/v1`, api_mode `chat_completions`.
3. **Credential** `OPENCODE_GO_API_KEY` in `services/hermes/.env` (gitignored);
   placeholder only in `.env.example`. Belongs to Hermes, never KORA.
4. **Delegation toolset enabled** for the api_server platform; KORA plugin
   directive updated to use `delegate_task` for heavy work.
5. **Filesystem boundary unchanged:** canonical repo not mounted; Hermes works
   in `/opt/data/homelab-workspace` (sanitized git repo, no `.env`, writable,
   `HERMES_WRITE_SAFE_ROOT=/opt/data`). Canonical apply via `kora-apply.sh`.
6. **Task Bridge deprecated** — to be removed after Go-path validation.

## Verified

- General request → `gpt-oss:20b-cloud` (PASS).
- Delegation credential resolution → `{provider: opencode-go, model:
  deepseek-v4-flash, base_url: https://opencode.ai/zen/go/v1, api_mode:
  chat_completions}` (PASS, config-level; live call requires the key).
- MCP (jdocmunch / context7 / graphify) enabled post-upgrade.
- Hermes cannot reach the canonical repo or the Docker socket.
- Workspace contains no `.env`/secrets.

## Validation required (pending real credential)

With `OPENCODE_GO_API_KEY` set in `services/hermes/.env` and Hermes restarted:
1. Heavy delegated task executes on DeepSeek Flash (verify in gateway logs).
2. Child retains terminal/files/MCP/skills inside the workspace.
3. Then remove Task Bridge (container, config, docs, ADR-0010).

## Rollback

Restore `config.yaml.bak-delegation-*`, revert compose digest to v0.17.0,
remove `OPENCODE_GO_API_KEY`, and (if needed) restore the old KORA plugin from
`__init__.py.bak-prev0214-*`.