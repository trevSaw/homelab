# Phase 14.2 Preflight — Migration Plan

**Executed:** 2026-08-01  
**Method:** Container recreate from new compose SoT; **no** `compose down` of shared network projects; data binds unchanged.

---

## Execution order (completed)

1. Inspect live ownership, networks, mounts, Phase 13 Memory contracts  
2. Harden `services/ollama/compose.yaml` (`ollama_ollama-net` → **external**)  
3. Ensure local `services/ollama/.env` (gitignored)  
4. Archive/disable `/hive/ollama/compose.yml`; leave models in place  
5. Stop/rm **only** `ollama` → `docker compose -p ollama -f services/ollama/compose.yaml up -d`  
6. Validate network + model list + KORA health  
7. Ensure local `services/hermes/.env` (gitignored)  
8. Archive/disable `/mnt/monarch/appdata/hermes/compose.yml`; leave data in place  
9. Stop/rm **only** `hermes` → `docker compose -p hermes -f services/hermes/compose.yaml up -d`  
10. Validate Hermes Traefik + data mount  
11. Document Open WebUI SoT boundaries; harden compose comments  
12. Publish Memory approval UX design (no Honcho writes)

---

## 1. Ollama ownership migration

### Current → target

| Item | Before | After |
| --- | --- | --- |
| Compose SoT | `/hive/ollama/compose.yml` | `services/ollama/compose.yaml` |
| Project workdir label | `/hive/ollama` | `.../services/ollama` |
| Data bind | `/hive/ollama:/root/.ollama` | **unchanged** |
| Network | project-defined `ollama-net` | **external** `ollama_ollama-net` |
| Image | `ollama/ollama:latest` (v0.30.10) | pinned `ollama/ollama:0.30.10` |

### File moves / archives (host)

| Path | Action |
| --- | --- |
| `/hive/ollama/compose.yml` | → `compose.yml.DISABLED-use-services-ollama` |
| `/hive/ollama/compose.yml.LEGACY-DO-NOT-USE` | backup copy |
| `/hive/ollama/README.COMPOSE_OWNERSHIP.md` | ownership notice |
| `/hive/ollama/models` (+ cache/state) | **not moved** |

### Data-loss risk

**Low.** Models remain on the same bind. Only container/project metadata changed. No volume delete commands used.

### Rollback

1. Stop/rm `ollama` from `services/ollama`  
2. Restore `/hive/ollama/compose.yml` from `compose.yml.LEGACY-DO-NOT-USE`  
3. `cd /hive/ollama && docker compose up -d ollama`  
4. Do **not** remove `ollama_ollama-net`

---

## 2. Hermes ownership migration

### Current → target

| Item | Before | After |
| --- | --- | --- |
| Compose SoT | `/mnt/monarch/appdata/hermes/compose.yml` | `services/hermes/compose.yaml` |
| Project workdir | `/mnt/monarch/appdata/hermes` | `.../services/hermes` |
| Data bind | `/mnt/monarch/appdata/hermes:/opt/data` | **unchanged** |
| Role | prototype agent | thin execution layer (ADR-0004) |

### File moves / archives (host)

| Path | Action |
| --- | --- |
| `.../hermes/compose.yml` | → `compose.yml.DISABLED-use-services-hermes` |
| `.../hermes/compose.yml.LEGACY-DO-NOT-USE` | backup |
| `.../hermes/README.COMPOSE_OWNERSHIP.md` | ownership notice |
| `config.yaml`, `memories/`, DBs, logs | **not moved** |

### Required repo files (already present / updated)

- `services/hermes/compose.yaml`
- `services/hermes/.env.example`
- `services/hermes/README.md`
- `services/hermes/Versions.md`
- `AI/Hermes/` registration docs

### Data-loss risk

**Low.** Same `/opt/data` bind; no wipe.

### Rollback

1. Stop/rm hermes from `services/hermes`  
2. Restore appdata `compose.yml` from legacy copy  
3. `docker compose -f /mnt/monarch/appdata/hermes/compose.yml up -d`

---

## 3. Open WebUI SoT separation (config only)

No container recreate required for boundary confirmation.

| Check | Result |
| --- | --- |
| Mount | Only `/mnt/monarch/appdata/open-webui` |
| Mounts to `AI/KORA/Memory` or `Knowledge` | None |
| Mounts to Honcho / KORA appdata | None |
| UI `vector_db` | Present under Open WebUI data — classified **application_runtime_data** |

Boundary artifact: `AI/OpenWebUI/Config/sot_boundaries.yaml`

---

## Compose reference validation

```bash
docker compose -f services/ollama/compose.yaml config >/dev/null
docker compose -f services/hermes/compose.yaml config >/dev/null
docker compose -f services/open-webui/compose.yaml config >/dev/null
docker compose -f services/kora/compose.yaml config >/dev/null
```

All validated during preflight.
