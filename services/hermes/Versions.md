# Hermes — Image Versions (Phase 22)

| Component | Image / Tag | Notes |
| --- | --- | --- |
| Hermes Agent | `nousresearch/hermes-agent@sha256:6bece0644e29a347e5ae17db43c36938c86f171c6f5e0cef18aa2075d331f3a3` | **v0.21.4 (2026.9.21)** · upstream `d337b736` · digest-pinned |
| KORA plugin | `services/hermes/plugin/kora/` (runtime `/opt/data/plugins/kora`, `plugin.yaml` v0.5.2) | Phase 3 adds `kora.docker_*` controlled administration tools; v0.5.2 routes infrastructure troubleshooting to the tool-enabled `operational` path |
| Discord platform (native) | `plugins/platforms/discord/` (in-image); `discord.py 2.7.1` | Phase 4 transport; enabled by `DISCORD_BOT_TOKEN`; `platform_toolsets.discord` = api_server parity |

**Upgrade rationale (Phase 22):** Hermes ≥ v0.21.1 is required for OpenCode Go
(`x-opencode-session` header, PR #101864). v0.21.4 is the current stable
release containing it.

Last reviewed: 2026-09-23