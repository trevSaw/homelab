---
title: KORA Discord Transport (Phase 4)
document_type: Implementation Report
service: hermes
owner: Homelab
status: Validated — Discord bot online; auto-thread remediation applied (Phase 4.1)
version: 1.3.0
last_reviewed: 2026-10-06
related_documents:
  - Architecture/decisions/ADR-0013-Discord-Native-Transport.md
  - Architecture/decisions/ADR-0004-KORA-Orchestration-Hermes.md
  - Architecture/decisions/ADR-0012-KORA-Controlled-Docker-Administration.md
  - services/hermes/README.md
  - Documentation/Phase3/KORA_Controlled_Administration.md
---

# KORA Discord Transport (Phase 4)

**Status:** Validated (2026-10-06). The **Message Content Intent was enabled**
in the Discord Developer Portal; the native Discord gateway is **connected** and
the bot is **online**. A live server test (authorized user mentions the bot → KORA
responds) succeeded and was verified from gateway logs, the Discord API, and the
KORA explainability record.

Discord is added as a first-class **I/O transport** into the existing KORA/Hermes
architecture using Hermes' **native Discord platform plugin**. No custom agent,
bridge, webhook worker, second runtime, or second authorization layer was added.

## 0. Root cause — resolved (2026-10-06 follow-up)

**Resolution:** the **Message Content Intent** was enabled in the Developer
Portal. On gateway restart the adapter reached `READY`
(`[Discord] Connected as Korra#5669`) and `gateway_state.json` reports
`discord.state = connected`. `GET /applications/@me` now shows
`MESSAGE_CONTENT_INTENT_ENABLED: True`; the application is also now
`bot_public: False` (private).

### Original root cause (for the record)

**Root cause:** the Discord application has the privileged **Message Content
Intent disabled**. Hermes' native adapter requests `intents.message_content =
True` unconditionally (`adapter.py:1246`), so Discord rejects the gateway
`IDENTIFY` (close code 4014) with `discord.errors.PrivilegedIntentsRequired`.
The adapter classifies this as **non-retryable**, parks the platform, and the
gateway continues serving `api_server` in a DEGRADED state. The bot never reaches
`READY`, so it appears **offline**.

**Evidence:**

* `gateway_state.json` → `discord.state = fatal`,
  `error_code = discord_intents_required`,
  `error_message` = "…privileged Gateway Intents are not enabled… Message Content
  Intent (required to read message text)".
* `errors.log` (reproduced on a fresh gateway restart at 2026-10-06 18:00:02
  JST / 09:00:02 UTC): `discord.errors.PrivilegedIntentsRequired: Shard ID None
  is requesting privileged intents that have not been explicitly enabled in the
  developer portal`.
* `GET https://discord.com/api/v10/applications/@me` → application **Kora**,
  `flags = 0` ⇒ `MESSAGE_CONTENT_INTENT_ENABLED: False` (and
  `GUILD_MEMBERS_INTENT_ENABLED: False`).
* Token check (`GET /users/@me` with a proper User-Agent) → **VALID**.
* DNS `discord.com` resolves; HTTPS reaches Discord; no proxy env vars.
* `_needs_server_members_intent` returns **False** for the numeric allowlist, so
  only **Message Content Intent** is requested (matches the guidance text).

**Remediation (manual, Developer Portal only):**

1. Open <https://discord.com/developers/applications> → application **Kora** →
   **Bot** → **Privileged Gateway Intents**.
2. Enable **MESSAGE CONTENT INTENT** → **Save Changes**.
3. Restart the gateway: `docker restart hermes` (or
   `docker exec hermes /opt/hermes/.venv/bin/hermes gateway restart`).
4. Confirm the bot shows **online** and the log shows Discord `READY` (no
   `PrivilegedIntentsRequired`).

Note: setting the flag via the API is **not supported** — `PATCH
/applications/@me {"flags": 262144}` returned HTTP 200 but left `flags = 0`. The
toggle is portal-only.

**Security observation:** `applications/@me` reports `bot_public: true` (the bot
is publicly installable). Authorization remains default-deny and the allowlist is
intact, so this is not an escalation; making the application **private** in the
same portal page is recommended as hardening.

**Upstream alternative (not taken):** because Discord still delivers message
content in DMs and messages that mention the bot without the intent, the adapter
*could* omit `message_content`; that requires changing upstream Hermes source and
is explicitly out of scope for this task.

## 1. Architecture

```text
Discord ─┐
         ├─▶ Hermes Gateway ─▶ KORA ─▶ Hermes Agent ─┬─ Ollama  gpt-oss:20b-cloud
Open WebUI┘                                            ├─ OpenCode Go  deepseek-v4-flash
                                                       ├─ MCPs / skills / delegation
                                                       └─ docker-admin / qBittorrent tools
```

