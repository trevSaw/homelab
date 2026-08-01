# KORA Deployment Topology

**Status:** Canonical logical deployment topology (Phase 13.15)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Logical architecture only. No Docker Compose, Kubernetes, ports, networks, volumes, or runtime configuration in this document.

Companion: `Production_Architecture.md`, `Production_Service_Topology.md`

---

## Purpose

Describe the logical production layout that Phase 14 will implement as Docker Compose services—without specifying implementation mechanics.

---

## Conceptual Flow

```text
User
 ↓
Open WebUI (UI only)
 ↓
KORA Runtime (Solo Stage 1 primary path — Phase 14.1)
 ↓
Classification
 ↓
Context Intelligence
 ↓
Context Assembly
 ↓
Council Runtime
  (Solo today → Simulated tomorrow → Distributed later)
 ↓
Local Ollama (inference)
```

**Phase 14.1 note:** Hermes remains a thin execution layer and is **not** on the Solo primary chat path. Full logical flow including Memory / Knowledge / Tools appears in later stages. Historical blueprint also showed `Open WebUI → Hermes → KORA`; Solo production implements direct `Open WebUI → KORA` per Stage 1 acceptance.

---

## Co-location Guidance (Logical)

| Profile | Typical co-location |
| --- | --- |
| **Solo (initial production)** | Classification + Context Intelligence + Assembly + Council + Explainability inside **KORA Runtime**; Hermes may be thin or tightly coupled; Memory/Knowledge/Tools optional or stubbed until rollout stages |
| **Simulated** | Same co-location; Council fidelity via structured prompting inside Council Runtime / KORA |
| **Distributed** | Council members may separate; Hermes coordinates; KORA remains synthesis/identity |
| **Hybrid** | Any concern may move to remote services if `Runtime_Contracts.md` hold |

Co-location does **not** erase logical boundaries for contracts, observability, or ownership.

---

## Deployment Domains (Logical)

```text
┌────────────── User Edge ──────────────┐
│ Open WebUI                            │
└───────────────────┬───────────────────┘
                    │
┌────────────── AI Core ────────────────┐
│ Hermes · KORA Runtime · Council       │
└───────┬───────────┬───────────┬───────┘
        │           │           │
┌───────▼──┐ ┌──────▼─────┐ ┌───▼────────┐
│ Memory   │ │ Knowledge  │ │ Tools/MCP  │
│ Domain   │ │ Domain     │ │ Domain     │
└──────────┘ └────────────┘ └─────┬──────┘
                                  │
                         External Systems
```

---

## What This Document Does Not Define

- docker-compose.yml / fragments / Dockerfiles  
- Networks, volumes, ports, secrets, env files  
- Traefik labels, host publishing, Phase 12 network attachment details  
- MCP server inventory installation  

Those belong to Phase 14 under Homelab governance and Phase 12 baseline constraints.

---

## Document Map

| Document | Role |
| --- | --- |
| `Deployment_Topology.md` (this file) | Logical layout |
| `Production_Service_Topology.md` | Per-service cards |
| `Production_Architecture.md` | Trust, data, scaling, rollback |
