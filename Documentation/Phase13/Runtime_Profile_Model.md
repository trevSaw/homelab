# Phase 13.14 — Runtime Profile Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Architecture only (profiles, contracts, observability, state)—no Docker, deploys, or tech selection changes

---

## Objectives

Define how the same KORA architecture operates across hardware capabilities without redesigning Council, Memory, Knowledge, Tools, or identity.

---

## Documents created

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Runtime_Profiles.md` | Solo, Simulated, Distributed, Hybrid profiles |
| `Architecture/ai/Runtime_Contracts.md` | Behavioral contracts for core concerns |
| `Architecture/ai/Runtime_Observability.md` | Tracing/provenance/explainability metadata requirements |
| `Architecture/ai/Runtime_State.md` | Request lifecycle and state ownership |
| `Documentation/Phase13/Runtime_Profile_Model.md` | This report |

---

## Runtime profiles

| Profile | Essence |
| --- | --- |
| **Solo** | Single local LLM; KORA reasons directly; Council conceptual; **current target** |
| **Simulated Council** | Single model; structured multi-member prompting |
| **Distributed Council** | Independent member runtimes under orchestration; KORA remains user face |
| **Hybrid** | Local + remote + specialized services under unchanged architecture |

All profiles share identical observable contracts.

---

## Implementation flexibility

Internals may change (one model vs many; local vs remote) **only if**:

- KORA identity is preserved  
- Context Intelligence path is preserved  
- Separations and governance hold  
- Explainability and provenance remain  

Architecture is not rewritten to fit a profile.

---

## Contract summary

Contracts defined for: Classification, Retrieval, Ranking, Context Assembly, Explainability, Memory Runtime, Knowledge Runtime, Council, Agents, Tools.

Cross-cutting: classify-before-retrieve; selective stores; no silent Memory/Knowledge writes; no ungated Execute; Graphify deferred.

---

## Observability summary

Required conceptual traces for classification, strategy, retrieval, ranking, assembly, Council contributions, response, candidates, and audit—without raw CoT or secrets. Tooling choice deferred.

---

## Remaining limitations

- No production runtime yet  
- No frozen wire schemas (Phase 13.15 concern)  
- Solo is the near-term target; Distributed/Hybrid not mandated  
- Vendor installs still ADR-gated and non-production until later phases  

---

## Phase boundary

**Phase 13** completes the architectural definition of KORA (through 13.14 profiles/contracts; 13.15 may still add production-implementation architecture docs).

**Phase 14** begins production-oriented runtime implementation under these contracts.

---

## Recommendation for Phase 13.15

Define **Production Implementation Architecture**: how Solo (then Simulated) maps to deployable components, sequencing, acceptance vs Phase 12 baseline—still without silently selecting final production stack outside ADR process.
