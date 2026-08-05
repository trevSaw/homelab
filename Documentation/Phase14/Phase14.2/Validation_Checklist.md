# Phase 14.2 Preflight — Validation Checklist

**Date:** 2026-08-01

## Ownership

- [x] `ollama` workdir = `services/ollama`
- [x] `hermes` workdir = `services/hermes`
- [x] `open-webui` workdir = `services/open-webui`
- [x] `kora` workdir = `services/kora`
- [x] Legacy `/hive/ollama/compose.yml` disabled
- [x] Legacy Hermes appdata `compose.yml` disabled

## Network & dependents

- [x] `ollama_ollama-net` exists
- [x] Dependents attached: ollama, kora, open-webui, hermes, honcho-*, code-server, odysseus
- [x] No `docker network rm` performed

## Data integrity

- [x] Ollama model list count unchanged (18 lines including header)
- [x] Hermes data mount still `/mnt/monarch/appdata/hermes -> /opt/data`
- [x] Hermes `config.yaml` present
- [x] Open WebUI data still `/mnt/monarch/appdata/open-webui`

## Health / ingress

- [x] `ollama` healthy
- [x] `kora` healthy (`ollama: true`)
- [x] `open-webui` healthy; `https://chat.fatherfankscloud.uk/` → 200
- [x] `hermes` healthy; `https://hermes.fatherfankscloud.uk/` → 302 login

## SoT boundaries

- [x] Open WebUI has no mounts into KORA Memory/Knowledge paths
- [x] Boundary file committed: `AI/OpenWebUI/Config/sot_boundaries.yaml`
- [x] Compose comments document forbidden mounts

## Memory writes

- [x] No Honcho durable write feature enabled in this preflight
- [x] Approval UX design published: `Memory_Approval_UX.md`

## Documentation

- [x] Preflight assessment, migration plan, validation checklist, approval UX
- [x] Service README notes updated where needed
