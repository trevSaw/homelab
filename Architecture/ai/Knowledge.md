# Knowledge Architecture

**Status:** Canonical architecture specification (Phase 13.2)  
**Runtime companion:** `Knowledge_Runtime.md` (Phase 13.5)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companion:** `Memory.md` / `Memory_Runtime.md` (separate system — do not merge)

Knowledge answers: **What information exists?**  
Memory answers: **What does KORA remember?**

---

## Purpose

Knowledge is the **reference-information subsystem** of KORA. It supplies governed facts, documents, standards, inventories, and curated references that Council deliberation may consume.

### Why KORA requires knowledge

- Council reasoning without reference truth invents plausible but ungrounded answers.
- Homelab decisions must respect repository standards, production baseline, and documented architecture.
- Specialized members (especially IRIS, LUMA, ALUMA, NOMA) need shared source material—not private folklore.
- Users deserve recommendations that can cite what exists, not only what was said in a prior chat.

### How knowledge improves Council reasoning

| Without knowledge | With knowledge |
| --- | --- |
| Strategy floats free of constraints | NOVA ranks options against documented limits |
| Discovery guesses | IRIS compares claims to sources |
| Engineering redesigns from memory alone | ALUMA builds against current architecture docs |
| “History” becomes anecdote | LUMA checks recorded decisions and precedents |
| Risk ignores known failure modes | NOMA reads documented exceptions and debt |

### Boundaries: Knowledge vs Memory vs Tools

| System | Question | Examples |
| --- | --- | --- |
| **Knowledge** | What information exists? | Docs, standards, ADRs, manuals, inventories, curated references |
| **Memory** | What does KORA remember? | Conversations, decisions made with the user, preferences, lessons learned |
| **Tools** | What is true in the environment *now*? | Live Docker/DNS/HA state via MCP and related integrations |

Rules:

1. Do not store conversational continuity as Knowledge.
2. Do not treat a chat recollection as authoritative Knowledge.
3. Do not treat live tool output as durable Knowledge until validated and recorded through governance.
4. Knowledge informs reasoning; **Knowledge does not make decisions.** The Council decides; KORA synthesizes.

### Knowledge quality principles

1. **Prefer authoritative sources** over convenience copies.
2. **Prefer freshness awareness** over false permanence.
3. **Prefer attribution** over anonymous assertion.
4. **Prefer applicability** over topical similarity alone.
5. **Prefer honest uncertainty** (“I need more information”) over fabricated completeness.
6. **Prefer minimum sufficient context** — retrieval serves deliberation, not archive dumping.

---

## Knowledge Domains

Conceptual categories. Implementation stores are deferred.

### Infrastructure Knowledge

Reference material about the homelab platform.

Examples:

- Homelab architecture
- Networking (`proxy` / `hotio`, Traefik, VLANs)
- Docker / compose standards
- Storage (Monarch appdata, Hive media)
- Service inventories and runbooks
- Production baseline and known exceptions

### Project Knowledge

Reference material about workstreams and decisions.

Examples:

- Roadmaps (Phase docs, StandardsRoadmap)
- Design documents
- ADRs
- Validation reports and completion records
- Deferred work and technical debt registers

### Technical Knowledge

General and specialized technical reference.

Examples:

- Documentation and manuals
- Research notes retained as reference
- Protocol / API references
- Coding and operational guides curated for the platform

### Personal Knowledge

User-provided reference information that is intentionally treated as durable reference (not mere chat memory).

Examples:

- Stated goals recorded as reference
- Explicit preference documents the user designates as knowledge
- Personal project briefs promoted into the knowledge corpus

Boundary: ephemeral preference expressed in conversation starts as **Memory** unless promoted under governance into Personal Knowledge.

### External Knowledge

Reference material originating outside the repository corpus.

Examples:

- External research retained with source metadata
- Vendor documentation snapshots
- API specifications
- Time-bounded “current information” captures

External Knowledge requires stricter authority and freshness handling.

---

## Knowledge Lifecycle

```text
Acquire
  ↓
Validate
  ↓
Organize
  ↓
Index
  ↓
Retrieve
  ↓
Provide Context
  ↓
Review / Update
```

