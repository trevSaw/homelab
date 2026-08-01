# KORA Architecture Alignment Report

**Phase:** 13.0 — KORA Architecture Alignment & Documentation Integration  
**Date:** 2026-08-01  
**Scope:** Documentation architecture only (no software, Docker, services, or technology selection)

---

## Summary

The AI architecture documentation under `Architecture/ai/` has been aligned to the finalized model:

**KORA (Knowledge-Oriented Response Assistant) is Brainiac.**  
KORA is the primary AI entity and a Council member who serves as Chair / Conductor / First Among Equals. The Council is a collective reasoning framework. Memory, knowledge, tools, agents, and models are subsystems or concerns of KORA—not peer identities and not a hierarchy that places KORA above the Council.

---

## Documents reviewed

| Document | Pre-alignment state | Alignment verdict |
| --- | --- | --- |
| `Architecture/ai/README.md` | One-line generic stub | Required rewrite as entry point |
| `Architecture/ai/KORA.md` | Missing | Created (canonical) |
| `Architecture/ai/Council/Dynamics.md` | Authoritative behavior; KORA omitted from member table | Minor consistency update only |
| `Architecture/ai/Council/README.md` | Placeholder `# README` | Updated as Council entry |
| `Architecture/ai/Council/Council.md` | Placeholder `# Council` | Brief overview pointer added |
| `Architecture/ai/Council/Selection.md` | Placeholder | No change (gap) |
| `Architecture/ai/Council/Voting.md` | Placeholder | No change (gap) |
| `Architecture/ai/Council/Members/*` | Canonical member specs present | No rewrite (lore/ops remain authoritative for members) |
| `Architecture/ai/Council/Members/Council-Dynamic.md` | Early draft source | Intentionally not rewritten; superseded by Dynamics.md |
| `Architecture/ai/Memory.md` | One-line stub | Light responsibility framing |
| `Architecture/ai/Models.md` | One-line stub | Light responsibility framing |
| `Architecture/ai/MCP.md` | One-line stub | Light responsibility framing |
| `Architecture/ai/Agents.md` | One-line stub | Light responsibility framing + anti-conflation rule |
| `Architecture/ai/FuturePlans.md` | One-line stub | Anchored to KORA model + Phase 13 sequence |
| `Documentation/Phase13/Phase13_Roadmap.md` | Phase 13.1+ roadmap | Reviewed; 13.0 recorded via this report + README link |
| `Architecture/standards/StandardsRoadmap.md` | Already uses Brainiac / KORA naming | No change required for 13.0 |

---

## Changes made

### Created

1. **`Architecture/ai/KORA.md`**  
   Canonical KORA / Brainiac architecture: identity, purpose, Council role, responsibilities, cognitive model, member relationships, request lifecycle, context assembly, memory/knowledge/tool/agent/model relationships, document map, future evolution placeholder.

2. **`Documentation/Phase13/KORA_Architecture_Alignment.md`** (this report)

### Updated

1. **`Architecture/ai/README.md`**  
   Entry point: what KORA is, what the Council is, conceptual model diagram, separation of responsibilities, document index.

2. **`Architecture/ai/Council/Dynamics.md`**  
   Added KORA to the Council Members table as Conductor / Chair; clarified KORA is part of the Council, not above it; linked `../KORA.md`. Operating principles and flows unchanged in substance.

3. **`Architecture/ai/Council/README.md`**  
   Replaced placeholder with Council directory entry and pointers.

4. **`Architecture/ai/Council/Council.md`**  
   Replaced placeholder with short overview pointing to Dynamics and KORA.md.

5. **`Architecture/ai/Memory.md`**, **`Models.md`**, **`MCP.md`**, **`Agents.md`**, **`FuturePlans.md`**  
   Preserved original purpose lines; added explicit responsibility boundaries relative to KORA without technology selection.

6. **`Documentation/Phase13/README.md`**  
   Linked this alignment report (see companion edit).

---

## Changes intentionally not made

| Item | Rationale |
| --- | --- |
| No rewrite of `Council/Members/*.md` | Member lore and operational voice already align; rewriting would duplicate `KORA.md` / Dynamics concerns |
| No rewrite of Council philosophy in Dynamics | Dynamics remains authoritative; only membership-table consistency was required |
| No expansion of `Selection.md` / `Voting.md` | Still Phase 13.1 deliverables; 13.0 is alignment, not completion of those artifacts |
| No deletion/rename of `Members/Council-Dynamic.md` | Historical source; superseded operationally by Dynamics.md |
| No rename of Memory/Models/MCP/Agents/FuturePlans | Names already match separation-of-responsibilities model |
| No Docker / compose / service / runtime changes | Explicitly out of scope |
| No technology selections (Ollama, vector DB, Hermes product choices, etc.) | Explicitly out of scope |
| No changes to Phase 12 deliverables | Prerequisite baseline remains untouched |

---

## Remaining architectural gaps

1. **Selection rules** (`Council/Selection.md`) — not formalized.
2. **Voting rules** (`Council/Voting.md`) — not formalized.
3. **Prompt architecture** and **canonical member template** beyond KORA member spec practice — still Phase 13.1 open items.
4. **Knowledge architecture** — no dedicated `Knowledge.md` yet; referenced as Phase 13.2.
5. **Context assembly specification** — owned in `KORA.md` at principle level; needs detailed design later.
6. **Memory governance / lifecycle** — stub only.
7. **Agent lifecycle vs Council role** — clarified in principle; orchestration patterns still Phase 13.3.
8. **MCP security model** — stub only; Phase 13.4.
9. **UX / explainability** — Phase 13.6; not started.
10. **`council.yaml`** — placeholder content only.

---

## Recommended next Phase 13 documentation steps

1. **Complete Phase 13.1 Council artifacts**  
   Formalize Selection.md, Voting.md, prompt architecture, and a short canonical member template derived from existing member specs.

2. **Add `Architecture/ai/Knowledge.md` (Phase 13.2 kickoff)**  
   Mirror Memory/MCP stubs: reference information vs memory vs tools, with governance hooks—still no tech lock-in.

3. **Record Phase 13.0 complete** in `Phase13_Roadmap.md` once this alignment is accepted.

4. **Keep Dynamics.md authoritative**  
   Any future orchestration (Hermes) docs must reference Dynamics rather than redefining Council behavior.

5. **When implementation begins**  
   Map runtime components explicitly onto: KORA identity, Council roles, Memory, Knowledge, Tools, Agents, Models—never introduce a second “Brainiac engine” abstraction.

---

## Consistency checklist

| Requirement | Status |
| --- | --- |
| KORA is Brainiac | Documented in `KORA.md` / README |
| KORA is a Council member | Dynamics table + KORA.md |
| Chair / Conductor / First Among Equals | Documented; Dynamics preserved |
| KORA does not replace the Council | Explicit in KORA.md |
| KORA does not manage members as employees/sub-agents | Explicit in KORA.md / Agents.md |
| Dynamics.md remains authoritative | Affirmed; only membership-table consistency edit |
| Separation: Council / Memory / Knowledge / Tools / Agents / Models | Documented in README + KORA.md + stubs |
| No infrastructure or technology implementation | Honored |
