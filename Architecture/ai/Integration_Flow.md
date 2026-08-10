# KORA Integration Flow (Conceptual)

**Status:** Canonical integration-flow specification (Phase 13.9)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Vertical_Slice.md`, `Prototype_Boundaries.md`, ADR-0004–0008, ADR-14.2A-001
**Rule:** Describe conceptual interactions. Technology candidates implement layers; they do not redefine ownership.

---

## Purpose

Define how layers interact in the thin vertical slice: what data moves, what must not move, who owns each concern, and how provenance is preserved.

Candidate technologies appear only as **ADR-governed layer mappings**, not as required installs.

## Phase 14.2A transport refinement

ADR-14.2A-001 adopts a general internal Event Bus as KORA's canonical
component-messaging mechanism. The invocation arrows in this Phase 13 document
remain logical ownership flows; implementations carry internal events through
the Event Bus instead of coupling producers directly to consumers.

The bus owns delivery and decoupling only. KORA still owns orchestration and
policy, and each receiving component retains its established responsibility.
The initial adapter is volatile and in-process; service boundaries are
architectural rather than deployment boundaries.

---

## Conceptual Stack

```text
Open WebUI          ← UI Layer candidate (ADR-0008)
    ↓
Hermes              ← Orchestration substrate candidate (ADR-0004)
    ↓
KORA                ← Platform identity / conductor (architecture)
    ↓
Council             ← Reasoning framework (Dynamics)
    ↓
Memory Runtime      ← Continuity (Honcho candidate / ADR-0005)
    ↓
Knowledge Runtime   ← Reference retrieval (ChromaDB candidate / ADR-0006)
    ↓
