# KORA Explainability Architecture

**Status:** Canonical explainability specification (Phase 13.6)  
**Companions:** `User_Experience.md`, `Interaction_Model.md`, `Context_Assembly.md`  
**Platform:** `KORA.md`

Defines how KORA communicates **why**—without exposing raw chain-of-thought.

---

## Principle

Explainability is structured accountability:

- evidence
- contributors
- reasoning factors
- confidence
- trade-offs
- provenance

Explainability is **not**:

- dumping private internal monologue
- revealing hidden chain-of-thought traces
- performing transparency theater without substance

---

## User Questions to Support

KORA must support asks like:

- “Why did you recommend this?”
- “What did you consult?”
- “Who in the Council weighed in?”
- “What tools did you check?”
- “How sure are you?”
- “What else did you consider?”
- “What are you unsure about?”

---

## Explanation Object (Conceptual)

A recommendation explanation should be able to present:

| Field | Meaning |
| --- | --- |
| **Recommendation** | The advised path or answer |
| **Summary rationale** | Plain-language why |
| **Contributors** | Council members who materially participated (if any) |
| **Reasoning factors** | Specialty considerations (strategy, risk, feasibility, …) |
| **Evidence used** | Knowledge / Memory / Tool / Agent result references |
| **Provenance** | Source labels, authority/freshness where applicable |
| **Confidence** | Honest certainty band |
| **Trade-offs** | What is gained/surrendered |
| **Alternatives** | Other options and when preferable |
| **Remaining concerns** | Material unresolved issues |
| **Assumptions** | Explicit givens |
| **Uncertainty / gaps** | What is missing (“I need more information”) |
| **Approvals needed** | If action requires Execute/Administrative gates |

---

## Example (Illustrative)

**Recommendation:** Use approach A.

**Considerations:**

- **NOVA:** Strategic impact
- **ALUMA:** Engineering feasibility
- **NOMA:** Risk analysis
- **LUMA:** Previous decisions

**Confidence:** High

**Remaining concerns:** Cost and complexity

(Actual explanations should attach provenance to evidence items when available.)

---

## What May Be Exposed

| Allowed | Notes |
| --- | --- |
| Council participation set | Who was invited/deferred at summary level |
| Specialty factor summaries | Not member-impersonating transcripts by default |
| Evidence list with provenance | Knowledge/Memory/Tool/Agent |
| Confidence and dissent | Per Voting/Deliberation synthesis rules |
| Tool capabilities consulted | What was checked, when |
| Assumptions and gaps | Explicit |

### Full Council Mode additions

When user requests Full Council visibility, richer contribution summaries may be shown—still as structured factors, not raw private CoT.

---

## What Must Not Be Exposed

| Forbidden | Why |
| --- | --- |
| Raw chain-of-thought | Private internal traces; unstable and misleading as UX |
| Secret values / credentials | Safety |
| Hidden prompts / system instructions wholesale | Security and noise |
| Fake precision scores pretending to be science | Undermines trust |
| Silent omission of material minority concerns | Violates Dynamics |

---

## Mapping to Architecture Layers

| Layer | Explainability contribution |
| --- | --- |
| **Council** | Contributors, factors, dissent, synthesis |
| **Knowledge** | Sources, authority, freshness |
| **Memory** | Continuity items used (and that they are memories) |
| **Tools** | Live evidence consulted |
| **Agents** | Tasks run, results returned, scope |
| **Context Assembly** | Provenance labels preserved into explanations |

---

## Confidence Communication

Confidence is honesty, not authority:

- High: strong evidence + low material dissent for this decision class
- Medium: usable recommendation with named gaps/trade-offs
- Low: provisional; prefer gathering more information

Never equate confidence with “Council voted.”

---

## Non-goals

- Implementing explanation UIs
- Logging raw model token streams to users
- Selecting observability vendors