Discord and Open WebUI share one authoritative Hermes gateway. Discord is an
outbound Discord Gateway/WebSocket client (discord.py 2.7.1) — no public webhook,
no new inbound port, no Traefik route, no extra container.

## 2. Native Discord support (audit)

| Item | Finding |
| --- | --- |
| Installed Hermes | **v0.21.4** (2026.9.21, upstream `d337b736`) |
| Native Discord plugin | `plugins/platforms/discord/` (`adapter.py`, `adapter_media.py`, `recovery.py`, `voice_mixer.py`) |
| Library | `discord.py 2.7.1` |
| Enablement | Platform enables when `DISCORD_BOT_TOKEN` is present (`PLATFORM_TOKEN_ENV_NAMES` / `_ENV_ENABLE_CREDENTIALS`) |
| Authorization | `DISCORD_ALLOWED_USERS`, `DISCORD_ALLOWED_ROLES`, `DISCORD_ALLOWED_CHANNELS`, `DISCORD_IGNORED_CHANNELS`; `DISCORD_ALLOW_ALL_USERS` is deny-by-default when unset |
| Behavior keys | `require_mention`, `free_response_channels`, `auto_thread`, `reactions`, `history_backfill`, `server_actions`, `max_attachment_bytes` |
| Toolsets | `platform_toolsets.discord` (was `[hermes-discord]` incl. `discord`, `discord_admin`) |

**Conclusion:** native support is complete and preferred; no compatibility layer was
created.

## 3. Changes

| File | Change |
| --- | --- |
| `/opt/data/config.yaml` (Hermes volume) | `platform_toolsets.discord` set to `[connections, file, kora, taskbridge, terminal, delegation]` (api_server parity; drops `discord`/`discord_admin`). Conservative `discord:` behavior block retained. |
| `services/hermes/.env.example` | Added `DISCORD_BOT_TOKEN`, `DISCORD_ALLOWED_USERS`, `DISCORD_ALLOWED_CHANNELS`, `DISCORD_REQUIRE_MENTION`, `DISCORD_HOME_CHANNEL`, `DISCORD_ALLOW_ALL_USERS` (documentation only; no values). |
| `services/hermes/compose.yaml` | Comment documenting that Discord is `.env`-driven and the token is never declared in compose. No functional/secret change. |
| `services/hermes/README.md` | New "Discord transport (Phase 4)" section. |
| `Architecture/decisions/ADR-0013-Discord-Native-Transport.md` | New ADR. |
| `Architecture/decisions/ADRIndex.md` | ADR-0013 indexed. |
| `Services/ServiceIndex.md` | Hermes row notes Phase 4 Discord transport. |
| `Documentation/Phase4/Discord_Transport.md` | This report. |

## 4. Discord configuration (variable names only)

| Variable | Set in | Notes |
| --- | --- | --- |
| `DISCORD_BOT_TOKEN` | `services/hermes/.env` (gitignored) | Secret; presence enables the platform. |
| `DISCORD_ALLOWED_USERS` | `.env` | Explicit user-ID allowlist; **required** for access. |
| `DISCORD_ALLOWED_CHANNELS` | `.env` | Optional explicit channel-ID allowlist. |
| `DISCORD_REQUIRE_MENTION` | `.env` / config | `true`. |
| `DISCORD_HOME_CHANNEL` | `.env` | Optional cron/notification target. |
| `DISCORD_ALLOW_ALL_USERS` | `.env` | `false`; not to be enabled. |

No value is recorded in this document or in any committed file.

## 5. Authorization model

* **Default deny.** With no allowlist and no allow-all, the adapter rejects all
  messages and logs `_warn_if_fail_closed_default`.
* Only explicit `DISCORD_ALLOWED_USERS` (and/or `DISCORD_ALLOWED_CHANNELS`)
  authorize. Role auth is not enabled (`dm_role_auth_guild` empty).
* Server channels use `require_mention: true`; `free_response_channels` is empty.
* DMs are gated by the same user allowlist.

## 6. Permissions

Intended bot permissions (Discord application/bot model, private application):
View Channels, Send Messages, Read Message History, Embed Links, Attach Files,
Send Messages in Threads, Add Reactions. **Not granted:** Administrator, Manage
Server, Manage Roles, Manage Channels, Ban Members, Kick Members. The native
`discord_admin` toolset is removed from `platform_toolsets.discord`, and
`discord.server_actions` is empty.

## 7. Session mapping

Native `gateway/session.py` (`build_session_key`):

| Surface | Key | Isolation |
| --- | --- | --- |
| DM | `agent:main:discord:dm:<chat_id>:<user>` | per DM user |
| Server channel | `agent:main:discord:channel:<channel_id>:<user>` | per user (`group_sessions_per_user: true`) |
| Thread | `agent:main:discord:thread:<channel_id>:<thread_id>` | shared thread session |

