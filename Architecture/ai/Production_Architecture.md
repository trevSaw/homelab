# KORA Production Architecture

**Status:** Canonical production-implementation architecture (Phase 13.15)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** This is a deployment **blueprint**, not a deployment. Phase 14 implements it (e.g. as Docker Compose). Phase 13.15 does not create compose, networks, volumes, ports, or secrets.

Companions: `Deployment_Topology.md`, `Production_Service_Topology.md`, `Rollout_Strategy.md`, `Operational_Readiness.md`, `Runtime_Profiles.md`, `Runtime_Contracts.md`

---

## Purpose

Translate completed Phase 13 architecture into a production implementation blueprint that:

1. Preserves all Phase 13 contracts and separations  
2. Targets **Solo Runtime** first  
3. Remains compatible with Simulated → Distributed → Hybrid profiles  
4. Treats Docker Compose as the planned Phase 14 substrate—not an architectural concern here  

---

## Production Runtime Topology (Logical)

```text
                    ┌─────────────────────┐
                    │   Trust: User Edge  │
                    │  Open WebUI (UI)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Trust: Orchestration│
                    │ Hermes (substrate)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Trust: KORA Core    │
                    │ KORA Runtime        │
                    │  · Classification   │
                    │  · Context Intel.   │
                    │  · Assembly         │
                    │  · Explainability   │
                    │  · Council Runtime  │
                    └─────┬─────┬─────┬───┘
                          │     │     │
              ┌───────────▼─┐ ┌─▼───────────┐ ┌─▼────────────┐
              │ Memory      │ │ Knowledge   │ │ Tool Runtime │
              │ Runtime     │ │ Runtime     │ │ + MCP Gateway│
              └─────────────┘ └─────────────┘ └──────┬───────┘
                                                     │
                                            ┌────────▼────────┐
                                            │ External Systems│
                                            │ (homelab / MCP) │
                                            └─────────────────┘
```

Relationship Runtime (Graphify) remains **optional / deferred** until ADR-0007 changes.

Logical services may co-locate in Solo (one KORA process) or separate later; **boundaries stay logical even when co-located**.

---

## Service Responsibilities (Summary)

| Domain | Responsibility |
| --- | --- |
| UI | Capture/present; never become KORA identity |
| Orchestration | Route/substrate; never replace Council or identity |
| KORA Core | Classify, retrieve plan, assemble, synthesize, explain |
| Council Runtime | Dynamics contributions (conceptual → simulated → distributed) |
| Memory | Continuity under Memory_Runtime governance |
| Knowledge | Retrieval under Knowledge_Runtime; not SoT |
| Tools / MCP | Live evidence; Execute gated |
| Relationship | Optional graph; never SoT |

Full service cards: `Production_Service_Topology.md`.

---

## Runtime Boundaries

| Boundary | Rule |
| --- | --- |
| UI ↔ Orchestration | UI calls façade; no bypass to models as “the brain” |
| Orchestration ↔ KORA | Substrate invokes KORA contracts |
| KORA ↔ Memory/Knowledge | Strategy-gated retrieval only |
| KORA ↔ Tools | Evidence ≠ decisions |
| Council ↔ Agents | Members ≠ temporary workers |
| Indexes ↔ SoT | Chroma/Graphify never outrank repo/ADRs |

---

## Deployment Domains

| Domain | Contains | Phase 14 note |
| --- | --- | --- |
| **Edge / UI** | Open WebUI | Behind homelab ingress norms (Traefik etc.)—configured in Phase 14 |
| **AI Core** | Hermes, KORA Runtime, Council Runtime | Primary KORA stack |
| **State Stores** | Memory Runtime, Knowledge Runtime | Persistent data ownership explicit |
| **Integration** | Tool Runtime, MCP Gateway | Least privilege; no Phase 12 regression |
| **Optional** | Relationship Runtime | Deferred |

Exact networks/volumes are Phase 14 implementation details.

---

## Trust Boundaries

