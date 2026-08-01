# KORA Operational Readiness

**Status:** Canonical operational-readiness architecture (Phase 13.15)  
**Platform:** KORA / Brainiac (`KORA.md`)  
**Rule:** Architecture-only ops philosophy. No runbooks that require compose files, ports, or secret material in this phase.

Companions: `Production_Architecture.md`, `Rollout_Strategy.md`, `Runtime_Observability.md`, `Runtime_State.md`

---

## Purpose

Define how a future production KORA stack should start, stop, degrade, recover, and be maintained—while preserving Phase 13 contracts.

---

## Startup Sequence (Logical)

1. **State stores** (if enabled): Knowledge Runtime, Memory Runtime — healthy or explicitly disabled  
2. **Integration** (if enabled): MCP Gateway → Tool Runtime  
3. **KORA Core:** KORA Runtime (Classification, Context Intelligence, Assembly, Explainability, Council Runtime)  
4. **Orchestration:** Hermes  
5. **UI:** Open WebUI  

Optional Relationship Runtime starts only if adopted and after Knowledge is healthy.

**Guard:** Do not accept user traffic until Classification → Context Intelligence path is live (even if Memory/Knowledge/Tools are disabled modes).

---

## Shutdown Sequence (Logical)

1. Stop accepting new UI sessions  
2. Drain in-flight KORA syntheses (timeout)  
3. Disable Tool Execute paths first; then Tool Runtime / MCP  
4. Quiesce Memory/Knowledge writes (candidates must not auto-commit)  
5. Stop Hermes / KORA Core  
6. Stop UI  
7. Stop stores  

Never shut down by “leaving Execute tools running.”

---

## Health Expectations

| Service class | Healthy means |
| --- | --- |
| UI | Renders; can reach orchestration or shows unavailable |
| Hermes | Routes to KORA; does not advertise as KORA |
| KORA | Classifies; refuses unsafe Execute; emits explainability |
| Memory | Answers or empty; no silent write |
| Knowledge | Answers with provenance or gap; not SoT claims |
| Tools/MCP | Read available or explicit down; Execute gated |
| Council | Contributions attributable; profile mode declared |

---

## Recovery Philosophy

1. **Fail closed** on Execute and identity  
2. **Fail open to honesty** on missing evidence (uncertainty, not fiction)  
3. Prefer **disable a domain** over violating contracts  
4. Rebuild indexes from SoT rather than trust corrupt stores  
5. Profile fallback: Distributed → Simulated → Solo  

---

## Degraded Operation

| Degradation | Allowed behavior |
| --- | --- |
| Memory down | Skip continuity; say so |
| Knowledge down | Architecture answers limited; ask for sources |
| Tools down | No live claims |
| Hermes down | No vendor-identity bypass; UI unavailable or maintenance |
| One Distributed member down | Continue with reduced Council; note degradation |

Forbidden degradation: silent model chat that skips KORA contracts.

---

## Dependency Failures

| Dependency | Response |
| --- | --- |
| Inference endpoint down | Hard unavailable |
| Chroma unreachable | Knowledge strategies gap-flag |
| Honcho unreachable | Memory strategies gap-flag |
| MCP down | Tools strategies uncertainty |
| Phase 12 system down | Tool evidence missing; do not invent |

---

## Runtime Modes

| Mode | Meaning |
| --- | --- |
| **Solo** | Initial production target |
| **Simulated** | Single-model Council fidelity |
| **Distributed** | Multi-member runtimes |
| **Hybrid** | Mixed local/remote |

Mode is an operational setting; architecture contracts are constant (`Runtime_Profiles.md`).

---

## Maintenance Philosophy

- Change one rollout stage domain at a time  
- Re-validate Context Intelligence scenarios after retrieval-stack changes  
- Never maintain by rewriting Phase 13 docs to match a vendor quirk  
- Obsidian remains external; not required for ops  
- Graphify remains off until adopted  

---

## Observability Tie-In

Operational readiness assumes `Runtime_Observability.md` events exist conceptually for classification, strategy, retrieval, ranking, Council, refusals, and audit—implementation of log stacks is Phase 14+.

---

## Document Map

| Document | Role |
| --- | --- |
| `Operational_Readiness.md` (this file) | Ops philosophy |
| `Rollout_Strategy.md` | What to enable when |
| `Runtime_Observability.md` | What to observe |
| `Runtime_State.md` | Lifecycle ownership |
