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

### Book & audiobook management (Phase 20)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0009 – Book & Audiobook Management (Chaptarr)](./ADR-0009-Books-Audiobooks-Management-Chaptarr.md) | Chaptarr + Audiobookshelf replacing retired Readarr | Draft (pending ARB sign-off) |

### KORA execution worker (Phase 20)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0010 – KORA Execution Worker (OpenCode Task Bridge)](./ADR-0010-KORA-Execution-Worker-OpenCode-Task-Bridge.md) | Async OpenCode execution for KORA with governed boundaries + approval | Superseded by ADR-0011 (Phase 22) |

### Hermes + OpenCode Go (Phase 22)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0011 – Hermes as Agent Harness + OpenCode Go Model Provider](./ADR-0011-KORA-Heavy-Coding-Hermes-Delegation-OpenCode-Go.md) | Hermes delegation for heavy coding; Task Bridge retired | Accepted (Phase 22) |

### KORA controlled administration (Phase 3)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0012 – KORA Controlled Docker Administration](./ADR-0012-KORA-Controlled-Docker-Administration.md) | Narrow `docker-admin` helper for live inspection + controlled restart/deploy; no socket in Hermes | Accepted (Phase 3) |

### KORA transports (Phase 4)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0013 – Discord Native Transport](./ADR-0013-Discord-Native-Transport.md) | Discord as a native Hermes platform (transport only); no custom bridge; KORA authoritative | Accepted (Phase 4) |

### KORA research services (Phase 5)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0014 – SearXNG Internal Research Service](./ADR-0014-SearXNG-Internal-Research-Service.md) | Internal-only metasearch backend for KORA/Hermes; reuses `ollama_ollama-net`; no public exposure | Accepted (Phase 5) |
| [ADR‑0015 – KORA External Web Research via SearXNG](./ADR-0015-KORA-Web-Research-SearXNG.md) | Native Hermes `web` toolset + bundled SearXNG provider; KORA research policy; no custom bridge; `web` on both transports | Accepted (Phase 5) |

### KORA documentation access (Phase 6)

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0016 – KORA Canonical Repository Read/Write Access](./ADR-0016-KORA-Canonical-Repo-RW-Access.md) | RW bind mount of the canonical repo + vault; secrets protected via 600/ACL; no Docker socket; docker-admin unchanged | Accepted (Phase 6) |

### Media acquisition & libraries

| ADR | Scope | Decision |
| --- | --- | --- |
| [ADR‑0017 – Comic Book Management (Kapowarr)](./ADR-0017-Kapowarr-Comic-Management.md) | Kapowarr comic manager writing into the Kavita comics root | Draft (pending ARB sign-off) |
| [ADR‑0018 – Uchiyomi → Kavita Shared Library](./ADR-0018-Uchiyomi-Kavita-Shared-Library.md) | Read-only bind mount of Uchiyomi media into Kavita; Uchiyomi sole writer; mobile offline reading | Accepted (2026-10-08) |

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
