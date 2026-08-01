# Boundary Verification — Phase 13.11

| Boundary | Evidence | Status |
| --- | --- | --- |
| Council ≠ Agents | `council_selection.agents_as_members=false` in all scenario JSON | ✅ |
| Memory ≠ Knowledge | Preference staged as Memory candidate; not committed; not labeled Knowledge authority | ✅ |
| Knowledge ≠ Tools | Knowledge fixtures only; no tool evidence used as Knowledge | ✅ |
| Tools ≠ Decisions | Forbidden scenario refused; `tool_invoked=false` across all runs | ✅ |
| KORA identity | `identity=KORA`; identity recommendation asserts Brainiac/KORA | ✅ |
| UI ≠ KORA | Open WebUI adapter forces `presented_as=KORA`; not product identity | ✅ |
| Hermes ≠ KORA | Adapter asserts `is_kora=false`, `replaces_council=false` | ✅ |
| Index ≠ SoT | Chroma/fixtures cited with authority labels; ADR preferred in conflict | ✅ |
| Graphify excluded | Adapter trace `graphify=excluded` | ✅ |
| No Phase 12 coupling | Container only on `kora_spike_net` | ✅ |
| No durable Memory write | `memory_write_committed=false` all scenarios | ✅ |
| No raw CoT | `explainability.raw_cot_exposed=false` | ✅ |

## Soft boundary quality note

Preference scenario still assembled unrelated Knowledge hits via naive keyword retrieval. This did **not** violate write/SoT boundaries but weakens minimum-sufficient assembly. Track for Phase 13.12.
