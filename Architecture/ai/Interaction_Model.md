# KORA Interaction Model

**Status:** Canonical interaction architecture (Phase 13.6)  
**Companion:** `User_Experience.md`, `Explainability.md`  
**Platform:** `KORA.md`

Defines how requests flow from the **user’s perspective**.

```text
User
  ↓
KORA
  ↓
Council / Memory / Knowledge / Agents / Tools
  ↓
Environment
```

No client frameworks are selected.

---

## Shared Request Flow (User-Visible)

1. User expresses intent (chat/voice/other surface).
2. KORA acknowledges understanding (objective, constraints, project context if any).
3. KORA assembles governed context (may be invisible).
4. If judgment is needed, Council participates per visibility mode.
5. If execution/gathering is needed, Agents/Tools may run under permissions.
6. KORA returns recommendation/answer with appropriate transparency.
7. User may ask “why?”, correct Memory, approve actions, or continue.

Internal mechanics remain as defined in Deliberation / Context Assembly / Tools / Agents.

---

## Conversational Interaction

**Intent:** Natural dialogue for questions, clarifications, and iterative problem-solving.

**User experience:**

- Talk to KORA directly (not to named workers by default)
- Follow-ups reuse Temporary Context / relevant Memory
- Invisible or Advisory Council unless escalated

**Examples:**

- “What’s dual-homing mean in our media stack?”
- “Summarize the Sonarr exception.”

---

## Project Interaction

**Intent:** Work inside a first-class project container.

**User experience:**

- Select or confirm project context (e.g., Homelab)
- Questions default to project Knowledge/Memory/Tools scope
- Decisions can be remembered as Project Memory (not auto-Knowledge)

**Examples:**

- “In Homelab, what ADRs affect Traefik?”
- “What did we defer after Phase 12.5?”

---

## Task Interaction

**Intent:** Track bounded work items, approvals, and progress.

**User experience:**

- Create/continue tasks from conversation
- See status, blockers, history, accountability
- Approval prompts for Execute/Administrative actions

**Examples:**

- “KORA, continue Phase 13 roadmap.”
- “Show open tasks for the media networking debt.”

---

## Research Interaction

**Intent:** Gather and organize information without pretending the gatherer is a Council member.

**User experience:**

- KORA may spawn Research/Documentation agents
- Results returned as evidence packs with provenance
- User can promote candidates into Knowledge only via governance UX

**Examples:**

- “Collect all Traefik-related docs and exceptions.”
- “Compare prior outage notes for DNS failures.”

---

## Decision Support Interaction

**Intent:** Trade-offs, recommendations, alternatives, dissent.

**User experience:**

- Clear recommendation
- Key considerations by specialty (Advisory/Full modes)
- Confidence, risks, alternatives, conditions
- Explainability on demand

**Examples:**

- “Should we dual-home Sonarr now?”
- “Ask the Council whether to keep NZBGet on shared VPN netns.”

---

## Automation Interaction

**Intent:** Approved repetitive or operational actions via Agents/Tools.

**User experience:**

- Explicit request or policy-triggered automation
- Permission level visible before Execute/Administrative
- Audit-friendly confirmation and outcome summary
- Never silent destructive action

**Examples:**

- “Draft a restart plan for service X.” (Propose)
- “Restart service X.” (Execute—approval required)

---

## Notification Interaction

**Intent:** Proactive, governed communication.

**User experience:**

- Notifications for watched conditions, task updates, approval needs
- User controls notification scope/intensity (future preference Memory)
- Notifications cite evidence type (tool/memory/knowledge) when actionable

**Examples:**

- “Disk pressure on Monarch crossed threshold.”
- “Approval needed: Administrative tool action queued.”

---

## Council Mode Selection (User Perspective)

| User signal | Typical mode |
| --- | --- |
| Simple factual/doc question | Invisible |
| Non-trivial recommendation | Advisory |
| “Ask the Council” / high stakes / material dissent | Full Council |
| User preference for always-verbose | Advisory default |

KORA may suggest escalating visibility when stakes rise.

---

## Cross-Cutting UX Beats

Every pattern should allow:

- “Why?” → Explainability
- “What do you remember?” → Memory interaction
- “Show sources.” → Knowledge/tool provenance
- “Don’t remember that.” → Memory deletion/correction
- “Do it.” vs “Only advise.” → Action boundary clarity

---

## Non-goals

- Wireframes or visual design systems
- Specific notification vendors
- Workflow engine selection