Open WebUI uses the `api_server` platform namespace, so Discord and Open WebUI
sessions never collide.

## 8. Inherited behavior

* **Long-running tasks:** typing indicators/reactions while working; final result
  delivered on completion; native Discord button approvals. No custom queue.
* **Message limits:** chunked at 2000 chars (split threshold 1900) with a chunk
  cap that replaces overflow with a notice.
* **Attachments:** images/audio as media; documents cached under the 32 MiB cap
  (`max_attachment_bytes`); small text-like files inlined (≤100 KB); SSRF-guarded
  downloads; nothing is executed.
* **Reconnect:** discord.py reconnect + adapter liveness probe; connect failures
  classified (`LoginFailure` non-retryable, others retryable) and supervised by
  the gateway.
* **Governance:** identical to Open WebUI — Phase 1 evidence semantics, Phase 2
  qBittorrent read-only tools, Phase 3 Docker confirmation/deny boundaries, and
  OpenCode Go delegation all apply unchanged.

## 9. Validation results (2026-10-06, Discord online)

Legend: **LIVE** = observed from Discord/gateway runtime; **DYN** = live adapter
code exercised in-process with synthetic inputs (no Discord traffic);
**INSPECT** = config/source inspection.

| # | Check | Method | Result |
| --- | --- | --- | --- |
| 1 | Discord plugin loaded / platform registered | LIVE | PASS (`Connecting to discord...`, `gateway_state.json`) |
| 1 | Bot reached `READY` and is online | LIVE | PASS (`[Discord] Connected as Korra#5669`; `discord.state=connected`) |
| 1 | Authorized user mention → KORA response | LIVE | PASS (`inbound message ... user=fatherFranku`; `response ready ... time=6.9s`; Discord API shows reply) |
| 2 | Unauthorized user denied | DYN | PASS (`_is_allowed_user("123456789012345678")` → False, DM and channel) |
| 3 | `@Korra` invokes KORA | LIVE | PASS (mention turn dispatched) |
| 3 | Non-mentioned channel message ignored | DYN | PASS (`require_mention=True`, `free_response_channels=∅`) |
| 4 | Discord enters the same KORA pipeline | LIVE | PASS (KORA explain record for the Discord session; delivered message carries the `[KORA]{...}` digest) |
| 4 | Transport only (no separate agent) | INSPECT | PASS (native `discord-platform`; one gateway; identical toolset) |
| 5 | qBittorrent read-only tools | LIVE | PASS (`v4.5.5`) |
| 5 | Docker tools via docker-admin; confirmation/deny | LIVE | PASS (`docker_list`=55; `restart hermes`→`restart-target-denied`) |
| 5 | No Docker socket in Hermes; docker-admin boundary | INSPECT | PASS |
| 5 | No Discord admin/server-management privilege | LIVE | PASS (guild perms: no Admin/Manage/Roles/Channels/Ban/Kick; has View/Send/History/Embed/Attach/Threads/React) |
| 6 | Normal Discord request uses `gpt-oss:20b-cloud` | LIVE | PASS (`session_model_usage.model = gpt-oss:20b-cloud`) |
| 6 | Heavy delegation provider/model | INSPECT | PASS (`delegation: opencode-go / deepseek-v4-flash`) |
| 7 | Open WebUI regression | LIVE | PASS (`api_server` KORA tool request → `v4.5.5`) |
| 8 | Thread behavior | LIVE | PASS (turn ran in `agent:main:discord:thread:...`; bot replied in the thread) |
| 8 | Attachments | — | Not live-tested (requires a user-sent attachment); native handling inspected (images/audio media; docs cached ≤32 MiB; small text inlined; SSRF-guarded; nothing executed) |
| 8 | Long-running task UX | — | Not live-tested via Discord (requires a Discord-origin long job); native gateway handling inspected |
| 9 | Token not in git/logs/docs/model output | INSPECT | PASS (0 log files contain it; `.env.example` empty) |
| 9 | `DISCORD_ALLOWED_USERS` configured | LIVE | PASS (SET) |
| 9 | `DISCORD_ALLOW_ALL_USERS` not enabled | LIVE/DYN | PASS (UNSET; `_discord_allow_all_users()` → False) |
| 9 | No public webhook / inbound Discord endpoint | INSPECT | PASS (outbound WS only; only `127.0.0.1:8642`) |

**Message Content Intent:** `GET /applications/@me` → `MESSAGE_CONTENT_INTENT_ENABLED: True`,
`bot_public: False`.

## 10. Deferred

* Live Discord attachment round-trip and Discord-originated long-running
  delegation (not safely testable from the automation side; recommended as
  quick manual spot-checks).
