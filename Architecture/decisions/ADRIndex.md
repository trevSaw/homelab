# ADR Index

This index lists all Architecture Decision Records (ADRs) stored in the repository.

## ADRs

- [ADR‑001 – Initial Architecture Decision](../Architecture/decisions/ADR-001-Initial-Architecture-Decision.md)
- [ADR‑002 – Service Catalog Structure](../Architecture/decisions/ADR-002-Service-Catalog-Structure.md)
- [ADR‑0003 – Home Assistant Networking](./ADR-0003-Home-Assistant-Networking.md)

### KORA technology evaluation (Phase 13.8)

| ADR | Candidate | Layer | Decision |
| --- | --- | --- | --- |
| [ADR‑0004 – KORA Orchestration (Hermes)](./ADR-0004-KORA-Orchestration-Hermes.md) | Hermes | Orchestration | Provisional Adopt |
| [ADR‑0005 – Memory Runtime (Honcho)](./ADR-0005-Memory-Runtime-Honcho.md) | Honcho | Memory Runtime | Spike |
| [ADR‑0006 – Knowledge Retrieval (ChromaDB)](./ADR-0006-Knowledge-Retrieval-ChromaDB.md) | ChromaDB | Knowledge Runtime | Provisional Adopt |
| [ADR‑0007 – Relationship Layer (Graphify)](./ADR-0007-Relationship-Layer-Graphify.md) | Graphify | Relationship Knowledge | Accepted for Future Implementation (Phase 14.4) |
| [ADR‑0008 – User Interface (Open WebUI)](./ADR-0008-User-Interface-OpenWebUI.md) | Open WebUI | User Interface | Provisional Adopt |

### KORA implementation architecture (Phase 14)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR-14.2A-001 – Internal Event Bus](./ADR-14.2A-001-Internal-Event-Bus.md) | General KORA internal messaging | Approved |
| [ADR-14.2B-001 – Approval-Gated Durable Memory](./ADR-14.2B-001-Approval-Gated-Durable-Memory.md) | Honcho adapter + workflow recovery + API authorization | Approved |

Evaluation method: `Architecture/ai/Implementation_Architecture.md`  
Template: `Architecture/ai/Technology_Evaluation_ADR_Template.md`  
Phase report: `Documentation/Phase13/Technology_Evaluation_ADR_Model.md`  
Vertical slice: `Architecture/ai/Vertical_Slice.md` (Phase 13.9)

No production installs are authorized by Draft/Provisional/Spike ADRs alone.
