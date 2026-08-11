# Honcho Memory Assessment — KORA sole personal-memory backend

**Branch:** `phase14-hermes-runtime` (READ-ONLY investigation — no production change)
**Date:** 2026-08-11

---

## 1. Actual Honcho version

**Honcho API v3.0.10** (from `/app/pyproject.toml`, `version = "3.0.10"`), deployed via the `services/honcho` build (api + deriver + pgvector:pg15 + redis:8.2). API healthy on the Docker network (`http://honcho-api:8000/health` → 200).

## 2. Actual Hermes version

**Hermes Agent v0.17.0** (2026.6.19, upstream cf58f1a5), `nousresearch/hermes-agent` (production running; digest-pinned in staging).

## 3. Current Honcho deployment

- Containers: `honcho-api`, `honcho-deriver`, `honcho-postgres` (pgvector), `honcho-redis` — separate services on `ollama_ollama-net`.
- v3 API routers: **workspaces → sessions → peers → messages → conclusions**, plus `conclusions/query` (semantic) and `conclusions/delete`.
- No API-key auth configured for the self-hosted instance (internal network).

## 4. Current Hermes/Honcho integration

- Hermes v0.17.0 ships a **native Honcho memory provider**: `/opt/hermes/plugins/memory/honcho/` (client.py, session.py, cli.py).
- Setup: `memory.provider: honcho` + `$HERMES_HOME/honcho.json` (`baseUrl`, `workspace`, `peerName`, `aiPeer`; `HONCHO_API_KEY`/`HONCHO_BASE_URL` env fallback; local URLs auto-skip API key).
- Provides: automatic two-layer context injection (session summary + user representation + peer cards, refreshed per cadence; optional dialectic `.chat()` reasoning), plus tools `honcho_profile`, `honcho_search` (semantic), `honcho_context`, `honcho_reasoning`, `honcho_conclude` (write persistent fact).
- **Currently NOT enabled** in the deployment: no `honcho.json`, no `HONCHO_*` env, `memory.provider` empty (built-in `MEMORY.md`/`USER.md` only).

## 5. Required KORA memory capabilities

Ordinary personalization/conversational memory: user preferences, likes/dislikes, interests, recurring preferences, useful personal context, conversational history, facts that improve future turns. Explicitly **not** security-sensitive material.

## 6. Honcho capability comparison

| Requirement | Honcho (v3.0.10) | Hermes v0.17.0 | KORA custom code |
|---|---|---|---|
| User preferences | YES — conclusions + user representation | YES — `honcho_conclude`, auto-injection | NO |
| Likes/dislikes | YES — conclusions + dialectic derivation | YES — tools + auto context | NO |
| Persistent user context | YES — peer representations, peer cards | YES — two-layer injection each turn | NO |
| Conversation memory | YES — sessions + session summaries | YES — `honcho_context`, summaries | NO |
| Memory retrieval | YES — `conclusions/query` (semantic), list | YES — `honcho_search`, `honcho_context` | NO |
| Memory creation | YES — `POST .../conclusions` | YES — `honcho_conclude` tool | NO |
| Memory updates/evolution | YES — new conclusions + dialectic reconciliation, delete | YES — dialectic depth/reconciliation | NO |
| Session association | YES — sessions, peers, workspace | YES — gateway session→peer mapping (`pinUserPeer` etc.) | NO |
| Authentication | Self-hosted: internal network (no key needed); cloud: API key | YES — `apiKey`/`baseUrl` config | NO (config only) |

## 7. How KORA accesses Honcho

Directly through Hermes' native memory facilities — **no KORA memory service**:
- The KORA agent (a Hermes agent) gets the honcho tools and automatic context injection by enabling `memory.provider: honcho`.
- Write: agent calls `honcho_conclude` (e.g., user says "I like Japanese curry" → agent persists the fact) or Honcho derives conclusions from sessions.
- Read: automatic per-turn context injection; on-demand via `honcho_search`/`honcho_context`.
- Update: Honcho's conclusions + dialectic reconciliation handle preference changes natively.
- Identity/session: Hermes maps the session/gateway identity to a Honcho peer/workspace.

## 8. What Phase 14.2 currently provides

The in-process `Memory Runtime` (`Runtime/app/`): event-driven proposals (`memory.candidate` on the in-process `EventBus`), **approval-gated** write workflow (Approval Engine + commit coordinator), eligibility/confidence/category/secret-redaction/dedup/capacity checks, SQLite proposal store with terminal-content redaction + audit, and a Honcho adapter that ultimately writes conclusions to Honcho. It has **no committed-memory read path** (deferred) and treats memory as governance-sensitive.

## 9. What Phase 14.2 functionality is redundant

Under the simplified memory definition (ordinary personalization; no secrets, no security-sensitive governance), the Phase 14.2 distinctives are redundant:
- approval-gated writes (not needed for ordinary preferences),
- proposal workflow / audit trail (not needed),
- secret-pattern redaction (not needed — secrets are excluded by policy),
- event-bus-driven candidate ingestion (not needed for agent-initiated memory),
- custom eligibility/dedup/capacity (Honcho's conclusions + dialectic consolidate natively).
The Phase 14.2 Honcho adapter ultimately writes the same Honcho conclusions Hermes can write directly.

## 10. What, if anything, KORA still needs

- **Enablement (configuration, not code):** `memory.provider: honcho` + a `honcho.json` (or env) with `baseUrl: http://honcho-api:8000`, `workspace: kora`, peer settings.
- **Optionally** a KORA agent prompt/policy line instructing the agent to use `honcho_conclude` when the user states a durable preference — prompt/config, not custom code.
- **No custom memory service, no bridge, no proxy, no new Python.**

## 11. Recommended architecture

```
Open WebUI → Hermes → KORA HEAD AGENT
                          └── Memory → Honcho   (Hermes native honcho provider)
```
Phase 14.2 custom Memory Runtime is **retired from the target architecture** (code and checkpoint/backup preserved in git; nothing deleted now).

## 12. Final decision

**OPTION A — HONCHO REPLACES CUSTOM MEMORY.**

Honcho v3.0.10 (already deployed) provides the required memory functionality, and Hermes v0.17.0 ships a native, comprehensive Honcho integration available to the KORA agent with **no custom memory code** — only configuration. The existing custom KORA Memory Runtime is redundant for the intended (ordinary, non-security-sensitive) use case and should be retired from the target architecture.

---

*Read-only. No production changes, no migration, no new code, no deletion of Phase 14.2 artifacts.*
