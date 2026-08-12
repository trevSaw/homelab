# Phase 14 — KORA Production Runtime Implementation

Phase 14 implements the Phase 13 architecture as a production runtime using Docker Compose under Homelab governance.

> **Closeout (2026-08-11):** Phase 14 final architecture is **complete**. KORA is now a
> **Hermes Agent**; the standalone KORA Runtime and custom Memory Runtime are retired and
> Honcho is the canonical memory backend. See
> [Phase14-Migration/10-kora-runtime-retirement.md](Phase14-Migration/10-kora-runtime-retirement.md)
> and [Phase14_Roadmap.md](Phase14_Roadmap.md).

## Documents

| Document | Purpose |
| --- | --- |
| [Phase14_Roadmap.md](Phase14_Roadmap.md) | Authoritative Phase 14 implementation roadmap (14.1–14.5, then Phase 15 Council & Intelligence, Phase 16 Automation) |
| [Phase14-Migration/](Phase14-Migration/) | Hermes/KORA migration assessment + retirement record |

## Related architecture (Phase 13)

| Path | Purpose |
| --- | --- |
| `Architecture/ai/Production_Architecture.md` | Production blueprint |
| `Architecture/ai/Production_Service_Topology.md` | Logical services |
| `Architecture/ai/Rollout_Strategy.md` | Capability enablement stages |
| `Architecture/ai/Runtime_Profiles.md` | Solo → Hybrid profiles |
| `Architecture/ai/Runtime_Contracts.md` | Behavioral contracts |
| `Documentation/Phase13/Production_Architecture_Model.md` | Phase 13.15 report |
| `Documentation/Phase12.5/Production_Baseline.md` | Production baseline prerequisite |

## Status

**Phase 14:** ✅ Complete (final architecture delivered 2026-08-11)

**Complete:** [14.1 Runtime Foundation](Phase14.1/Runtime_Foundation_Report.md)

**Preflight:** [14.2 Preflight](Phase14.2/README.md) (ownership migration + Memory approval UX design)

**Complete:** [14.2A Memory Runtime Foundation](Phase14.2A/README.md) (Event Bus + ephemeral proposals) — **retired** in final architecture (Honcho is canonical)

**Complete:** [14.2B Approval integration + durable Memory adapter](Phases/Phase14.2B_Closeout.md) — **retired** in final architecture

**Complete:** [14.2C Knowledge Ingestion Foundation](Phase14.2C/README.md)

**Complete:** [14.2D Production Validation](Phase14.2D/README.md)

**Complete:** [14.3 Knowledge Platform](Phase14.3/README.md) — knowledge now external via Chroma

**Complete:** [14.4 Knowledge Graph](Phase14.4/README.md) — Graphify external service

**Complete:** [14.5 Tool Platform](Phase14.5/README.md) — tools via Hermes runtime

**Next:** Phase 15 — Council & Intelligence (definitions preserved; not yet implemented)
