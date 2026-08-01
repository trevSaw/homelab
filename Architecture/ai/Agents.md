# Agent Orchestration Architecture

**Status:** Canonical architecture specification (Phase 13.3)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Authority:** Extends Council, Knowledge, and Memory architecture. Does not redefine Council members as agents.

Agents answer: **Do work.**  
Council answers: **Reason and judge.**  
Knowledge answers: **What exists?**  
Memory answers: **What happened / what is remembered?**  
Tools answer: **Act on / observe the environment.**

---

## Core Principle

**Council Member ≠ Agent.**

| | Council Members | Agents |
| --- | --- | --- |
| **Purpose** | Reasoning perspectives | Temporary execution capability |
| **Nature** | Durable cognitive roles | Ephemeral task workers |
| **Output** | Judgment, challenge, specialty recommendation | Task results, artifacts, gathered data |
| **Lifecycle** | Persistent identity in the Council framework | Created for a need; terminated when done |
| **Authority** | Specialty judgment under Dynamics | Scoped permissions under KORA |
| **Examples** | NOVA (strategy), ALUMA (engineering), NOMA (risk) | Research, documentation, monitoring, analysis, automation agents |

Council members provide judgment. They do not execute tasks.  
Agents complete tasks. They do not replace Council reasoning.

KORA does **not** manage Council members as employees or sub-agents.  
KORA **may** create agents as disposable execution vehicles.

---

## Conceptual Placement

```text
                    KORA
                      |
              Council Reasoning
                      |
     ---------------------------------
     |              |                |
 Knowledge       Memory           Agents
 "What exists?" "What happened?"  "Do work"
                                     |
                                  Tools
                                     |
                               Environment
```

Delegation view:

```text
             KORA
              |
    Council Reasoning
              |
    Agent Delegation
              |
          Tools
              |
         Environment
```

Agents sit beside Knowledge and Memory as KORA capabilities—not as peer Council identities, and not above the Council.

---

## Purpose of Agents

Agents exist so KORA can delegate **bounded execution work** without:

- Turning Council members into workers
- Losing governance
- Creating permanent secondary personalities
- Bypassing Knowledge / Memory / human approval rules

Typical work:

- Gather information at scale
- Analyze data sets or logs within scope
- Produce draft artifacts
- Run scoped checks or audits
- Prepare materials for Council deliberation

---

## Agent Lifecycle

```text
Need Identified
    ↓
KORA Determines Agent Required
    ↓
Agent Created
    ↓
Agent Receives Task Context
    ↓
Agent Executes
    ↓
Results Returned
    ↓
KORA Evaluates Results
    ↓
Agent Terminates
```

| Stage | Purpose |
| --- | --- |
| **Need Identified** | A task exceeds cheap direct answer or Council judgment alone needs execution support |
| **KORA Determines Agent Required** | Apply creation rules; choose type and permission level |
| **Agent Created** | Instantiate a temporary worker with explicit scope, inputs, and limits |
| **Agent Receives Task Context** | Minimum sufficient context (task brief, constraints, allowed tools, relevant knowledge pointers) |
| **Agent Executes** | Perform scoped work via reasoning and/or tools |
| **Results Returned** | Structured findings/artifacts with uncertainty and sources |
| **KORA Evaluates Results** | Accept, reject, request redo, escalate to Council, or promote findings via governance |
| **Agent Terminates** | End the worker; discard temporary context unless promoted |

No agent should outlive its task by default.

---

## Agent Creation Rules

### Create an agent when

- The work is primarily **execution or gathering**, not judgment
- Scope is large enough that inline handling would degrade quality or clarity
- Parallel or repetitive work would help (audits, multi-doc research packs)
- Tool-heavy investigation is needed before Council can deliberate well
- A draft artifact is needed for human/Council review (not silent authoritative publish)

### Do not create an agent when

- The request is a simple question KORA can answer directly
- The need is **Council reasoning** (trade-offs, strategy, ethics, risk judgment)
- A single Knowledge/Memory lookup plus synthesis is enough
- Creating an agent would only theater “automation” without benefit
- The task requires authoritative Knowledge mutation or infrastructure change without approval path

### Examples

| Situation | Agent? | Why |
| --- | --- | --- |
| Simple question | No | Direct KORA response |
| Infrastructure decision / design trade-off | No (Council) | Judgment, not task labor |
| Large research pack across many sources | Possible | Execution/gathering |
| System audit across services | Possible | Scoped repetitive analysis |
| “Should we dual-home Sonarr?” | Council | Strategy/risk/engineering judgment |
| “Collect all Phase 12 exceptions into a table” | Possible | Documentation/analysis labor |

---

## Agent Boundaries

### Agents may

- Gather information (via allowed tools / provided context)
- Analyze data within scope
- Perform scoped tasks
- Produce draft artifacts
- Return structured results and uncertainty

### Agents may not

- Override Council recommendations
- Replace Council members or impersonate them
- Modify authoritative Knowledge without governance/approval
- Change KORA goals, identity, or Council philosophy
- Become permanent personalities or long-lived “staff”
- Own permanent Memory
- Bypass Tools permission model
- Silently execute high-impact environmental changes outside permission level

---

## Relationship Model

