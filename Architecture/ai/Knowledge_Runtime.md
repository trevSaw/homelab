# Knowledge Runtime Architecture

**Status:** Canonical runtime architecture specification (Phase 13.5)  
**Boundary companion:** `Knowledge.md` (Phase 13.2 domains, quality, governance principles)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Related:** `Memory_Runtime.md`, `Context_Assembly.md`, `Tools.md`

Knowledge answers: **What information exists and has been validated as reference material?**

This document defines how knowledge is acquired, validated, updated, and promoted at runtime conceptually.  
It does **not** select databases, embeddings, ingestion products, or RAG frameworks.

---

## Relationship to Phase 13.2

`Knowledge.md` remains authoritative for:

- Domains
- Quality axes
- Authority tiers
- Conceptual relationships
- Separation from Memory/Tools

`Knowledge_Runtime.md` specifies **operational evolution** of that corpus over time.

---

## Knowledge Acquisition (Conceptual)

How information enters the knowledge ecosystem:

| Source class | Examples | Notes |
| --- | --- | --- |
| Repository documentation | Architecture, Standards, Documentation, Services | Primary interim substrate |
| Project artifacts | Phase reports, validation packs, ADRs | Often high authority when approved |
| External references | Vendor docs, research captures | Require provenance + freshness |
| Generated documentation | KORA/agent drafts | **Candidates only** until evaluated |

Acquisition creates candidates—not automatic Authoritative Knowledge.

---

## Knowledge Validation

Every candidate/item should be evaluable on:

| Axis | Meaning |
| --- | --- |
| **Authority** | Who/what is allowed to assert this? |
| **Provenance** | Where did it come from? |
| **Freshness** | When updated; is it possibly stale? |
| **Confidence** | How certain should consumers be? |
| **Supersession** | What does it replace / what replaces it? |

Validation does not equal Council agreement. Validation means reference fitness.

---

## Knowledge Updates

### How updates occur

1. Source owner changes authoritative document through normal governance (repo/ADR process)
2. KORA/agents may **flag** staleness or conflict
3. Candidate updates enter promotion pipeline
4. Consumers retrieve with supersession awareness

### Outdated information

- Mark deprecated/superseded
- Keep historical copies when useful for LUMA-style continuity
- Exclude from default “current truth” retrieval

### Conflicts

- Represent dual citations rather than silent overwrite
- Prefer higher authority tier and explicit supersession
- Escalate unresolved authoritative conflicts to humans
- Surface conflict into Context Assembly / Council (often IRIS + LUMA + specialist)

---

## Knowledge Promotion Pipeline

```text
Information
  ↓
Candidate Knowledge
  ↓
Validated Knowledge
  ↓
Authoritative Knowledge
```

| Stage | Meaning | Gate |
| --- | --- | --- |
| **Information** | Raw material (docs, notes, tool captures, drafts) | None |
| **Candidate Knowledge** | Proposed reference item with provenance | Intake hygiene / sensitivity checks |
| **Validated Knowledge** | Reviewed for accuracy/applicability within scope | Owner/reviewer validation |
| **Authoritative Knowledge** | Decision-grade reference (standards, ADR, baseline, approved docs) | Human/governance approval norms |

### Hard rules

1. **Memory cannot silently become Knowledge**
2. **Tool results cannot silently become Knowledge**
3. **Generated content requires evaluation** before authority
4. Chat preference ≠ universal truth

Examples:

| Input | Allowed as | Not allowed as |
| --- | --- | --- |
| “I prefer Jellyfin.” | User Memory (preference) | Knowledge: “Jellyfin is universally better” |
| Tool: “Container is stopped.” | Live tool evidence | Knowledge: “Service is permanently broken” |
| KORA summary of a standard | Candidate / draft | Authoritative Standard without approval |

---

## Runtime Retrieval Expectations

- Classification-driven relevance (from Council Selection / request class)
- Return provenance, authority tier, freshness cues
- Prefer minimum sufficient set
- Distinguish Working vs Authoritative tiers in results
- Feed Context Assembly—not automatic decision issuance

---

## Relationship to Tools and Agents

- Tools may supply candidates (snapshots, exports) under permission
- Agents may draft documentation candidates
- Neither may self-promote to Authoritative Knowledge
- KORA evaluates promotion path; humans approve authoritative classes

---

## Non-goals

- Vector DB / graph DB / search engine selection
- Embedding strategy
- Ingestion pipeline deployment
- RAG framework choice

---

## Document Map

| Document | Role |
| --- | --- |
| `Knowledge_Runtime.md` (this file) | Runtime acquisition/validation/update/promotion |
| `Knowledge.md` | Domains, quality, governance principles |
| `Context_Assembly.md` | How knowledge enters reasoning context |
| `Memory_Runtime.md` | Continuity store runtime (separate) |
| `Documentation/Phase13/Memory_Runtime_Model.md` | Phase 13.5 report |
