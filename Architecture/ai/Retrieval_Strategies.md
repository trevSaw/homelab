# KORA Retrieval Strategies

**Status:** Canonical conceptual specification (Phase 13.12)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Companion:** `Context_Intelligence.md`, `Context_Ranking.md`  
**Rule:** Strategy is chosen by **classification**. Default is selective—not global—retrieval.

No vendor, embedding, or database selection in this document.

---

## Strategy Object (Conceptual)

Each strategy declares:

| Field | Meaning |
| --- | --- |
| **Query Memory?** | yes / no / limited |
| **Query Knowledge?** | yes / no / limited |
| **Query Tools?** | yes / no / read-only |
| **Query Agents?** | yes / no (rare in thin path) |
| **Relationship graph?** | no (default; Graphify planned for Phase 14.4) |
| **Priority order** | which store first |
| **Expected provenance** | required labels |
| **Expected confidence posture** | high/medium/low / ask |
| **Budget** | max candidates per store (conceptual) |

---

## Strategy Catalog

### 1. Architecture question

**Examples:** “How should a service attach to proxy?” / “Why did we choose Traefik?”

| Store | Policy |
| --- | --- |
| Knowledge | **Yes** — standards, ADRs, architecture docs |
| Memory | **No** (unless user references a prior personal decision) |
| Tools | **No** (unless asking live topology) |
| Agents | No by default |
| Graphify | No |

**Priority:** Knowledge (Authoritative → Validated → Candidate)  
**Provenance:** `knowledge` + path/ADR id + authority tier  
**Confidence:** High when ADR/standard hit; medium otherwise  
**Ignore:** User preference stores, unrelated project chatter

---

### 2. User preference

**Examples:** “I prefer Jellyfin over Plex.” / “I prefer Jellyfin.”

| Store | Policy |
| --- | --- |
| Memory | **Yes** — User Memory only (read); writes need governance |
| Knowledge | **No** |
| Tools | **No** |
| Agents | No |
| Graphify | No |

**Priority:** Memory-first (often Memory-only)  
**Provenance:** `memory` + preference id  
**Confidence:** High if explicit statement; candidate if inferred  
**Ignore:** Entire Knowledge corpus (fixes Phase 13.11 over-fetch)

---

### 3. Personal question

**Examples:** “What do you remember about me?” / “What are my preferences?”

| Store | Policy |
| --- | --- |
| Memory | **Yes** — User Memory |
| Knowledge | **No** |
| Tools | **No** |
| Agents | No |

**Priority:** Memory-only  
**Provenance:** `memory`  
**Confidence:** Per memory confidence; empty Memory is valid  
**Ignore:** Knowledge, Tools

---

### 4. Project question

**Examples:** “Continue Phase 13.” / “Where did we leave the HA work?”

| Store | Policy |
| --- | --- |
| Memory | **Yes** — Project Memory |
| Knowledge | **Yes** — project/phase docs, roadmaps, architecture |
| Tools | No unless status asked |
| Agents | No by default |
| Graphify | No (default) |

**Priority:** Project Memory → Project/phase Knowledge → Architecture/roadmap Knowledge  
**Provenance:** separate Memory vs Knowledge labels  
**Confidence:** Medium–high depending on freshness of phase docs  
**Ignore:** Unrelated personal preferences; unrelated live metrics

---

### 5. Research request

**Examples:** “Compare approaches for X using our docs.”

| Store | Policy |
| --- | --- |
| Knowledge | **Yes** — broad but budgeted |
| Memory | Limited (only if user constraints stored) |
| Tools | No unless researching live state |
| Agents | Optional later for gathering drafts |

**Priority:** Knowledge-first  
**Provenance:** `knowledge` with authority/freshness  
**Confidence:** Variable; surface gaps  
**Ignore:** Preference Memory unless relevant constraint

---

### 6. Operational status

**Examples:** “What containers are running?” / disk fill “right now”

| Store | Policy |
| --- | --- |
| Tools | **Yes** — Read tools only when authorized |
| Knowledge | **No** for live facts (may cite runbooks separately if asked “how to check”) |
| Memory | Limited Operational Memory only if continuity helps |
| Agents | Optional mediated reads |

