# Phase 14.1 — KORA Runtime Foundation Report

**Status:** Complete  
**Date:** 2026-08-01  
**Stage:** Solo Runtime (Rollout Stage 1)

## Summary

Phase 14.1 delivered the production Solo path foundation:

`User → Open WebUI → KORA Runtime → Local Ollama → Response`

Hermes remains a thin execution layer (ADR-0004). Open WebUI remains UI-only (ADR-0008). Memory, Knowledge, Tools, Council deliberation, and agents are deferred.

## Migration decisions

| Service | Decision |
| --- | --- |
| Ollama | Migrate compose SoT; preserve models; keep running |
| Open WebUI | Migrate + rewire to KORA; preserve chat data |
| Hermes | Refactor compose/docs to thin layer; keep running |
| Honcho | Unchanged until 14.2 |
| KORA | New runtime |

## Validation

See `Validation/Phase14.1/`. Compose config, architecture path, identity, and Execute refusal checks passed. Traefik UI returns HTTP 200.

## Recommendations before Phase 14.2

1. Complete residual Ollama compose project ownership move from `/hive/ollama` → `services/ollama` without dropping `ollama_ollama-net`.
2. Align Hermes live project to `services/hermes`.
3. Confirm Open WebUI built-in RAG/memory features stay disabled for KORA SoT paths.
4. Design approval UX hooks before enabling Honcho durable writes.
