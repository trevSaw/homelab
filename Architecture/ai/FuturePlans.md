# Future Plans

Future AI architecture ideas and sequencing for the KORA (Brainiac) platform.

## Anchors (do not regress)

- KORA ≡ Brainiac (single platform identity)
- KORA is a Council member and Conductor / First Among Equals
- `Council/Dynamics.md` remains authoritative for Council behavior
- Separation of Council / Memory / Knowledge / Tools / Agents / Models
- Phase 12 production baseline remains the environmental prerequisite

## Near-term documentation sequence (Phase 13)

| Track | Focus |
| --- | --- |
| 13.0–13.15 | ✅ Complete — architectural definition of KORA |

Authoritative Phase 13 roadmap: `Documentation/Phase13/Phase13_Roadmap.md`.  
Canonical architecture: `KORA.md`.

## Phase 14 — Production Runtime Implementation

| Track | Focus |
| --- | --- |
| 14.1 | Runtime Foundation (KORA + Hermes + Open WebUI + Ollama) | ✅ Complete (2026-08-01) |
| 14.2 preflight | Ownership migration + Memory approval UX design | ✅ Complete (2026-08-01) |
| 14.2A | Event Bus + Memory proposal foundation | ✅ Complete (2026-08-03) |
| 14.2B | Approval integration + durable Memory adapter | ✅ Complete |
| 14.2C | Knowledge Ingestion Foundation | ✅ Complete |
| 14.2D | Production Validation | ✅ Complete |
| 14.3 | Knowledge Platform | Planned |
| 14.4 | Knowledge Graph | Planned |
| 14.5 | Tool Platform | Planned |

Authoritative Phase 14 roadmap: `Documentation/Phase14/Phase14_Roadmap.md`.

**Boundary:** Phase 13 = architecture. Phase 14 = implementation under those
contracts. ADR-14.2A-001 additively refines internal component communication
through the Event Bus without transferring ownership.

## Later

| Track | Focus |
| --- | --- |
| Phase 15 | Council & Intelligence (hardware-agnostic Council orchestration + Context Intelligence hardening) |
| Phase 16 | Automation & Autonomous Workflows (governed autonomous workflows) |
| Phase 16+ | AI Automation (governance assistant workflows) |

Capability progression: Knowledge Platform → Knowledge Graph → Tool Platform → Council & Intelligence → Automation & Autonomous Workflows.

## Status

Living notes file — prefer updating Phase 13/14 roadmaps for formal scope changes.
