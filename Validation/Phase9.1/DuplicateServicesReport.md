# Phase 9.1 – Duplicate Services Report

## Detected Duplicate (Case‑Insensitive)

| Service Name (as appears) | Repository Paths | Reason |
|---------------------------|------------------|--------|
| **EchoOS / echoos** | `homelab/services/EchoOS/`<br>`homelab/services/echoos/` | Case‑insensitive name collision discovered during Phase 8.5 import. Both compose files were preserved. Manual review required before any refactoring or consolidation. |

## Recommended Action (Phase 9.x)

- **Manual Review Required** – Do not merge, rename, or delete either directory during Phase 9.1.  
- Add this duplicate to the **Risk Register** with severity **High** (potential for deployment confusion and duplicate resource consumption).  
- Resolve during Phase 9.3/9.4 when service refactoring is permitted.

*No modifications to service definitions or compose files have been made.*