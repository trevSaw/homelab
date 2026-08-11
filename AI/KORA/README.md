# KORA — Homelab AI Conductor (Hermes Agent)

**Status: KORA is now a Hermes Agent. The standalone KORA Runtime is retired.**

Target architecture (Phase 14 final):

```text
Open WebUI → Hermes → KORA HEAD AGENT → Honcho (memory) / Chroma (knowledge)
                                           / Graphify (relationships) / Ollama (inference) / MCP (tools)
```

## Active KORA assets

- **KORA Agent code** (loaded by Hermes v0.17.0):
  `Documentation/Phase14/Phase14-Migration/staging/plugins/kora/`
  (production copy at `/opt/data/plugins/kora` on the Hermes volume).
- **Agent registration:** `Config/hermes_registration.yaml`.
- **System prompt:** `Prompts/solo_system.txt`.

## Retired (standalone runtime)

The old standalone KORA Runtime (`Runtime/`, `Knowledge/`, `Tools/`, their
configs and tests, and `services/kora/`) is **retired from the active
architecture**. It is preserved in Git history (see
`git log` / checkout of any pre-retirement commit) and in the production
backup `PHASE14-KORA-RUNTIME-FINAL-BACKUP-20260810`.

Retirement report:
`Documentation/Phase14/Phase14-Migration/10-kora-runtime-retirement.md`.
