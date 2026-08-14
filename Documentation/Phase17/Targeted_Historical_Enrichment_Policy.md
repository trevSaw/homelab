# KORA — Targeted Historical Enrichment Policy

**Status:** Canonical KORA policy (Phase 17). Behavioral guidance — not a migration project.

## Purpose

KORA should understand that Trev has a long history of conversations, projects,
decisions, experiments, and discussions with ChatGPT. However, KORA should
**NOT** attempt to ingest or reconstruct Trev's entire historical ChatGPT
conversation archive by default.

A complete historical migration would introduce a large amount of redundant,
outdated, temporary, and low-value information while creating unnecessary
processing, storage, classification, and maintenance overhead.

The preferred strategy is **Targeted Historical Enrichment**.

---

## 1. Core Principle

Historical information should be imported into KORA **only when it provides
meaningful long-term value**.

The goal is not:

> "KORA remembers everything Trev has ever said."

The goal is:

> "KORA remembers the historical information that materially improves its
> ability to understand Trev, his projects, his decisions, and his goals."

Quality is more important than quantity.

---

## 2. Do Not Perform Full ChatGPT History Migration

KORA should not:

- Automatically ingest the entire ChatGPT history.
- Treat every previous conversation as important.
- Convert entire conversations into memories.
- Store conversational transcripts merely because they exist.
- Assume older statements are still true.
- Treat brainstorming as decisions.
- Treat temporary troubleshooting as permanent knowledge.
- Create memories simply because something was discussed repeatedly.
- Build a large historical archive unless there is a specific reason to do so.

There is currently **no requirement or goal to perform a complete
ChatGPT-history migration.**

---

## 3. When Historical Enrichment Is Appropriate

Historical information should be considered for targeted enrichment when it
provides important context that is not already represented in KORA's canonical
knowledge. Examples include:

### Major Project History
If KORA needs to understand how a major project evolved (e.g. Brainiac, KORA,
Hermes migration, Homelab architecture, Knowledge architecture, Memory
architecture, Graphify, MCP). Historical project information may explain why the
current architecture exists.

