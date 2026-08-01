# KORA Runtime Contracts

**Status:** Canonical runtime-contract specification (Phase 13.14)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Contracts define observable inputs, outputs, guarantees, and prohibitions. Profiles may change internals; they may not weaken contracts.

Companions: `Runtime_Profiles.md`, `Runtime_Observability.md`, `Runtime_State.md`

---

## Purpose

Specify the interfaces every KORA runtime—Solo, Simulated, Distributed, or Hybrid—must honor so architecture remains stable across hardware.

Contracts are **behavioral**, not API schemas. Exact serialization is an implementation concern for Phase 13.15+.

---

## Cross-Cutting Guarantees

1. Classification precedes retrieval  
2. Selective retrieval only (no global dump by default)  
3. Provenance labels on evidence  
4. Memory ≠ Knowledge ≠ Tools ≠ Agents ≠ Council seats  
5. Explainability without raw CoT  
6. No durable Memory write without governance approval  
7. No Knowledge promotion without governance  
8. No Execute/Administrative without approval UX  
9. Graphify off default path  
10. KORA remains sole user-facing identity  

---

## 1. Classification Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | User request; minimal Temporary Context; optional project/session hints; safety flags |
| **Outputs** | Classification label; confidence/ambiguity flag; rationale suitable for explainability |
| **Guarantees** | Runs before retrieval; ambiguous → narrower/safer path or clarification |
| **Prohibited** | Retrieving stores before classification; inventing live facts to classify |

---

## 2. Retrieval (Context Intelligence) Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Classification; strategy selection (`Retrieval_Strategies.md`); budgets |
| **Outputs** | Queried/skipped store lists; candidate evidence with provenance; skip reasons |
| **Guarantees** | Only allowed stores queried; preference → Knowledge off; operational → Tools-first; Graphify excluded by default |
| **Prohibited** | Global search across all stores; silent store queries not reflected in explainability |

---

## 3. Ranking Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Candidates from allowed stores; query; budgets |
| **Outputs** | Ranked kept set; ranking decisions; pruning records |
| **Guarantees** | Axes include relevance, authority, freshness, confidence, provenance, safety; conflicts not silently collapsed |
| **Prohibited** | Promoting Memory over Knowledge authority for standards; treating Tools as Knowledge |

---

## 4. Context Assembly Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Ranked/budgeted candidates; user request; Council selection metadata |
| **Outputs** | Provenance-labeled context package for Council/synthesis |
| **Guarantees** | Minimum sufficient; no laundering of source classes; no reopen of skipped stores without explicit expansion |
| **Prohibited** | Corpus dumps; stripping provenance; unlabeled Memory+Knowledge merges |

---

## 5. Explainability Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Recommendation; classification; strategy; queried/skipped; ranking/pruning; evidence; contributors; confidence |
| **Outputs** | Structured explanation object (`Explainability.md`) |
| **Guarantees** | User can see why/stores/contributors/confidence; identity remains KORA |
| **Prohibited** | Raw chain-of-thought dumps; vendor product as self-identity |

---

## 6. Memory Runtime Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Memory queries when strategy allows; user correction/delete/approve intents |
| **Outputs** | Memory evidence (`source_class=memory`) or empty; candidates pending approval |
| **Guarantees** | User control of personal Memory; empty Memory valid; no silent durable writes |
| **Prohibited** | Auto-persist preferences; labeling Memory as Knowledge; storing secrets |

---

## 7. Knowledge Runtime Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Knowledge queries when strategy allows; governed sources |
| **Outputs** | Knowledge evidence with authority/freshness/provenance |
| **Guarantees** | Index ≠ SoT; repo/ADRs remain authority; conflicts dual-cite |
| **Prohibited** | Silent promotion; inventing standards; substituting Tools for Knowledge SoT |

---

## 8. Council Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Assembled context; selection record; request class |
| **Outputs** | Member contributions (real or simulated per profile); synthesis inputs for KORA |
| **Guarantees** | Dynamics/Selection/Deliberation/Voting semantics; disagreement preservable; members ≠ agents |
| **Prohibited** | Majority-vote theater as authority; agents as seats; bypassing KORA synthesis identity |

Profile note: Solo/Simulated may produce contributions without independent member processes; Distributed may use independent runtimes—**outputs must still satisfy this contract**.

---

## 9. Agents Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Scoped task from KORA; permissions; context subset |
| **Outputs** | Temporary results with provenance; termination |
| **Guarantees** | Create/evaluate/terminate lifecycle; not Council seats |
| **Prohibited** | Permanent “staff agents”; autonomous Execute; presenting as KORA |

---

## 10. Tools Contract

| Field | Requirement |
| --- | --- |
| **Inputs** | Permissioned tool calls when strategy allows (Read vs Execute) |
| **Outputs** | Point-in-time evidence (`source_class=tool`) or explicit unavailability |
| **Guarantees** | Evidence ≠ decision; missing tools → uncertainty, not fabrication |
| **Prohibited** | Silent Execute/Administrative; promoting tool dumps to Knowledge |

---

## Contract Compliance Across Profiles

| Profile | Must still satisfy |
| --- | --- |
| Solo | All contracts; Council outputs may be conceptual under Dynamics |
| Simulated | All contracts; member contributions via structured prompting |
| Distributed | All contracts; orchestration substrate cannot own identity |
| Hybrid | All contracts; remote failures fail closed |

---

## Non-goals

- JSON schema freezing
- Vendor SDK bindings
- Production SLOs
- Logging stack selection

Those belong to later implementation phases under these contracts.

---

## Document Map

| Document | Role |
| --- | --- |
| `Runtime_Contracts.md` (this file) | Behavioral contracts |
| `Runtime_Profiles.md` | How hardware realizes contracts |
| `Runtime_Observability.md` | What must be observable |
| `Runtime_State.md` | State ownership through the lifecycle |
