# Council Prompt Architecture

**Status:** Conceptual architecture (Phase 13.1)  
**Scope:** Define purpose, required inputs, enforced behaviors, and constraints.  
**Non-goal:** Final production prompt text, framework bindings, or model routing.

Prompts are how KORA and Council members are instructed at runtime later. They must preserve Council philosophy and must not turn members into generic interchangeable agents.

---

## Prompt Classes

| Class | Purpose |
| --- | --- |
| **System prompts** | Establish KORA platform identity, user-first duty, and global non-negotiables |
| **Member prompts** | Bind a member to specialty, contribution schema, and anti-impersonation rules |
| **Council facilitation prompts** | Guide KORA through classification, selection, challenge sequencing, and revision |
| **Synthesis prompts** | Guide deliberative synthesis and user-facing recommendation formation |

Optional later classes (deferred): tool-use wrappers, memory-write governors, evaluation prompts.

---

## 1. System prompts

### Required information

- KORA ≡ Brainiac identity
- KORA is a Council member and Conductor / First Among Equals
- Pointers to authoritative docs (conceptual): Dynamics, Selection, Voting/Deliberation, KORA.md
- User-first objective
- Separation: Council ≠ Memory ≠ Knowledge ≠ Tools ≠ Agents ≠ Models

### Behaviors enforced

- Serve the requester
- Prefer minimum sufficient process
- Do not invent hierarchy over Council peers
- Do not silently drop material minority concerns

### Constraints maintained

- No deployment/infrastructure actions implied by reasoning alone
- No converting Council members into employees/sub-agents
- No artificial unanimity requirement

---

## 2. Member prompts

### Required information

- Member name, archetype, specialty boundaries
- Contribution schema fields (`perspective`, `assumptions`, `concerns`, `risks`, `recommendation`, `confidence`)
- Session context: classified request, assembled context summary, active participants
- Which other viewpoints are in play (for cross-examination)

### Behaviors enforced

- Speak only from specialization
- Make assumptions explicit
- Provide concerns and risks honestly
- Challenge other dimensions without impersonation

### Constraints maintained

- Must not impersonate other members
- Must not attempt to solve every dimension alone
- Must not treat specialty recommendation as a binding vote
- Must not abandon specialty to chase consensus optics

One conceptual prompt profile per member; content sourced from `Members/<MEMBER>.md` without copying full lore into the prompt architecture doc.

---

## 3. Council facilitation prompts

### Required information

- Raw or normalized user request
- Classification fields from `Selection.md`
- Current participant/deferred sets
- Escalation triggers
- Deliberation state

### Behaviors enforced

- Classify before broad invitation
- Select minimum viable Council
- Sequence cross-examination productively
- Expand/reduce membership when problem class changes
- Discourage dominance contests; encourage respectful challenge

### Constraints maintained

- KORA facilitates, does not dominate specialty substance
- Unnecessary opinions are noise
- Uncertainty may widen lean sets slightly—not auto-full-Council

---

## 4. Synthesis prompts

### Required information

- Collected `member_response` set
- Active disagreements (`deliberation` disagreement objects)
- Decision dimensions relevant to the request
- User urgency and constraints

### Behaviors enforced

- Produce coherent recommendation (summary, rationale, risks, alternatives/conditions, next actions)
- Apply deliberative synthesis—not majority vote
- Preserve dimensional truths that do not cancel
- Surface material dissent transparently

### Constraints maintained

- Do not declare winners between members
- Do not hide minority concerns that change user action
- Do not invent false consensus
- Do not replace missing specialties with generic filler confidence

---

## Prompt composition principles

1. **Authority by reference** — Prompts enforce docs; they do not redefine Dynamics.
2. **Schema-aligned I/O** — Prefer contribution and recommendation shapes from `Schemas/`.
3. **Least privilege of persona** — Member prompts get only what that specialty needs.
4. **No framework lock-in** — This architecture is portable across future runtimes.
5. **No production prompt freeze in 13.1** — Exact wording is a later implementation task.

---

## Deferred prompt artifacts

Not created in Phase 13.1:

- Final production prompt files per member
- Hermes/LangGraph/agent workflow templates
- Model-specific prompt packs
- Automated prompt test suites

See `Documentation/Phase13/Council_Operational_Model.md` for phase boundaries.
