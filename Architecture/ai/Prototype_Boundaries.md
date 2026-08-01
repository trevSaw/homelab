# KORA Prototype Boundaries

**Status:** Canonical prototype-scope specification (Phase 13.9)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companions:** `Vertical_Slice.md`, `Integration_Flow.md`  
**Rule:** The first prototype proves interfaces—not autonomy, production ops, or vendor lock-in.

---

## Purpose

Define what the first KORA thin vertical slice is **allowed to prove** and what it is **forbidden to do**.

This keeps implementation risk bounded when a later spike is authorized.  
This document itself authorizes **neither** installs nor deployments.

---

## Prototype Intent

Prove:

> A user request can become a provenance-labeled recommendation with explainability, using KORA classification, Council selection, context assembly, and separated Memory/Knowledge retrieval—without collapsing architectural boundaries.

---

## Allowed

The first prototype **may** demonstrate:

| Allowed proof | Why it matters |
| --- | --- |
| **Conversation flow** | Interface → orchestration → KORA → response loop |
| **Context assembly** | Minimum sufficient packaged context with labels |
| **Council selection** | Classification-driven member selection / deferral |
| **Recommendation generation** | KORA synthesis of deliberative outputs |
| **Explainability** | Structured why/evidence/contributors (no raw CoT) |
| **Separated retrieval stubs** | Distinct Memory vs Knowledge result channels (even if stubbed/empty) |
| **Failure paths** | Retrieval unavailable, refuse Execute, missing provenance handling |
| **Invisible / Advisory Council presentation modes** | Per UX contracts, if surfaced |

Allowed artifacts are **design proofs and non-production spikes** when separately authorized—not Phase 12 production changes.

---

## Not Allowed

The first prototype **must not**:

| Forbidden | Rationale |
| --- | --- |
| **Autonomous actions** | Tools ≠ Decisions; no self-acting on the homelab |
| **System modification** | No compose/network/service changes; no Phase 12 regression |
| **Production automation** | No cron-driven ops, self-healing, or unattended Execute |
| **Permanent memory writes without governance** | Memory lifecycle requires Evaluate/Classify/confirmation rules |
| **Silent Memory → Knowledge promotion** | Boundary preservation |
| **Treating indexes as SoT** | Chroma/Graphify (if present later) are not authority |
| **Replacing KORA identity with UI/orchestration brand** | Open WebUI / Hermes are substrates only |
| **Council-as-agents collapse** | Members remain advisory seats, not temporary workers |
| **Raw chain-of-thought exposure** | Explainability contract |
| **Installing Hermes, Open WebUI, Honcho, ChromaDB, or Graphify under this phase** | Phase 13.9 is architecture validation only |
| **Creating Docker compose for the slice under this phase** | Explicit restriction |
| **MCP server deployment / live admin tooling** | Out of thin-slice scope |

---

## Proof Levels

| Level | Meaning | Authorized by Phase 13.9? |
| --- | --- | --- |
| **Architecture proof** | Documents define interfaces, I/O, boundaries | Yes (this phase) |
| **Design spike plan** | Time-boxed non-production experiment plan | Referenced only; needs later authorization |
| **Runtime spike** | Actual processes/containers | **No** in 13.9 |
| **Production path** | Homelab baseline integration | **No** |

---

## Acceptance for a Future Spike (Not This Phase)

When a later phase authorizes a spike, it should still obey these boundaries unless an ADR explicitly expands them.

Minimum spike acceptance (preview):

1. One request → one recommendation + explainability object
2. Provenance labels present on evidence
3. Memory and Knowledge channels remain distinct
4. No Execute/Administrative side effects
5. No durable Memory write unless gated by explicit governance UX
6. Rollback leaves Phase 12 and architecture docs intact

---

## Document Map

| Document | Role |
| --- | --- |
| `Prototype_Boundaries.md` (this file) | Allowed / forbidden prototype scope |
| `Vertical_Slice.md` | E2E workflow |
| `Integration_Flow.md` | Data movement and ownership |
