# Context Assembly Architecture

**Status:** Canonical architecture specification (Phase 13.5; Context Intelligence integration Phase 13.12)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Inputs:** `Context_Intelligence.md`, `Retrieval_Strategies.md`, `Context_Ranking.md`, `Memory_Runtime.md`, `Knowledge_Runtime.md`, `Tools.md`, `Agents.md`, `Council/`

Context Assembly is how KORA builds the **reasoning context** for a request.  
It is a KORA responsibility—not a Council member, agent, or tool.

**Upstream:** Classification → **Context Intelligence** (select/filter/rank plan) → selective retrieval → **Context Assembly** (this document).


---

## Purpose

Assemble the minimum sufficient, provenance-labeled context so Council deliberation (and any agent support) is grounded without flooding or laundering sources.

---

## Assembly Model

```text
User Request
Conversation Context
Relevant Memory
Relevant Knowledge
Live Tool Evidence
Council Selection
Agent Results
        =
   KORA Context
```

Relationship view:

```text
             KORA
              |
     Context Intelligence
     (strategy / rank / prune)
              |
      Context Assembly
    /        |        \
Memory   Knowledge   Tools
              |
         Agent Results
              |
      Council Reasoning
```

None of these inputs independently make the final decision. Council reasons; KORA synthesizes.  
Assembly consumes **already strategy-gated and ranked** candidates; it must not re-open ignored stores unless KORA requests expansion.


---

## What Enters Context

| Input | Why it may enter |
| --- | --- |
| **User Request** | Defines objective and constraints |
| **Conversation Context** | Immediate dialogue coherence (Temporary Context) |
| **Relevant Memory** | Continuity: preferences, prior decisions, lessons |
| **Relevant Knowledge** | Reference truth: standards, ADRs, inventories, docs |
| **Live Tool Evidence** | Point-in-time environment facts |
| **Council Selection** | Who is active/deferred and why (process metadata) |
| **Agent Results** | Scoped execution outputs awaiting evaluation |

### What should not enter by default

- Entire corpora
- Raw secret-bearing dumps
- Unrelated project memories
- Deprecated Knowledge marked non-current (unless historical question)
- Agent private scratch beyond returned results

---

## Priority Rules (Conceptual)

When assembling, prefer:

1. **Safety/sensitivity filters** first (never include forbidden content)
2. **User Request + explicit constraints**
3. **Live Tool Evidence** when freshness of environment state matters
4. **Authoritative Knowledge** for standards/baseline/ADR claims
5. **Explicit User Memory** over inferred Memory
6. **Validated Knowledge** over Working/Candidate drafts
7. **Agent Results** when they address an identified gap
8. **Conversation Context** as glue, not as authority

Priority is situational: a personal preference question elevates User Memory; an outage elevates Tools + Operational Memory + relevant Knowledge.

---

## Conflict Handling

| Conflict type | Handling |
| --- | --- |
| Tool vs Knowledge | Surface both; likely freshness issue; do not silently pick |
| Memory vs Knowledge | Memory does not override authoritative Knowledge; may record user preference separately |
| Memory vs Memory | Prefer newer explicit correction |
| Agent result vs Tool | Re-validate with tools if material; treat agent output as mediated evidence |
| Knowledge vs Knowledge | Authority tier + supersession; else dual-cite |

Conflicts become visible context for Council (especially IRIS/LUMA/NOMA as relevant).

---

## Provenance Model

Every important context fragment should answer:

| Question | Example labels |
| --- | --- |
| Where did this come from? | memory / knowledge / tool / agent / user_request / conversation |
| How reliable is it? | confidence / authority tier |
| When was it updated? | timestamp / freshness unknown |
| What kind is it? | preference, standard, live_state, draft, lesson, … |

### Required provenance discipline

- Do not strip source labels during assembly
- Do not relabel Memory as Knowledge
- Do not relabel Tool evidence as durable Knowledge
- Do not present Generated Content as Authoritative without evaluation

---

## Context Limits

Assembly must prefer **minimum sufficient context**:

- Enough for material decision dimensions
- Not so much that signal is drowned
- Expand on demand when Council/KORA identifies missing information
- Re-assemble if selection/problem class changes mid-deliberation

Exact token/byte budgets are implementation concerns—not fixed here.  
Conceptual budgets and pruning rules: `Context_Ranking.md`. Classification-aware store selection: `Retrieval_Strategies.md`.


---

## Governance Hooks

| Rule | Effect on assembly |
| --- | --- |
| Memory ↛ Knowledge silently | Preferences stay Memory-labeled |
| Tool ↛ Knowledge silently | Live state stays tool-labeled |
| Generated content needs evaluation | Drafts labeled candidate/draft |
| User controls personal memory | Honors deletion/correction in retrieval |
| Phase 12 baseline | Authoritative infra claims prefer baseline Knowledge + live tools |

---

## Lifecycle Placement

Within Council deliberation (`Council/Deliberation.md`):

`Classification → Context Intelligence → Selective Retrieval → Context Assembly → Member Selection → …`

Assembly may refresh after agent tool work or mid-session expansion (re-run Intelligence with gap flags).


---

## Explainability Hook

Assembled context with provenance is the substrate for user-facing explanations (`Explainability.md`).  
Do not strip provenance during assembly if explainability must remain honest.

---

## Document Map

| Document | Role |
| --- | --- |
| `Context_Assembly.md` (this file) | How KORA builds reasoning context |
| `Context_Intelligence.md` | Classification-aware select/filter/rank plan (Phase 13.12) |
| `Retrieval_Strategies.md` | Per-class store query policies |
| `Context_Ranking.md` | Ranking, budgets, pruning |
| `Memory_Runtime.md` / `Knowledge_Runtime.md` | Store runtimes feeding assembly |
| `Tools.md` / `Agents.md` | Live evidence and mediated results |
| `Council/Selection.md` / `Deliberation.md` | When/why context is consumed |
| `Documentation/Phase13/Memory_Runtime_Model.md` | Phase 13.5 report |
| `Documentation/Phase13/Context_Intelligence_Model.md` | Phase 13.12 report |
| `Explainability.md` | Consumes provenance-labeled context for user-facing why |