| Stage | Purpose | Responsibility (conceptual) | Governance concerns |
| --- | --- | --- | --- |
| **Acquire** | Bring candidate information into scope | Human curation; controlled import; future ingestion pipelines | Source identity, license/sensitivity, scope creep |
| **Validate** | Confirm correctness and applicability | Human review for authoritative classes; automated checks later | False confidence, unverified web claims, secret leakage |
| **Organize** | Place items into domains and collections | Knowledge ownership roles; directory/taxonomy conventions | Orphan docs, duplicate SoT, naming drift |
| **Index** | Make items findable by conceptual retrieval | Future indexing services (deferred tech) | Incomplete indexes, stale index vs source |
| **Retrieve** | Select relevant items for a request | KORA context assembly after classification | Over-retrieval, under-retrieval, wrong domain |
| **Provide Context** | Deliver usable excerpts/citations into deliberation | KORA; Council consumes, does not own the store | Context flooding, missing attribution |
| **Review / Update** | Correct, supersede, or deprecate | Owners of authoritative sources; KORA may flag conflicts | Silent rot, conflicting “current” truths |

Lifecycle stages are architectural. No database, crawler, or RAG product is selected here.

---

## Knowledge Quality Model

KORA evaluates candidate knowledge along these axes before treating it as decision-grade context.

| Axis | Question | Failure mode if ignored |
| --- | --- | --- |
| **Accuracy** | Is the information correct? | Confident wrong recommendations |
| **Freshness** | Could it be outdated? | Acting on superseded architecture |
| **Authority** | What is the source, and is it allowed to speak? | Blog-tier claims overriding ADRs/baseline |
| **Context** | Does it apply to *this* decision? | Topically similar but wrong environment |
| **Confidence** | How certain should KORA be? | Fake certainty; suppressed “need more information” |

### Epistemic states (required distinction)

KORA must distinguish:

| State | Meaning |
| --- | --- |
| **I know** | Supported by validated, authoritative Knowledge in scope |
| **I have evidence** | Partial support exists; gaps or conflicts remain |
| **I believe** | Inference or unverified hypothesis—not Knowledge authority |
| **I need more information** | Retrieval/tools/human input required before strong recommendation |

Council synthesis must not launder “I believe” into “I know.”

---

## Knowledge Retrieval Model

Conceptual flow (aligns with Council deliberation):

```text
User Request
    ↓
KORA Classification
    ↓
Knowledge Requirements
    ↓
Relevant Knowledge Retrieval
    ↓
Context Assembly
    ↓
Council Deliberation
```

### Who requests knowledge

- **KORA** owns knowledge requirement derivation and retrieval initiation after classification.
- **Council members** may request additional knowledge mid-deliberation (especially IRIS for missing sources, LUMA for precedent documents, ALUMA for standards/constraints).
- Members do not bypass KORA to invent a parallel private corpus as platform truth.

### How relevance is determined

Relevance is **classification-driven**, not similarity-only:

1. Map request domain and constraints to knowledge domains.
2. Prefer authoritative collections for that domain (for example, Phase 12 baseline for production state claims).
3. Retrieve minimum sufficient set for material decision dimensions.
4. Attach source attribution and freshness cues to each item.

### Conflicting sources

When sources conflict:

1. Prefer higher authority per governance (see below).
2. Prefer newer validated supersession over older copies.
3. Surface unresolved conflict to Council (often IRIS + LUMA + relevant specialist).
4. Represent uncertainty explicitly; do not silently pick a favorite.

### Uncertainty representation

Retrieval results should be able to express:

- Found / not found
- Partial coverage
- Conflict present
- Freshness unknown
- Authority tier

Uncertain knowledge must be visible in context assembly, not dropped.

---

## Council Relationship

Knowledge informs reasoning. Knowledge does not replace the Council.

### Example — Infrastructure decision

**Knowledge may provide:**

- Current architecture documentation
- Docker / networking standards
- Production baseline and exceptions
- Historical technical facts recorded as reference
- Documented constraints and debt

**Council provides:**

| Member | Contribution |
| --- | --- |
| NOVA | Strategy |
| IRIS | Discovery against sources / gaps |
| ALUMA | Engineering |
| NOMA | Risk |
| LUMA | Continuity with recorded history |
| TALIA / SOLA | Human impact / communication when material |
| KORA | Selection, facilitation, synthesis |

**Rule:** Even perfect Knowledge leaves judgment, trade-offs, and user-facing recommendation to Council deliberation under Dynamics / Deliberation / Voting (synthesis).

---

## Knowledge Governance

### Source authority (conceptual tiers)

| Tier | Examples | Typical use |
| --- | --- | --- |
| **Authoritative** | ADRs, Standards, Production Baseline, approved Phase completion docs | Decision-grade constraints |
| **Operational** | Service READMEs, runbooks, inventories | Day-to-day reference |
| **Working** | Drafts, proposals, WIP notes | Provisional; must be labeled |
| **External** | Vendor docs, research captures | Requires source + freshness metadata |
| **Deprecated** | Superseded docs retained for history | Must not drive current decisions unless explicitly historical |

