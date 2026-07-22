## Migration Wave Plan

| Wave | Services (ordered by dependency) |
|------|---------------------------------|
| **Wave 1** (critical) | EchoOS, echoos |
| **Wave 2** (core infrastructure) | odysseus → ollama → traefik |
| **Wave 3** (management) | portainer |
| **Wave 4** (media & productivity) | jellyfin, Hotio, calibre‑web |
| **Wave 5** (automation & development) | n8n, honcho, code‑server |
| **Wave 6** (utility & monitoring) | authentic, beszel, beszel_agent, hermes, homepage, NZBget |
| **Wave 7** (infrastructure) | CosmoOS |

*Each wave respects explicit Docker dependencies and logical network dependencies (e.g., `odysseus` after `ollama`; services using `proxy` after `traefik`).*