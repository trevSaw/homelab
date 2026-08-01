# KORA User Experience Architecture

**Status:** Canonical UX architecture specification (Phase 13.6)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Interaction_Model.md`, `Explainability.md`

This document defines **what it should feel like to work with KORA** and the UX contract future interfaces must satisfy.  
It does **not** select UI frameworks, apps, or vendors.

---

## UX Philosophy

KORA is not a magic chatbot.

Working with KORA should feel like collaborating with a governed intelligence that:

- understands the request
- grounds answers in Memory, Knowledge, and live Tool evidence
- reasons through the Council when judgment is required
- can delegate scoped work to Agents
- explains recommendations without dumping private chain-of-thought
- respects user control over personal Memory
- requires approval for high-impact actions

The product identity is **KORA**. Interfaces are windows into KORA—not separate assistant brands.

---

## Interaction Principles

1. **Clarity over theater** — Prefer understandable answers over impressive opacity.
2. **Provenance over mystique** — Users can learn where information came from.
3. **Judgment over automation-by-default** — Execution/Administrative actions stay gated.
4. **Minimum sufficient process** — Invisible Council when appropriate; deeper visibility on request or high stakes.
5. **User control of personal continuity** — Memory is inspectable, correctable, deletable.
6. **Honest uncertainty** — Confidence, trade-offs, and “I need more information” are first-class.
7. **No Council/Agent conflation in UX** — Do not present members as workers or agents as advisors.
8. **Technology-agnostic contract** — UX requirements outlive any specific client.

---

## User Relationship Model

| Role | Relationship to KORA |
| --- | --- |
| **Primary user** | Converses with KORA; owns personal Memory; approves high-impact actions |
| **Operator / admin** | May manage tool permissions, project scopes, and governance settings (future) |
| **Observer** | May receive notifications/summaries without full control (future)

KORA serves the requester as highest priority (Council Dynamics). The UX must not bury the user’s goal under internal ceremony.

---

## Trust Model

Trust is earned by consistent behavior:

| Trust builder | UX implication |
| --- | --- |
| Correct provenance | Label memory / knowledge / tool / agent sources |
| Transparent dissent | Show material minority concerns when they change action |
| Bounded autonomy | Clear when KORA only advises vs when action needs approval |
| Controllable memory | User can see/fix/delete personal memories |
| Stable identity | KORA remains KORA across surfaces |

Trust breakers to avoid:

- Silent Knowledge promotion from chat or tools
- Fake certainty
- Hidden high-impact execution
- Presenting Council members as interchangeable bots

---

## Transparency Model

Transparency levels align with Council visibility modes (`Interaction_Model.md` / Council UX section below):

| Mode | User sees |
| --- | --- |
| **Invisible** | Natural KORA answer; deeper explainability available on demand |
| **Advisory** | KORA notes key contributors/evidence factors |
| **Full Council** | Explicit deliberation visibility the user requested |

Transparency always available via explainability asks (“Why did you recommend this?”)—see `Explainability.md`.

---

## Primary Interaction Surfaces (Future)

Support conceptually—not as product picks:

| Surface | Intent |
| --- | --- |
| **Chat** | Primary conversational interface |
| **Voice** | Hands-free / ambient interaction |
| **Desktop** | Deep work, projects, reviews |
| **Mobile** | Quick asks, approvals, notifications |
| **Notifications** | Proactive alerts within governance |
| **Proactive communication** | KORA-initiated updates when warranted and permitted |

No specific applications or frameworks are selected.

---

## Interaction Pattern Families

Detailed flows: `Interaction_Model.md`.

| Pattern | User intent |
| --- | --- |
| Conversational | Ask, clarify, continue dialogue |
| Project | Work inside a first-class project context |
| Task | Track/approve/execute bounded work |
| Research | Gather and organize information |
| Decision support | Trade-offs, recommendations, alternatives |
| Automation | Approved repetitive/operational actions |
| Notification | Receive timely governed updates |

---

## Memory Interaction (UX)

Users should be able to:

- View remembered information
- Correct memories
- Delete memories
- Approve important memories when confirmation is required
- Understand why something was remembered

Example:

> “KORA, what do you remember about my homelab?”

Governing rules: `Memory_Runtime.md` (user controls personal memory).

---

## Knowledge Exploration (UX)

Users should be able to:

- Search knowledge
- Browse collections/domains
- Inspect relationships (conceptual graph)
- See provenance, confidence, source authority, freshness
- Access historical/superseded context when asking historical questions

Example:

> “Show me everything related to Traefik.”

Governing rules: `Knowledge.md`, `Knowledge_Runtime.md`.

---

## Council Visibility Modes

### Invisible Mode

KORA handles Council internally and responds naturally.

- **Advantages:** natural assistant experience
- **Disadvantages:** less immediate transparency
- **Appropriate when:** low-stakes Q&A; user prefers speed; explainability remains on-demand

### Advisory Mode

KORA explains key consultation, for example:

> “I consulted ALUMA and NOMA.”

- **Advantages:** trust, education, transparency
- **Disadvantages:** slightly more verbose
- **Appropriate when:** non-trivial recommendations; user learning the system; medium stakes

### Full Council Mode

User explicitly requests:

> “Ask the Council.”

- **Advantages:** maximum visibility
- **Disadvantages:** more complex interaction
- **Appropriate when:** high stakes; user requests it; unresolved dissent is material; educational walkthrough

Default: start Invisible or Advisory by preference; escalate visibility with stakes or user request. Never invent Full Council ceremony for simple facts.

---

## Project Awareness (UX)

Projects are first-class concepts.

A project may contain:

- Documentation
- Repositories
- Decisions
- Services
- History
- Current state
- Future plans

Example project: **Homelab** — Docker infrastructure, ADRs, service catalog, architecture docs, roadmap.

Users should be able to:

- Set/switch project context
- Ask project-scoped questions
- Review project decisions and open items
- Distinguish project Memory from global User Memory

---

## Task and Action Management (UX)

Future interaction patterns for:

- Tasks
- Approvals
- Execution requests
- Progress tracking
- History
- Accountability

Example:

> “KORA, continue Phase 13 roadmap.”

Execution/Administrative tool actions require approval UX consistent with `Tools.md` / `Agents.md`.

---

## What the UX Must Expose (Contract)

The UX must make it possible to understand:

| Topic | Exposed as |
| --- | --- |
| Council reasoning model | Modes + explainability |
| Memory governance | View/correct/delete/approve |
| Knowledge provenance | Source, authority, freshness, confidence |
| Tool evidence | Live evidence labels and time |
| Agent boundaries | Task scope, results, termination—not permanent staff |
| Uncertainty | Confidence, gaps, trade-offs |
| Approvals | Clear gates for high-impact actions |

---

## Non-goals

- Choosing React/Flutter/Open WebUI/etc.
- Implementing clients
- Selecting memory/knowledge/UI vendors

---

## Document Map

| Document | Role |
| --- | --- |
| `User_Experience.md` (this file) | UX philosophy and contract |
| `Interaction_Model.md` | User-facing request flows |
| `Explainability.md` | Why/evidence/contributors model |
| `Documentation/Phase13/User_Experience_Model.md` | Phase 13.6 report |
