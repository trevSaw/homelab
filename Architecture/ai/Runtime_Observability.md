# KORA Runtime Observability

**Status:** Canonical observability specification (Phase 13.14)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Observability describes *what must be visible for accountability*. It does **not** select logging vendors, APM products, or storage backends.

Companions: `Runtime_Contracts.md`, `Runtime_State.md`, `Explainability.md`

---

## Purpose

Ensure every runtime profile can prove it followed Phase 13 contracts: classification, selective retrieval, ranking, assembly, Council contribution, and explainability—without exposing raw chain-of-thought.

---

## Principles

1. **Architecture over tooling** — require events/fields; defer ELK/Loki/etc.  
2. **Provenance first** — every evidence item remains attributable  
3. **No CoT dumps** — private monologue is not an audit artifact  
4. **Same events across profiles** — Solo and Distributed emit the same conceptual traces  
5. **Privacy** — never log secrets, tokens, or forbidden personal content  

---

## Required Trace Spans (Conceptual)

| Span / stage | Must record |
| --- | --- |
| **Request received** | Session id; request id; UI substrate (not identity) |
| **Classification** | Label; ambiguity; rationale summary |
| **Retrieval strategy** | Strategy name; budgets; queried stores; skipped stores + reasons |
| **Retrieval** | Per-store query issued or skipped; hit counts; empty-valid flags |
| **Ranking** | Scores/axes for kept items; prune reasons |
| **Context Assembly** | Final evidence refs + source_class; package size class (minimal/expanded) |
| **Council** | Active/deferred members; contribution ids; disagreement flag |
| **Synthesis / response** | Recommendation id; confidence; refusal flag |
| **Memory candidate** | Candidate id; pending approval; **commit=false unless approved** |
| **Knowledge candidate** | Candidate id; not authoritative until governance |
| **Audit close** | Outcome; contract violations if any |

---

## Provenance Logging

Every evidence reference in traces must include:

- `source_class` (`memory` \| `knowledge` \| `tool` \| `agent` \| `user` \| `conversation`)
- `source_ref`
- authority or confidence cue
- freshness cue when known
- retrieval_reason

Anti-laundering: traces that merge classes without labels are defects.

---

## Classification Logs

Must answer:

- What class was chosen?
- Was retrieval blocked until after classification?
- Was clarification preferred?

---

## Retrieval Logs

Must answer:

- Which stores were queried?
- Which were skipped and why?
- Was Graphify excluded?
- Did preference paths keep Knowledge budget at zero?

---

## Explainability Metadata

Observability must be able to reconstruct the user-facing explanation fields:

- classification, strategy, stores queried/skipped
- evidence used
- contributors
- confidence
- conflict/disagreement flags
- pruning notes when material

User explanation remains structured; internal traces may hold denser refs but still **no raw CoT**.

---

## Council Contribution Records

| Field | Meaning |
| --- | --- |
| Member id | Council seat (not agent id) |
| Active / deferred | Selection outcome |
| Contribution ref | Structured contribution handle |
| Profile mode | Solo conceptual / Simulated prompt / Distributed runtime |

Distributed profiles must not log member vendor brands as KORA identity.

---

## Confidence Metrics

Record confidence posture at:

- classification
- retrieval completeness (hits vs gaps)
- synthesis recommendation

Missing Tools → confidence unknown/low for live claims—not invented certainty.

---

## Failure & Boundary Events

Emit explicit events for:

- refused Execute/Administrative
- missing live evidence
- conflict preserved
- attempted Memory write blocked
- attempted Knowledge promotion blocked
- contract violation (should fail the turn)

---

## Retention (Conceptual)

- Prefer short retention for Temporary Context traces  
- Durable audit of governance decisions follows homelab norms  
- Exact retention tech deferred  

---

## Non-goals

- Choosing Prometheus/Grafana/Loki/OpenTelemetry vendors  
- Defining dashboards  
- Production alerting SLOs  

---

## Document Map

| Document | Role |
| --- | --- |
| `Runtime_Observability.md` (this file) | What must be observable |
| `Runtime_Contracts.md` | What must be true |
| `Runtime_State.md` | Where state lives in the lifecycle |
| `Explainability.md` | User-facing subset |
