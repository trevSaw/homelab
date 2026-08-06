# SoT Boundary Verification — Phase 14.2 Preflight

## Open WebUI mounts

Only:

`/mnt/monarch/appdata/open-webui -> /app/backend/data`

Contents include UI-local `webui.db`, `vector_db`, `uploads`, `cache`.

## Conflict scan

No mounts to:

- `AI/KORA/Memory`
- `AI/KORA/Knowledge`
- `/mnt/monarch/appdata/honcho`
- `/mnt/monarch/appdata/kora` (as UI RAG)

## Classification

| Path | Classification |
| --- | --- |
| `/mnt/monarch/appdata/open-webui` | Application runtime data (not KORA SoT) |
| `AI/KORA/Memory` | KORA Memory skeleton (Phase 14.2+) |
| `AI/KORA/Knowledge` | KORA Knowledge skeleton (Phase 14.3+) |
| Honcho volumes | Memory candidate backend (writes gated; not enabled in preflight) |

Boundary config: `AI/OpenWebUI/Config/sot_boundaries.yaml`