| Zone | Trust assumption |
| --- | --- |
| User Edge | Authenticated users; untrusted content in prompts |
| AI Core | Trusted to enforce contracts; still must not hold unchecked Execute rights |
| State Stores | Hold Memory/Knowledge candidates—secrets forbidden |
| Integration | Highest blast radius; Read default; Execute approval-gated |
| External Systems | Untrusted/variable; evidence only |

---

## Data Ownership

| Data class | Owner | Durable? |
| --- | --- | --- |
| User-facing identity / synthesis | KORA | Policy in docs |
| Session Temporary Context | KORA / UI session | Ephemeral |
| Approved User/Project Memory | Memory Runtime | Yes, governed |
| Knowledge index | Knowledge Runtime | Rebuildable; SoT = repo/ADRs |
| Tool evidence | Tool Runtime | Ephemeral unless audited |
| Audit/traces | Observability (conceptual) | Per retention policy |
| Relationship graph | Optional Relationship Runtime | Rebuildable; not SoT |

---

## Failure Isolation

| Failure | Expected isolation |
| --- | --- |
| UI down | No user access; core idle |
| Orchestration down | UI cannot reach KORA; no silent direct-model fallback that erases identity |
| Memory down | Preference/personal paths degrade; Knowledge/Tools may continue if strategy allows |
| Knowledge down | Architecture paths degrade with gap flags; no invention |
| Tools/MCP down | Operational paths uncertain; no fabrication |
| Council Distributed member down | Fall back toward Simulated/Solo synthesis with explicit degradation |

---

## Upgrade Strategy

1. Upgrade one logical service at a time when separated  
2. Preserve Runtime Contracts across upgrades  
3. Re-run acceptance against Vertical Slice + Context Intelligence scenarios  
4. Prefer rebuildable indexes over opaque lock-in  
5. Never upgrade by rewriting Phase 13 architecture around a vendor release  

---

## Rollback Philosophy

- Production stack must be removable without rewriting KORA docs  
- Indexes disposable if sources remain in git  
- Memory rollback requires export/governance—plan backups in Phase 14  
- Profile rollback: Distributed → Simulated → Solo without identity change  

---

## Horizontal Scaling Model

| Concern | Solo (initial) | Later |
| --- | --- | --- |
| UI | Single instance adequate | Scale replicas behind ingress |
| KORA Core | Single conductor | Scale carefully; session affinity may be needed |
| Memory/Knowledge | Single store each | Scale read replicas only if contracts hold |
| Distributed Council | N/A initially | Scale member runtimes independently |
| Tools/MCP | Least privilege gateways | Scale Read; keep Execute tightly controlled |

Scaling must not collapse trust boundaries or skip Context Intelligence.

---

## Future Distributed Council Compatibility

Production architecture **must not** hard-wire Solo forever:

- Council Runtime is a replaceable realization behind Dynamics  
- Hermes remains orchestration substrate (ADR-0004), not identity  
- Member runtimes may appear later without changing UI identity or Memory/Knowledge contracts  
- Observability events stay the same across profiles (`Runtime_Observability.md`)  

---

## Production Constraints (Explicit)

- KORA remains the product identity  
- Council remains replaceable across profiles  
- Memory ≠ Knowledge; Knowledge ≠ Tools; Council ≠ Agents  
- Graphify optional until adopted  
- Obsidian external only  
- Context Intelligence always precedes retrieval  
- Explainability and provenance preserved  
- Runtime Profiles unchanged; **Solo is initial production target**  
- Docker Compose = Phase 14 substrate, not architecture  

---

## Non-goals (This Phase)

Compose files, Dockerfiles, env files, network/volume/port/secret configuration, MCP server installs, production runtime implementation, ADR decision changes.

---

## Document Map

| Document | Role |
| --- | --- |
| `Production_Architecture.md` (this file) | Production blueprint overview |
| `Deployment_Topology.md` | Logical layout / flow |
| `Production_Service_Topology.md` | Logical services for Phase 14 Compose |
| `Rollout_Strategy.md` | Staged enablement |
| `Operational_Readiness.md` | Ops philosophy |
| `Documentation/Phase13/Production_Architecture_Model.md` | Phase 13.15 report |
