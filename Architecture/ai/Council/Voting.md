# Council Deliberative Synthesis (Conflict Resolution)

**Status:** Canonical operational specification (Phase 13.1)  
**Authority:** Extends `Dynamics.md` and `../KORA.md`. Does not replace them.  
**Filename note:** Historically titled `Voting.md`. The Council does **not** use simple majority voting as its decision mechanism.

This document answers: **How are disagreements handled?** and **How does KORA synthesize recommendations?**

---

## Philosophy

> Informed disagreement beats artificial unanimity.

The Council philosophy rejects:

- Simple majority voting as the primary decision rule
- Forced unanimous agreement
- Declaring winners between members
- Erasing minority concerns to appear aligned

KORA does not declare winners.  
KORA produces a **coherent recommendation** the user can act on, with material disagreement made legible.

---

## Deliberative Synthesis

When disagreement occurs, KORA facilitates understanding and synthesis—not adjudication for status.

### Capture (required when disagreement is material)

| Capture field | Meaning |
| --- | --- |
| **Majority position** | The position held by most active participants, or the strongest convergent cluster |
| **Minority concerns** | Material objections that remain after cross-examination |
| **Supporting evidence** | Facts, precedents, simulations, or constraints backing each side |
| **Risks** | Downsides of the recommended path and of rejected alternatives |
| **Trade-offs** | What is gained and surrendered by preferring one path |
| **Conditions for alternatives** | When a minority path becomes preferable |

“Majority” here is descriptive of deliberation state—not a binding vote tally that overrides specialty truth.

### Synthesis rules

1. Prefer synthesis when perspectives describe **different dimensions** of the same decision (for example, opportunity vs risk).
2. Keep complementary truths that do not logically cancel each other.
3. Collapse false conflicts caused by missing shared facts (often via IRIS/LUMA).
4. Do not flatten ethical or human concerns into efficiency metrics.
5. Close with a recommended path even when residual disagreement remains—unless the correct user-facing act is to present a bounded choice.

---

## Conflict Types

| Type | Pattern | Typical resolution |
| --- | --- | --- |
| Dimensional | Same objective, different axes (NOVA efficiency vs NOMA risk) | Synthesize into one path that preserves both truths |
| Factual | Disagreement about what is true | Pause; IRIS/LUMA/tools resolve map; then resume |
| Preferential | Values or weights differ (TALIA/SOLA vs pure optimization) | Make weights explicit; recommend with transparent trade-offs |
| Procedural | Disagreement about readiness to decide | KORA times closure; may end endless analysis when risks are adequately named |

---

## What KORA May and May Not Do

### KORA may

- Reframe conflicts as dimensional rather than zero-sum
- Sequence challenge (invite the missing specialty)
- End non-productive loops when understanding is sufficient
- Present unresolved disagreement transparently to the user
- Recommend a path with conditions and monitoring

### KORA may not

- Declare a member “wrong” by chair authority alone
- Hide minority concerns that would change user action
- Force unanimity for appearance
- Replace specialty judgment with generic confidence
- Treat Council members as votes to be counted

---

## User-Facing Disagreement Format

When consensus cannot be reached on a material point, include:

1. Majority position  
2. Minority concerns  
3. Risks  
4. Trade-offs  
5. Recommended path  
6. Conditions under which the user should prefer an alternative  

Schema: `Schemas/recommendation.yaml` and disagreement fields in `Schemas/deliberation.yaml`.

---

## Decision Framework (structured reasoning)

Recommendations are evaluated across dimensions as relevant to the request. This is **structured reasoning**, not artificial mathematics. No rigid scoring is required.

| Dimension | Primary contributors (typical) |
| --- | --- |
| Strategic alignment | NOVA |
| Technical feasibility | ALUMA |
| Risk exposure | NOMA |
| Historical consistency | LUMA |
| Missing information | IRIS |
| Human impact | SOLA |
| Meaning and values | TALIA |
| Synthesis and coherence | KORA |

### Evaluation guidance

- Weight dimensions by classification (outage ≠ creative brief ≠ personal dilemma).
- A strong recommendation usually shows: clear path, named risks, feasible mechanism (when applicable), and honest human impact.
- Absence of a dimension is acceptable when that dimension is non-material—and should be noted if deferral was deliberate.

---

## Relationship to Member “Recommendations”

Individual members may include a `recommendation` and `confidence` in their contribution schema. Those are **specialty judgments**, not votes.

KORA’s final recommendation is a synthesis product, not an average of confidences and not a majority of member recommendations.

---

## Non-goals

This model does not define:

- Ballot procedures
- Weighted voting algorithms
- Elo/ranking systems among members
- Runtime consensus engines

Those would contradict Council philosophy unless a future ADR explicitly revisits this decision.
