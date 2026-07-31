# Deferred Work — Beyond Phase 12

Intentionally **not** done in Phase 12. Do not execute as part of closeout.

## Phase 13 — AI / Brainiac (roadmap)

- Core AI platform redesign (Ollama, Open WebUI)  
- AI networking standardization  
- Knowledge / RAG platform  
- Persistent memory (Honcho and successors)  
- Agent framework (Hermes and successors)  
- MCP services  
- GPU optimization & scheduling  
- Model serving standards  

Existing AI containers are **inventory only** in the Phase 12 baseline.

## Other deferred platform work

- Full DockerStandard domain-tree migration (`compose/<domain>/...`)  
- Secrets platform (Vault / Docker secrets / rotation) — roadmap “Phase 12 — Secrets & Security” remains planned naming collision; treat as post-12 security track  
- Nextcloud replacement / cloud redesign  
- Complete `/hive/media` path migration  
- Lidarr (not deployed)  
- SABnzbd (not used)  
- CasaOS retirement for remaining apps (Actual, Crafty, LazyLibrarian, …)  
- Authentik forward-auth on all media UIs  
- Backup redesign beyond cutover snapshots  

## Explicit non-goals of Phase 12.5

No migrations, recreates, upgrades, or live config changes during closeout.
