# Council Selection Model

**Status:** Canonical operational specification (Phase 13.1)  
**Authority:** Extends `Dynamics.md` and `../KORA.md`. Does not replace them.  
**Owner:** KORA (Chair / Conductor), as a Council member facilitating process—not as a hierarchy above the Council.

This document answers: **How does KORA decide who participates?**

---

## Purpose

Selection produces the **minimum viable Council**: the smallest set of members whose specialties can produce a strong recommendation for the classified request.

Unnecessary opinions create noise. Full-Council participation is exceptional, not default.

---

## Request Classification

Before inviting members, KORA classifies the request.

### Classification fields

| Field | Question KORA answers |
| --- | --- |
| **Objective** | What outcome does the user need? |
| **Domain** | What subject area(s) does this touch? |
| **Complexity** | How many interacting constraints exist? |
| **Constraints** | What is fixed, forbidden, or non-negotiable? |
| **Time horizon** | Immediate fix, near-term change, or long-term plan? |
| **Risk level** | What happens if the recommendation is wrong? |
| **Required expertise** | Which specialties materially affect the answer? |
| **Missing perspectives** | Which absences would create blind spots? |
| **Unnecessary voices** | Which specialties would add noise without value? |

### Classification outputs

1. Problem class (for example: infrastructure, troubleshooting, personal decision, long-term planning, creative)
2. Candidate invite list
3. Deferred list (with reasons)
4. Escalation triggers (conditions that would add members mid-session)

Classification is part of KORA’s coordination specialty. It is not a substitute for member expertise.

---

## Specialty Map (selection reference)

| Member | Specialty contribution (selection lens) |
| --- | --- |
| KORA | Always present as facilitator/synthesizer; may also contribute coordination judgment |
| NOVA | Strategy, option ranking, path efficiency |
| IRIS | Missing facts, contradictions, discovery |
| TALIA | Meaning, ethics, human interpretation |
| SOLA | Motivation, communication, human reception |
| LUMA | Precedent, prior decisions, historical continuity |
| ALUMA | Engineering, architecture, implementability |
| NOMA | Risk, consequence simulation, logical integrity |

KORA is always in the session as Chair/Conductor. Other members are invited only when their specialty is material.

---

## Member Selection Principles

### 1. Minimum viable Council

Invite only members whose absence would weaken the recommendation on a material dimension.

**Goal:** the smallest group capable of producing a strong recommendation.

### 2. Pair complementary tensions when both dimensions matter

Examples (non-exhaustive):

| If the decision hinges on… | Prefer including… |
| --- | --- |
| Path vs failure mode | NOVA + NOMA |
| Destination vs build path | NOVA + ALUMA |
| Present discovery vs precedent | IRIS + LUMA |
| Conscience vs encouragement | TALIA + SOLA |

### 3. Defer without discarding

Deferred members remain available. Deferral is not exclusion from the Council identity—only from this session’s active set.

### 4. Expand when the problem class changes

Add members when new information reveals a missing material dimension (see Mid-Discussion Revision).

### 5. Full Council is exceptional

Invite the full Council when:

- Multiple domains interact at high stakes
- Irreversibility is high and several specialties are each material
- Prior lean deliberations failed because a deferred dimension proved critical
- The user explicitly requests comprehensive multi-perspective review

### 6. Uncertainty bias

When classification confidence is low:

- Prefer a slightly broader lean set over a dangerously narrow one
- Prefer adding IRIS (missing information) and/or NOMA (downside) before adding non-material voices
- Do not default to full Council solely because of uncertainty

### 7. User-first filter

If a specialty cannot change what the user should do, defer it.

---

## Worked Example — Infrastructure Upgrade

**Request class:** Infrastructure upgrade / architecture change

**Likely participants:**

| Member | Why |
| --- | --- |
| KORA | Classification, facilitation, synthesis |
| ALUMA | Engineering / redesign |
| NOVA | Strategy / option ranking |
| NOMA | Risk / failure domains |
| LUMA | Historical decisions and repeated patterns |

**Deferred unless human impact becomes relevant:**

| Member | Why deferred |
| --- | --- |
| SOLA | Translation/motivation not yet material |
| TALIA | Ethical/meaning framing not yet material |
| IRIS | Add if facts are incomplete or sources conflict |

**Escalation triggers:**

- User comprehension or adoption risk → add SOLA (and possibly TALIA)
- Incomplete or contradictory facts → add IRIS
- Values conflict or dignity/stakeholder harm → add TALIA

This matches Dynamics guidance: networking/infrastructure problems often need NOVA, ALUMA, and NOMA; relationship/human-impact sets differ.

---

## Composition Patterns (normative examples)

| Problem class | Typical lean set | Often deferred |
| --- | --- | --- |
| Infrastructure / networking | KORA, NOVA, ALUMA, NOMA (+ LUMA if precedent matters) | SOLA, TALIA |
| Technical troubleshooting | KORA, IRIS, LUMA, NOMA, ALUMA, NOVA | SOLA, TALIA unless comms/ops human factors matter |
| Personal decision | KORA, TALIA, SOLA, LUMA, NOVA, NOMA | ALUMA unless implementation is central |
| Long-term planning | KORA, LUMA, NOVA, NOMA, ALUMA, TALIA, IRIS | SOLA unless adoption narrative is central |
| Creative brainstorming | KORA, SOLA, IRIS, TALIA, NOVA, ALUMA, LUMA | NOMA unless practical risk is material |

Patterns are defaults, not rigid rosters. Classification overrides pattern.

---

## Mid-Discussion Revision

KORA may revise selection during deliberation.

### Expand when

- A claim depends on missing facts → invite IRIS
- A “new” path may be a repeated failure → invite LUMA
- An optimal path ignores willingness/understanding → invite TALIA and/or SOLA
- Strategy lacks a buildable mechanism → invite ALUMA
- Strategy lacks consequence modeling → invite NOMA
- Options lack ranking/closure → invite or re-engage NOVA

### Reduce when

- A member’s dimension is resolved and further input is noise
- The problem has narrowed to a single remaining specialty question

### Process

1. Name the newly material dimension.
2. Invite or release the corresponding member.
3. Resume from Individual Perspectives or Cross Examination as appropriate.
4. Preserve prior resolved points unless invalidated.

---

## Selection Record (conceptual)

Every session should be able to answer:

- Who was invited and why?
- Who was deferred and why?
- What would trigger expansion?

Schema: `Schemas/request.yaml` (classification + selection fields) and `Schemas/deliberation.yaml` (participants).

---

## Non-goals

Selection does **not**:

- Rank members by authority
- Convert members into generic agents
- Require unanimous invitation
- Optimize for theatrical completeness
- Replace member specialty content with KORA’s generalist answer
