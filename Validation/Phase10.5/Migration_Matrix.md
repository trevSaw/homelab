# Phase 10.5 — Migration Matrix (hardened)

Policy frozen: config → `/mnt/monarch/appdata`; large datasets on `/hive`; **Ollama models move with config**.

| Order | Service | Current | Target | Req? | Matches target? | Risk | Rollback / notes |
|------:|---------|---------|--------|------|-----------------|------|------------------|
| 10 | code-server | `/hive/code-server/config` | `.../code-server` | yes | no | low | bak + `.old`; needs `.env` |
| 11 | homepage | `/hive/config/homepage` | `.../homepage` | yes | no (live drift) | low | also migrate homepage-images |
| 11 | homepage-images | `/hive/data/homepage/images` | `.../homepage/images` | yes | no | low | companion |
| 12 | traefik | appdata acme | `.../traefik` | verify | yes (live) | low* | non-empty dest EXPECTED |
| 13 | beszel | appdata | same | no | yes | low | N/A |
| 14 | portainer | `/hive/portainer` | `.../portainer` | yes | no | low | exclude unreadable 49/50; tiny |
| 15 | beszel-agent | relative | TBD | deferred | n/a | low | — |
| 20 | authentik | PATH_DATA | `.../authentik` | verify | partial | medium | stack may be undeployed |
| 21–24 | honcho, hermes, n8n, open-webui | appdata | same | no | yes | medium | N/A |
| 25 | odysseus | `./data` | TBD | deferred | partial | medium | — |
| 30 | ollama | `/hive/ollama` | `.../ollama` | yes | no | higher | **models included**; relocatable later |
| 31–32 | calibre, calibre-web | `/hive/.../config` | appdata | yes | no | higher | books stay |
| 35–36 | echoos, cosmoos | special | — | deferred/no | n/a | higher | — |
| 40 | jellyfin | `/hive/jellyfin/config` | `.../jellyfin` | yes | no | final | media stay |
| 41 | nzbget | `/hive/NZBget/config` | `.../nzbget` | yes | no | final | **exclude downloads/** + logs |
| 42 | hotio | `/hive/Hotio/config` | `.../hotio` | yes | no | final | downloads stay |

\*traefik = small data, high blast radius.

## Operator notes

- Prefer order 10 → 42; skip `no`/`deferred` until classified.
- Always read the **operator summary block** at the end of each script — do not judge success mid-log.
- NZBget: after copy with excludes, confirm NZBget still points downloads at `/hive/downloads` (or nested path intentionally left on hive).

## Assumptions / limitations

See [Migration_Inventory.md](Migration_Inventory.md).
