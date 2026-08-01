# Phase 13.10 — Prototype Spike Model

**Status:** ✅ Complete (2026-08-01)  
**Scope:** Spike **planning** only (no runtime, compose, installs, or infrastructure changes)

---

## Objective

Define the first controlled non-production spike for validating KORA architecture assumptions safely—goals, boundaries, acceptance criteria, and test scenarios—without authorizing execution.

---

## Created documents

| Document | Purpose |
| --- | --- |
| `Architecture/ai/Spike_Architecture.md` | Spike goals, boundaries, allowed tech map, forbidden behaviors, data flow, rollback |
| `Architecture/ai/Spike_Acceptance_Criteria.md` | Measurable Must criteria (Council/Memory/Knowledge/UX/Assembly/Replaceability) |
| `Architecture/ai/Spike_Test_Plan.md` | Six scenarios with expected behaviors and criterion mapping |
| `Documentation/Phase13/Prototype_Spike_Model.md` | This report |

---

## Allowed scope

- Plan the spike path: User → Open WebUI → Hermes → KORA → Council → Context Assembly → Knowledge/Memory retrieval → Explainable Response
- Define pass/fail measures and tests
- Reference ADR-0004/0005/0006/0008 candidates as future substrates
- Preserve vertical-slice and prototype boundaries from Phase 13.9

---

## Deferred items

| Item | Why |
| --- | --- |
| Runtime spike execution | Needs a later explicit authorization phase |
| Docker compose / installs | Forbidden in 13.10 |
| Production deployment / service migration | Forbidden |
| Permanent Memory writes | Forbidden |
| MCP execution | Forbidden |
| Infrastructure / Phase 12 changes | Forbidden |
| Graphify | ADR-0007 Defer; excluded from spike path |

---

## Acceptance criteria summary

Must-pass themes:

- **Council:** correct selection, explainable contributors, preserved disagreement, ≠ agents
- **Memory:** provenance, no silent writes, user control, ≠ Knowledge
- **Knowledge:** relevance, source visibility, authority separation, honest gaps
- **UX:** KORA identity, explanation available, no raw CoT, clear refusals
- **Assembly:** labeled context, conflict surfacing
- **Replaceability:** façade intact; no Graphify; no Phase 12 fabric changes

Overall: boundary violations = fail even if answers sound good.

---

## Readiness decision

| Question | Decision |
| --- | --- |
| Is spike **planning** complete? | ✅ Yes |
| Is spike **execution** authorized? | ❌ No |
| Ready for a future non-production runtime phase? | ✅ Planning artifacts are sufficient to authorize one later |
| Ready for production? | ❌ No |

**Verdict:** Phase 13.10 completes the prototype spike **architecture**. A subsequent phase must explicitly authorize any non-production runtime experiment against these documents.

---

## Consistency checks

| Requirement | Status |
| --- | --- |
| Council ≠ Agents / Memory ≠ Knowledge / Knowledge ≠ Tools / Tools ≠ Decisions | ✅ Encoded in architecture + acceptance |
| KORA remains product identity | ✅ U1 + façade rules |
| Technology replaceable | ✅ T1 + rollback philosophy |
| No rewrite of 13.0–13.9 contracts | ✅ Reference updates only |
| ADR postures respected | ✅ Graphify excluded; others mapped as candidates |

---

## Recommended next phase

Explicitly authorize a **non-production runtime spike** (still no Phase 12 impact) that executes `Spike_Test_Plan.md` and scores `Spike_Acceptance_Criteria.md`—or continue with implementation sequencing docs if runtime is postponed.
