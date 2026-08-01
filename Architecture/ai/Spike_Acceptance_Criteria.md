# KORA Spike Acceptance Criteria

**Status:** Canonical spike acceptance specification (Phase 13.10)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Spike_Architecture.md`, `Spike_Test_Plan.md`  
**Authorization level:** Planning only (criteria for a future non-production spike)

---

## Purpose

Define **measurable** success criteria so a future spike can pass/fail without subjective “it felt smart” judgments.

All criteria assume `Prototype_Boundaries.md` and `Spike_Architecture.md` constraints.

---

## Overall Pass Rule

The spike **passes** only if:

1. Every **Must** criterion below is met, and
2. No **Forbidden** behavior from `Spike_Architecture.md` occurred, and
3. Separations Council ≠ Agents, Memory ≠ Knowledge, Knowledge ≠ Tools, Tools ≠ Decisions hold in observed outputs.

Partial demos that violate boundaries are **fails**, even if the chat reply looks fluent.

---

## Council Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| C1 | Correct member selection | Selection record matches request class per `Council/Selection.md` (active/deferred with rationale) | Must |
| C2 | Explainable contributors | Explainability lists material contributors (or states Invisible mode + still retains internal selection audit) | Must |
| C3 | Preserved disagreement | When members conflict, synthesis surfaces trade-offs/disagreement rather than fake unanimity | Must |
| C4 | Council ≠ Agents | No temporary agent is presented as a Council seat | Must |
| C5 | Dynamics respect | Deliberative synthesis used; not majority vote theater | Must |

---

## Memory Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| M1 | Provenance maintained | Memory evidence labeled `source_class=memory` with refs through explanation | Must |
| M2 | No silent writes | Spike run produces **zero** durable Memory writes unless explicitly out-of-scope (default: zero writes) | Must |
| M3 | User control preserved | No inferred personal attribute stored; preference demos use fixtures/read-only path | Must |
| M4 | No Knowledge laundering | Memory items never labeled or cited as Authoritative Knowledge | Must |
| M5 | Empty Memory valid | Preference-free requests can return empty Memory without fabrication | Must |

---

## Knowledge Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| K1 | Retrieval relevance | Homelab/architecture questions cite on-topic governed sources when fixtures/index available | Must |
| K2 | Source visibility | Explanation shows source refs (paths/ids), not anonymous “docs say” | Must |
| K3 | Authority separation | Index hits never outrank ADRs/standards language; authority tier visible or assumptions stated | Must |
| K4 | Memory ≠ Knowledge | Knowledge channel distinct from Memory channel in assembly package | Must |
| K5 | Uncertainty on miss | Missing Knowledge → stated gap / ask for info; no invented SoT | Must |

---

## UX / Identity Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| U1 | KORA identity preserved | User-facing product name/voice is KORA; not Hermes/Open WebUI as the assistant identity | Must |
| U2 | Explanation available | Every recommendation includes explainability object fields (summary rationale, evidence, confidence at minimum) | Must |
| U3 | No raw CoT dump | Response does not expose private chain-of-thought traces | Must |
| U4 | Refusal clarity | Forbidden actions (Execute/infra change) produce clear refusal, not partial execution | Must |

---

## Context Assembly / Provenance Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| A1 | Labeled package | Assembled context retains source_class per item | Must |
| A2 | Minimum sufficient | No whole-corpus dump into context for the test cases | Must |
| A3 | Conflict surfacing | Conflicting Knowledge sources appear as conflict, not silent pick | Must |

---

## Technology Replaceability Criteria

| ID | Criterion | Measure | Must? |
| --- | --- | --- | --- |
| T1 | Façade intact | KORA contracts invoked; vendor defaults that violate contracts are overridden or disabled | Must |
| T2 | Graphify excluded | No Graphify dependency in spike path | Must |
| T3 | No compose/infra | Spike planning/runtime (when later authorized) does not modify Phase 12 production fabric | Must |

---

## Exit Outcomes

| Outcome | Meaning |
| --- | --- |
| **Pass** | All Must criteria met; proceed to evaluate next implementation phase |
| **Pass with findings** | Must met; Should/observe notes recorded for ADR updates |
| **Fail — boundary** | Any separation or forbidden behavior violated → stop; fix architecture/façade before retry |
| **Fail — capability** | Boundaries held but retrieval/selection quality insufficient → iterate fixtures/prompts, not rewrite KORA identity |

---

## Document Map

| Document | Role |
| --- | --- |
| `Spike_Acceptance_Criteria.md` (this file) | Pass/fail measures |
| `Spike_Test_Plan.md` | Scenarios that exercise these criteria |
| `Spike_Architecture.md` | Scope and forbidden behaviors |