### Ownership

- Every authoritative knowledge item should have a clear owning path in the repository (or declared external owner).
- Homelab platform knowledge defaults to repository governance paths already established (Architecture, Documentation, Services, Validation).

### Update responsibility

- Source owners update authoritative documents through normal repo process.
- KORA may **flag** staleness or conflict; KORA does not silently rewrite authoritative Knowledge.
- Promotion from Memory → Personal/Project Knowledge requires explicit governance (human approval for authoritative classes).

### Conflict resolution

1. Authority tier
2. Explicit supersession links / newer approved docs
3. Human resolution for authoritative conflicts
4. Transparent dual-citation to Council while unresolved

### Deprecated information handling

- Retain for historical continuity when useful.
- Mark deprecated / superseded.
- Exclude from default “current truth” retrieval unless the request is historical.

### Human approval boundaries

Human approval is required (or already embodied via repo merge norms) for:

- New authoritative standards / ADRs / baseline changes
- Promotion of chat claims into authoritative Knowledge
- Acceptance of high-impact external knowledge as decision-grade
- Destruction or unmarked alteration of authoritative sources

KORA may propose; humans approve authoritative mutations.

---

## Knowledge Relationships (Conceptual Graph)

KORA **should conceptually support relationships** among knowledge entities so retrieval and Council reasoning can follow links—not only keyword hits.

### Relationship requirement (conceptual)

Support links among:

- Documents
- Projects / phases
- Services
- Decisions (ADRs, recorded choices)
- People / roles (as metadata, not surveillance)
- Systems / hosts / networks
- Concepts (for example “dual-home media networking”)

### Example relationship types (non-exhaustive)

| From | To | Relation idea |
| --- | --- | --- |
| Service | Standard | governed_by |
| ADR | Architecture doc | decides |
| Phase report | Baseline | establishes |
| Document | Document | supersedes |
| Service | Host/network | deployed_on |
| Decision | Decision | revises |

### Non-decision

No graph database, triple store, or product is selected. Phase 13.2 only asserts that **relationship-aware knowledge is an architectural requirement** for future implementation.

---

## Context Assembly Integration

Per `KORA.md` and `Council/Deliberation.md`, context assembly combines:

| Input | Role |
| --- | --- |
| Knowledge | What exists (reference) |
| Memory | What was remembered (continuity) |
| Tools | What is true now (live) |

Assembly principles:

- Keep provenance labels on each fragment (`knowledge` | `memory` | `tool`).
- Prefer Knowledge for standards/baseline claims.
- Prefer Tools for live state when freshness matters.
- Prefer Memory for user-specific continuity and prior recommendations.
- Feed assembled context into Council; do not let any single store monopolize the answer.

---

## Future Implementation Boundaries

Possible future capabilities (**not selected here**):

- Document ingestion pipelines
- Semantic search
- Embedding generation
- Retrieval systems / RAG frameworks
- Knowledge graph engines
- Reranking
- Source attribution UX
- Automated freshness crawlers
- Access-control layers for sensitive corpora

These belong to later Phase 13 implementation tracks (especially 13.4 tools and 13.5 runtime), under ADRs when technology choices are made.

---

## Document Map

| Document | Role |
| --- | --- |
| `Knowledge.md` (this file) | Canonical Knowledge Architecture (domains, quality, governance principles) |
| `Knowledge_Runtime.md` | Runtime acquisition, validation, updates, promotion |
| `Memory.md` | Memory subsystem (separate) |
| `Context_Assembly.md` | How knowledge enters reasoning context |
| `KORA.md` | Platform architecture; context assembly ownership |
| `Council/Deliberation.md` | When knowledge enters the session lifecycle |
| `Council/Selection.md` | Classification that drives knowledge requirements |
| `Tools.md` | Live tools — not durable Knowledge by default |
| `MCP.md` | Tool / MCP architecture |
| `Documentation/Phase13/Knowledge_Architecture_Model.md` | Phase 13.2 report |
| `Documentation/Phase13/Memory_Runtime_Model.md` | Phase 13.5 report |

---

## Status

Phase 13.2 architecture complete at the conceptual level.  
Phase 13.5 adds runtime evolution/promotion rules in `Knowledge_Runtime.md`.  
No databases, vector stores, ingestion services, or RAG implementations are authorized by these documents alone.