Tools               ← Live evidence (MCP later; optional in thin slice)
```

**Relationship Knowledge (Graphify / ADR-0007)** is an intentional component scheduled for Phase 14.4 (Knowledge Graph). It remains **out of the default thin-slice path** and is not yet implemented.

Reading tip: arrows mean “invokes / requests,” not “is replaced by.”

---

## Layer Mapping (Candidates vs Architecture)

| Architecture layer | Candidate (ADR) | Owns | Must not own |
| --- | --- | --- | --- |
| User Interface | Open WebUI (0008) | Capture request; render recommendation/explanation | Intelligence, Council, SoT |
| Orchestration | Hermes (0004) | Routing, agent spawn hooks, tool transport | KORA brand; Council rules |
| Conductor / synthesis | **KORA** | Classification, assembly, synthesis, explainability | Vendor product identity |
| Internal messaging | Event Bus (14.2A-001) | Envelope delivery, subscriptions, correlation | Policy, domain decisions, SoT |
| Council | Council docs | Deliberation contributions | Execution; tool authority |
| Memory Runtime | Honcho spike (0005) | Continuity retrieval/governance | Knowledge authority |
| Knowledge Runtime | ChromaDB (0006) | Semantic retrieval index | Document SoT / promotion |
| Relationship Knowledge | Graphify (0007, planned Phase 14.4) | Structural relationships | SoT; Memory |
| Tools | MCP later | Live environment evidence | Decisions |

---

## What Data Moves

| Hop | Data that may move | Form |
| --- | --- | --- |
| UI → Orchestration | User message, session id, UI mode flags | Request envelope |
| Orchestration → KORA | Same envelope + transport metadata | Conductor invocation |
| KORA → Classification/Selection | Request + conversation Temporary Context | Internal KORA process |
| KORA → Event Bus → Memory Runtime | Candidate/retrieval message + governed scope | Serializable event envelope |
| Memory Runtime → Event Bus → KORA | Proposal status or future Memory result | Serializable event envelope |
| KORA → Knowledge Runtime | Retrieval query + filters (authority/freshness) | Knowledge query |
| Knowledge Runtime → KORA | Knowledge hits + provenance/authority/freshness | Knowledge result set (may be empty) |
| KORA → Context Assembly | Request, selection, memory, knowledge, optional tool/agent | Assembled context package |
| KORA → Council | Assembled context + member briefs | Deliberation inputs |
| Council → KORA | Member contributions (structured) | Deliberation outputs |
| KORA → UI | Recommendation + explainability object | Response envelope |
| KORA → Tools (optional) | Scoped read queries only in thin slice | Tool calls |
| Tools → KORA | Evidence payloads + provenance | Tool results |

---

## What Does Not Move

| Must not move | Why |
| --- | --- |
| Raw chain-of-thought / private monologue to UI | Explainability contract |
| Secrets, tokens, private keys | Security / Memory governance |
| Entire corpora into context | Minimum-sufficient assembly |
| Memory records re-labeled as Knowledge | Memory ≠ Knowledge |
| Tool results re-labeled as Authoritative Knowledge by default | Knowledge ≠ Tools |
| Council seats serialized as disposable agents | Council ≠ Agents |
| Unapproved Execute/Administrative commands | Tools ≠ Decisions; prototype boundaries |
| Durable Memory writes without Evaluate/Classify/confirmation | Prototype boundaries |
| Graphify graph as blocking dependency | Graphify planned for Phase 14.4; not implemented |
| UI chat DB as Knowledge SoT | Indexes/UI ≠ authority |
| Hermes/Open WebUI branding as product identity | KORA ≡ Brainiac |

---

## Ownership Boundaries

```text
User owns ....... personal Memory control rights; final accept/reject of advice
UI owns ......... presentation and capture only
Orchestration owns transport/runtime substrate, not policy
KORA owns ....... classification, selection orchestration, assembly, synthesis, explanation
Event Bus owns ... internal envelope delivery and subscriptions, not policy
Council owns .... specialty judgment contributions under Dynamics
Memory Runtime owns continuity artifacts under Memory_Runtime governance
Knowledge Runtime owns retrieval over governed sources; not promotion authority
Repo/ADRs own ... Authoritative Knowledge SoT
Tools own ....... point-in-time evidence only
```

Conflict rule: if a candidate product’s default behavior violates ownership, **our façade wins**. Architecture is not rewritten to fit the tool.

---

## Provenance Preservation

Provenance must survive every hop:

1. **At retrieval:** Memory and Knowledge results include `source_class`, `source_ref`, freshness/confidence/authority as applicable.
2. **At assembly:** Context package retains labels; no silent merge of classes.
3. **At deliberation:** Members see labeled evidence; contributions can cite evidence ids.
4. **At synthesis:** Recommendation claims map to evidence ids or are marked assumptive.
5. **At explainability:** UI receives structured provenance—not unlabeled prose dumps.
6. **On failure:** Partial results keep labels; gaps are explicit.

Anti-laundering rule: concatenation of Memory + Knowledge text without labels is a defect.

---

## Thin-Slice Default Path

For Phase 13.9 validation (and the first allowed spike later):

```text
Open WebUI → Hermes → KORA → Council
                         ↓
                    Event Bus
                 ↙       ↓       ↘
 Memory Runtime (read) Knowledge  Tools (optional)
                  Graphify omitted from thin slice (scheduled Phase 14.4)
```

Write paths (Memory durable store, Knowledge promotion, tool Execute) remain **out of default path**.

---

## Implementation Risk Notes

| Risk | Mitigation in architecture |
| --- | --- |
| UI becomes second brain | ADR-0008 constraints; façade routing |
| Hermes replaces KORA identity | ADR-0004 façade / branding rules |
| Honcho dialectic auto-writes | ADR-0005 spike gates; no ungated durable writes |
| Chroma treated as truth | ADR-0006 non-authority; repo SoT |
| Graphify premature complexity | Graphify planned for Phase 14.4; omit from thin slice |
| Agent/Council confusion | Selection + Agents.md boundaries |

---

## Document Map

| Document | Role |
| --- | --- |
| `Integration_Flow.md` (this file) | Data movement, ownership, provenance across layers |
| `Vertical_Slice.md` | E2E workflow stages |
| `Prototype_Boundaries.md` | Allowed / forbidden proofs |
| `Architecture/decisions/ADR-0004`–`0008` | Technology evaluation decisions |