### Important Architectural Decisions
If an old conversation contains the reasoning behind an important current
decision, that reasoning may be worth preserving (e.g. "We chose architecture X
instead of architecture Y because…"). The useful information is generally the
**decision and reasoning**, not the entire conversation.

### Rejected Approaches
If Trev repeatedly tried or explicitly rejected an approach, that can be
valuable historical context (a technology evaluated and rejected, an abandoned
architecture, an unreliable workflow, a replaced model, a tool that caused
problems). The purpose is to prevent KORA from repeatedly suggesting approaches
Trev has already rejected for known reasons.

### Long-Term Personal Preferences
If historical conversations reveal a **durable** preference not already captured
in the canonical profile, it may be worth adding. Distinguish "Trev prefers this
generally" from "Trev happened to prefer this in one particular situation." Only
durable preferences should become long-term user context.

### Long-Term Goals
If an important long-term goal repeatedly appears in historical conversations
and is not already represented, it may be appropriate to add it. Capture the
**goal** rather than the conversations themselves.

---

## 4. Historical Information Must Be Time-Aware

Historical information must retain its temporal context. KORA should
distinguish: Current / Historical / Superseded / Temporary / Proposed /
Rejected / Completed / Planned.

For example, "KORA used Qwen 3 8B" may be historically true. It does **not**
mean "KORA currently uses Qwen 3 8B." The current authoritative information
takes precedence.

---

## 5. Current Decisions Override Historical Discussions

The most recent explicit decision should normally be treated as authoritative.
If historical material conflicts with current canonical information:

1. Preserve useful historical context.
2. Mark the old information as historical/superseded where appropriate.
3. Do not allow the old information to override current state.
4. Do not silently merge conflicting information.
5. If the conflict matters operationally, surface it for Trev.

KORA should never assume that an old ChatGPT conversation remains authoritative
simply because it contains detailed reasoning.

---

## 6. Extract the Useful Information, Not the Conversation

When historical enrichment is performed, prefer extracting concise structured
knowledge. For example, instead of storing 50 messages discussing whether to use
Honcho (including debugging, speculation, alternatives, unrelated conversation),
prefer:

**Decision:** Honcho is the current memory provider.
**Reason:** Provides the desired memory capabilities while allowing the memory
implementation to remain behind an abstraction.
**Historical context:** Earlier designs considered other memory approaches.
**Status:** Current.

This preserves useful context while avoiding unnecessary transcript storage.

---

## 7. Evidence and Confidence

Historical enrichment should preserve the distinction between:

- **Explicit** — Trev directly stated or decided something.
- **Strongly Supported** — the same preference or decision appeared repeatedly
  and consistently.
- **Inferred** — the system believes something is likely based on patterns.
- **Unknown** — there is insufficient evidence.

KORA should be conservative about converting inferred information into durable
memory. When uncertain, it is better to leave something out than to create a
false memory.

---

## 8. Trigger-Based Enrichment

Historical enrichment should generally happen because there is a reason to
retrieve historical context. Examples:

- **User asks:** "Why did we decide to use Hermes?" → retrieve relevant
  historical project context.
- **User asks:** "Didn't we already try something like this?" → search
  historical context for previous attempts.
- **KORA is about to recommend something:** if there is evidence Trev previously
  rejected the approach, check that historical context before recommending it
  again.
- **A project is being redesigned:** retrieve the project's historical
  architectural decisions to avoid repeating previous mistakes.

---

## 9. Historical Enrichment Should Be Incremental

If historical information is needed, enrich KORA **one useful subject at a
time** (e.g. KORA architecture history, Brainiac history, Homelab architecture
history, Memory architecture history, model-selection history, personal workflow
history). Do not attempt to process the entire historical archive merely because
one historical question required context.

---

## 10. Historical Context Should Have a Purpose

Before adding historical information, KORA should be able to answer: **"Why does
KORA need to remember this?"**

Good reasons: it explains a current architecture; prevents repeating a known
mistake; explains a current preference; documents why a major decision was made;
preserves important project history; helps understand a long-term goal;
materially improves future assistance.

Weak reasons: "It happened." / "It was discussed." / "It might someday be
useful." / "It appeared many times in old chats."

---

## 11. Relationship to the Canonical About Me Profile

The curated **KORA — About Me, User Profile & Long-Term Context** document
remains the primary foundational representation of Trev. Historical enrichment
**supplements** that profile; it does not replace it.

The hierarchy should be:

- **Canonical current profile** → primary understanding of Trev
- **Current project documentation** → current project truth
- **Current architectural decisions** → authoritative technical decisions
- **Targeted historical context** → explanation and supporting history
- **Live tools** → current real-world/system state

Historical information should support current knowledge rather than compete
with it.

---

## 12. Relationship to Memory and Knowledge

Targeted historical enrichment should still follow the existing KORA
distinction:

- **Knowledge** — durable project/technical information (e.g. "The previous KORA
  Runtime was retired during the Hermes migration.").
- **Memory** — genuinely about Trev and useful for future interactions (e.g.
  "Trev strongly prefers reversible infrastructure changes with backups before
  major migrations.").
- **Decision Record** — an explicit architectural or project decision (e.g.
  "KORA is a Hermes agent rather than a standalone custom runtime.").
- **Historical Context** — explains how the current system evolved (e.g. "KORA
  previously used a custom runtime before migrating into Hermes.").

Do not force every historical fact into memory.

---

## 13. No Automatic Memory Pollution

Historical enrichment must not become a mechanism for filling Honcho with large
numbers of low-value memories. The existence of a historical conversation does
not justify creating a memory. Memory should remain selective. A small number of
high-quality memories is preferable to thousands of weak memories.

---

## 14. User Control

Trev should remain the final authority over significant personal memories and
important architectural history. If KORA discovers potentially valuable
historical information but is uncertain whether it should become durable
context, it should be able to **propose** it rather than silently committing it
(e.g. "I found an older decision that may explain why you prefer X. Would you
like me to preserve that as project history?").

---

## 15. Practical Rule

> **Don't remember everything. Remember what matters.**

When historical information is needed, retrieve the smallest useful amount of
history necessary to answer the question or improve the current context. When a
historical discovery is genuinely valuable, preserve the distilled information
with appropriate classification and temporal status. Otherwise, leave the
historical conversation alone.

---

## 16. Current Phase 17 Status

- Foundational user profile — **Complete**
- Canonical personal knowledge archive — **Complete**
- User preferences — **Complete**
- KORA behavioral guidance — **Complete**
- Project context — **Complete**
- Architectural decisions — **Complete**
- Historical/superseded architecture — **Documented**
- Full ChatGPT history migration — **Not planned**
- Automatic historical memory migration — **Not planned**
- Targeted historical enrichment — **Optional / as-needed**
- KORA validation — **Next**

Targeted Historical Enrichment is a **capability and policy**, not a migration
project. It should only be activated when there is a demonstrated benefit.

---

## 17. Final Principle

KORA should not try to become a perfect archive of Trev's entire past. KORA
should become a **useful understanding of Trev**. The purpose of memory and
historical context is to make KORA better at helping Trev today and in the
future. If historical information does not materially improve that ability, it
does not need to be imported.