**Priority:** Tool-first  
**Provenance:** `tool` + timestamp  
**Confidence:** High for fresh tool evidence; **unknown** if tools unavailable—do not fabricate  
**Ignore:** Knowledge as substitute for live state; Graphify

---

### 7. Decision support

**Examples:** “Should we adopt approach A or B under our standards?”

| Store | Policy |
| --- | --- |
| Knowledge | **Yes** — ADRs, standards, baselines |
| Memory | Limited — prior project decisions if relevant |
| Tools | If live constraints matter |
| Agents | Optional analysis workers (≠ Council) |

**Priority:** Knowledge-first → relevant Project Memory → Tools if needed  
**Provenance:** mixed labels preserved  
**Confidence:** Medium; trade-offs expected for Council  
**Ignore:** Unrelated preferences; silent single-source picks

---

### 8. Automation request

**Examples:** “Restart Traefik and open port 80.”

| Store | Policy |
| --- | --- |
| Tools | **Do not Execute** in default path; may Read policy Knowledge |
| Knowledge | **Yes** — governance/standards for refusal rationale |
| Memory | No |
| Agents | No autonomous Execute |

**Priority:** Knowledge (governance) → refuse Execute  
**Provenance:** `knowledge` for why refused  
**Confidence:** High on refusal posture  
**Ignore:** Treating request as ordinary Q&A retrieval binge

---

### 9. Unknown / clarification

**Examples:** “I'm not sure.” / underspecified asks

| Store | Policy |
| --- | --- |
| Memory | **Minimal / no** |
| Knowledge | **Minimal / no** |
| Tools | **No** |
| Agents | No |

**Priority:** Clarification-first; minimal retrieval  
**Provenance:** mostly `user` / conversation  
**Confidence:** Low; ask for missing information  
**Ignore:** Unnecessary context from all stores

---

### 10. Identity

**Examples:** “What are you?”

| Store | Policy |
| --- | --- |
| Memory | No |
| Knowledge | Limited optional (`KORA.md` identity) |
| Tools | No |

**Priority:** Identity policy / optional Knowledge identity docs  
**Provenance:** architecture identity, not vendor names as self  
**Confidence:** High on identity assertion  

---

### 11. Conflicting information

**Examples:** “Which HA networking rule is correct?” when sources disagree

| Store | Policy |
| --- | --- |
| Knowledge | **Yes** — retrieve conflicting pair deliberately |
| Memory | No unless user preference about the conflict |
| Tools | If live state relevant |

**Priority:** Knowledge with **conflict preservation** (not collapse)  
**Provenance:** dual-cite + authority tiers  
**Confidence:** Explicit uncertainty until authority/supersession resolves  

---

## Specific Scenario Mapping (Required)

| User say | Strategy | Queried | Ignored |
| --- | --- | --- | --- |
| “I prefer Jellyfin.” | User preference | Memory only | Knowledge, Tools |
| “Why did we choose Traefik?” | Architecture | Knowledge (ADRs/architecture) | Memory (default) |
| “What containers are running?” | Operational status | Tools only | Knowledge |
| “What do you remember about me?” | Personal | Memory only | Knowledge, Tools |
| “Continue Phase 13.” | Project | Project Memory + Project/roadmap/architecture Knowledge | Unrelated prefs; live tools |
| “I'm not sure.” | Unknown/clarification | Minimal / none | Unnecessary context |

---

## Memory-first vs Knowledge-first vs Tool-first

| Mode | When |
| --- | --- |
| **Memory-first** | Preferences, personal continuity, “what do you remember” |
| **Knowledge-first** | Architecture, ADR rationale, standards, research, decision support |
| **Tool-first** | Live operational status / “right now” environment facts |
| **Clarification-first** | Unknown, underspecified, user uncertainty |

Mixed modes (e.g. project) still **sequence** stores—they do not dump all corpora at once.

---

## Document Map

| Document | Role |
| --- | --- |
| `Retrieval_Strategies.md` (this file) | Per-class store policies |
| `Context_Intelligence.md` | Orchestrates strategy selection |
| `Context_Ranking.md` | Scores and prunes after retrieval |
