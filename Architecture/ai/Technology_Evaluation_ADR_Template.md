# ADR Template — KORA Technology Evaluation

**Filename:** `ADR-####-short-description.md` (use leading zeros)  
**Use with:** `Architecture/decisions/ADRTemplate.md` required sections  
**Purpose:** Evaluate a technology candidate against KORA Phase 13 architecture without letting the tool redefine KORA.

**Status of candidate under review:** Candidate / Spike / Provisional Adopt / Reject / Defer  

---

## Meta

| Field | Value |
| --- | --- |
| ADR ID | ADR-XXXX |
| Title | |
| Date | |
| Author | |
| Candidate technology | |
| Proposed implementation layer | UI / Orchestration / Memory / Knowledge / Relationship / Tools / Models / Other |
| Related architecture docs | KORA.md, … |

---

## Context

Background, problem statement, and why a technology choice is needed now.

---

## Candidate Summary

What the technology claims to provide, and which KORA layer it would occupy.

---

## Architecture Fit

Does it satisfy:

- [ ] `KORA.md` (KORA identity; not a second brain)
- [ ] Council model (members ≠ agents; synthesis rules)
- [ ] Knowledge model (provenance, authority, freshness)
- [ ] Memory model (user control; Memory ≠ Knowledge)
- [ ] Agents / Tools models (permissions; tools ≠ decisions)
- [ ] UX / Explainability (transparency without raw CoT)

**Architecture fit notes:**

**Deal-breakers found:**

---

## Security

Authn/z, secrets handling, network exposure, blast radius, failure modes.

**Security notes:**

---

## Maintenance

Complexity, operational burden, upgrades, backups, documentation quality.

**Maintenance notes:**

---

## Integration

APIs, interoperability, standards/MCP support, replaceability.

**Integration notes:**

---

## Performance

Homelab-scale adequacy, latency, failure under load.

**Performance notes:**

---

## Migration

Export/import, lock-in risk, exit cost, data ownership.

**Migration notes:**

---

## Community

Stewardship, release cadence, abandonment risk, license.

**Community notes:**

---

## Operational Complexity

Day-2 operations, observability, incident response burden.

**Operational complexity notes:**

---

## Governance

Permissions, auditability, approval workflows, conformance to Phase 12 baseline where relevant.

**Governance notes:**

---

## Alternatives Considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| | | |

---

## Decision

One of:

- **Adopt (provisional)** — constraints and rollback required
- **Defer**
- **Reject**
- **Spike** — time-boxed, non-production limits required

**Decision statement:**

**Constraints / conditions:**

**Rollback plan:**

---

## Consequences

Positive and negative impacts (ops, security, maintenance, UX).

---

## Implementation Notes

Only after decision is Adopt/Spike: practical next steps.  
No Docker/compose/deploy work is authorized by drafting this ADR alone.