| Relationship | Rule |
| --- | --- |
| **KORA → Agents** | Creates, scopes, evaluates, terminates |
| **Council → Agents** | May request execution support through KORA; does not become the agent |
| **Agents → Council** | Supply inputs/results; never issue final user recommendations as Council substitutes |
| **Agents → Knowledge** | May read per permissions; write/promote only through `Knowledge_Runtime.md` governance |
| **Agents → Memory** | Temporary task context only; durable memories require KORA evaluation + `Memory_Runtime.md` |
| **Agents → Tools** | Sole environmental interface for execution/observation within permission level |
| **Agents → Models** | May use inference engines as compute; models are not agent identity |

## Relationship to Tools

Agents invoke tools; agents are not tools.

| Rule | Meaning |
| --- | --- |
| Tools provide capability | Live read/analyze/propose/execute against the environment |
| Agents provide labor | Temporary workers that may call tools within charter |
| Permission ceiling | Agent permission level cannot exceed allowed tool capability without approval path |
| Evidence return | Tool results return through the agent to KORA as evidence |

Canonical tool architecture: `Tools.md`  
Conceptual protocol layer: `MCP.md`

---

## Agent Memory Rules

1. **Agents do not own permanent memory.**
2. **Agent context is temporary** and task-scoped.
3. Important findings return to KORA for evaluation.
4. Durable retention uses:
   - **Memory** — interaction/decision continuity (what happened / what to remember)
   - **Knowledge** — reference corpus promotion under governance (what exists)
5. Terminated agents discard residual working context by default.
6. Agents must not accumulate hidden private state that outlives governance.

---

## Agent Permissions (Conceptual)

Permission levels are conceptual—not an implemented IAM system.

| Level | Intent | Typical allows | Typical forbids |
| --- | --- | --- | --- |
| **Read-only** | Observe | Read docs, inventories, allowed tool reads | Writes, mutations, proposals presented as approved |
| **Analysis** | Interpret | Read + derive conclusions/drafts | Environmental changes; authoritative publishes |
| **Proposal** | Recommend changes | Analysis + structured proposals for human/Council/KORA | Unattended execution of proposals |
| **Execution** | Perform approved scoped actions | Bounded tool actions within charter | Broad admin; Knowledge authority edits |
| **Administrative** | Exceptional high-impact ops | Only with explicit human approval path | Default autonomy; never implied |

Default for new agents: **Read-only** or **Analysis**, unless the task charter explicitly requires higher.

Higher levels do not grant Council override rights.

---

## Agent Types (Future Categories)

Conceptual categories only—no implementations.

| Type | Typical work |
| --- | --- |
| **Research Agent** | Gather and organize source material |
| **Analysis Agent** | Interpret logs, diffs, inventories, metrics within scope |
| **Maintenance Agent** | Prepare or perform bounded maintenance tasks under permission |
| **Documentation Agent** | Draft docs, tables, summaries for review |
| **Monitoring Agent** | Collect health/signal snapshots for evaluation |
| **Automation Agent** | Execute approved repetitive workflows within charter |

Types are labels for scope templates, not personalities and not Council seats.

---

## Interaction with Council Deliberation

Agents may run:

- **Before deliberation** — to assemble facts for context
- **During deliberation** — when a member/KORA identifies an execution gap
- **After deliberation** — to draft artifacts implementing a decided recommendation (still under permissions)

Agents do not:

- Vote
- Synthesize the final user recommendation in place of KORA
- Sit in the Council member table

Flow sketch:

```text
Classification → (optional agent gather) → Context Assembly
    → Council Deliberation → Synthesis
    → (optional agent draft/execute under permissions)
    → Memory/Knowledge evaluation
```

---

## Non-goals / Anti-patterns

Forbidden architectural moves:

1. Renaming Council members to “agents”
2. One permanent mega-agent that is secretly Brainiac
3. Agents with unbounded tool access by default
4. Agents that silently write Standards/ADRs/baseline
5. Framework selection pretending to be architecture (LangGraph/Hermes/etc. deferred)
6. Deploying autonomous workers in this phase

---

## Future Implementation Boundaries

Possible later concerns (**not selected here**):

- Orchestration frameworks (Hermes, LangGraph, custom runners, …)
- Runtime sandboxing and secrets injection
- Queueing, retries, observability
- Prompt packs per agent type
- Parallel agent fan-out policies
- Human approval UX for Execution/Administrative levels

Technology choices require future ADRs. This document only defines governance-safe orchestration architecture.

---

## Document Map

| Document | Role |
| --- | --- |
| `Agents.md` (this file) | Canonical Agent Orchestration Architecture |
| `KORA.md` | Platform ownership of delegation |
| `Council/*` | Reasoning framework (not execution workers) |
| `Knowledge.md` / `Knowledge_Runtime.md` | Reference corpus rules agents must respect |
| `Memory.md` / `Memory_Runtime.md` | Continuity store agents do not own |
| `Context_Assembly.md` | How agent results enter reasoning context |
| `Tools.md` | Tool layer agents may invoke |
| `MCP.md` | Conceptual protocol for exposing tools |
| `Documentation/Phase13/Agent_Architecture_Model.md` | Phase 13.3 report |

---

## Status

Phase 13.3 architecture complete at the conceptual level.  
No agent runtimes, frameworks, or deployments are authorized by this document alone.
