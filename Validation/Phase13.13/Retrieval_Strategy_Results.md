# Retrieval Strategy Results

| Scenario | Strategy | Queried | Key skipped stores | Result |
| --- | --- | --- | --- | --- |
| 01 | `knowledge_first_architecture` | Knowledge | Memory, Tools, Graphify | Pass |
| 02 | `memory_only_preference` | Memory | Knowledge, Tools, Graphify | Pass |
| 03 | `tools_only_live_status` | Tools | Memory, Knowledge, Graphify | Pass |
| 04 | `knowledge_conflict_preserving` | Knowledge | Memory, Tools, Graphify | Pass |
| 05 | `identity_policy_only` | None | All stores | Pass |
| 06 | `refusal_minimal` | None | All stores | Pass |
| 07 | `tools_only_live_status` | Tools | Memory, Knowledge, Graphify | Pass |
| 08 | `memory_only_personal` | Memory | Knowledge, Tools, Graphify | Pass |
| 09 | `project_memory_then_knowledge` | Memory, Knowledge | Tools, Graphify | Pass |
| 10 | `clarification_minimal` | None | All stores | Pass |

Phase 13.11 regression check: Scenario 02 queried no Knowledge and assembled no Knowledge evidence.