* Discord voice features (native `voice_fx` remains disabled).
* Any Discord server administration (intentionally not exposed).
* Removal of the deprecated `taskbridge` toolset entry from
  `platform_toolsets.discord`/`api_server` (separate cleanup; not required for
  Discord startup).

## 11. Operation

1. Create a private Discord application + bot; copy the bot token.
2. Put token + allowlist only in `services/hermes/.env`.
3. Enable the **Message Content Intent**; invite the bot with the minimal
   permissions from §6.
4. `docker compose -f services/hermes/compose.yaml up -d`.
5. `docker exec hermes /opt/hermes/.venv/bin/hermes gateway status`.
6. Test DM, mention, non-mention, unauthorized user, threads.

## 12. Phase 4.1 — auto-thread creation failure (diagnosed & fixed 2026-10-06)

**Symptom:** an authorized mention reached Hermes, but replies showed
"⚠️ Hermes could not create a Discord thread for this message, so the request was
not processed." The bot stayed online and its fallback seed messages sent fine.

**Confirmed cause (upstream Hermes v0.21.4 + discord.py interaction, not a
Discord permission or config error):** Hermes' default `DISCORD_COMMAND_SYNC_POLICY=safe`
runs a paced slash-command reconcile and, for its duration, sets
`http.max_ratelimit_timeout = 30` on the discord.py client. discord.py copies
that value onto each per-route rate-limit bucket **when the bucket is first
created**. The first auto-thread (the "hello" test at 09:08:47 UTC) happened
*during* the reconcile (which finished at 09:09:50 UTC), so the thread-creation
bucket cached `30`. Discord's thread-create bucket advertises a 300 s reset
window, so `_Bucket.acquire()` then raised `RateLimited` **pre-emptively** for the
rest of that window ("Too many requests. Retry in Ns") without ever contacting
Discord. The request was never actually rejected by Discord.

**Evidence:**

* `errors.log`: `Auto-thread creation failed ... Direct error: Too many requests.
  Retry in 184.76 seconds.` (09:10:43) and `... 129.72 seconds.` (09:11:38) — both
  count down to the same reset (09:13:48), i.e. a bucket window, not a fresh 429.
* The successful `hello` thread was created at 09:08:47, inside the reconcile
  window (start ~09:04, finish 09:09:50, `created=70`).
* Fallback `channel.send` (a different bucket) always succeeded, so the token and
  message-send permissions were fine.
* The thread-create route was healthy after the window: a direct
  `POST /channels/{id}/messages/{id}/threads` probe returned **201**
  (`X-RateLimit-Remaining: 49`, `X-RateLimit-Reset-After: 300`).
* Not a permission issue: the bot already owns the `hello` thread and
  `Create Public Threads`/`Send Messages in Threads` are granted (§6 and the
  live guild-permission audit in §9).

**Remediation (config-only, no upstream patch, `auto_thread` preserved):**
set `DISCORD_COMMAND_SYNC_POLICY=bulk`. The `bulk` branch of
`_run_post_connect_initialization` performs the same reconcile as a single
`tree.sync()` request and **does not touch `max_ratelimit_timeout`**, so route
buckets can never cache a non-`None` cap. Added to
`services/hermes/compose.yaml` (default) and `services/hermes/.env.example`.

**Validation after remediation:**

| Check | Method | Result |
| --- | --- | --- |
| Bot online / connected | LIVE | PASS (`Connected as Korra#5669`; `discord.state=connected`) |
| Command sync (no `max_ratelimit_timeout` mutation) | LIVE | PASS (`Synced 70 slash command(s) via bulk tree sync`) |
| Thread creation from a message (the failing op) | LIVE (Discord API) | PASS (`POST .../threads` → 201; probe thread archived) |
| Open WebUI → KORA → qBittorrent regression | LIVE | PASS (`v4.5.5`, connected) |
| Docker socket absent / `docker-admin` boundary | INSPECT | PASS |
| Allowlist enforced; `ALLOW_ALL_USERS` unset | LIVE/INSPECT | PASS |
| No token in logs/repo; `git diff --check` clean | INSPECT | PASS |
| **End-to-end: `@Korra` → auto-thread → KORA → qBittorrent → thread reply** | LIVE | **PASS** |

**End-to-end confirmation (2026-10-06 18:26 JST):** authorized user
`fatherFranku` sent `@Korra a can you tell me what torrents i have seeding?`;
the gateway created auto-thread `List torrents seeding` (chat `…985045`), the
Discord session `20261006_182646_fae4cb9e` invoked the read-only
`kora.qbit_torrents` tool (twice, `decision=allowed`), and KORA delivered live
torrent state in the thread (108.9 s, 4 API calls, 829-char response plus a
continuation after a transient mid-stream cut, then the thread was renamed).
No further auto-thread failures occurred (the only two in the log predate the
fix). **Phase 4.1 validated.**
