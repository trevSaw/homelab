# Agents

Agent architecture, responsibilities, boundaries, and workflows.

## Role in the KORA architecture

Agents are **temporary execution entities** created for bounded tasks under KORA’s coordination.

| Agents are | Agents are not |
| --- | --- |
| Ephemeral workers with explicit scope | Council members |
| Task executors that report back into KORA’s request lifecycle | A parallel “Brainiac” identity |
| Optional implementation mechanisms for orchestration | Managers of KORA or of the Council |

**Do not conflate Council members with agents.**  
Council members are durable cognitive roles in a reasoning framework. Agents are disposable execution vehicles.

Canonical platform definition: `KORA.md`.  
Council behavior: `Council/Dynamics.md`.  
Orchestration design: Phase 13.3.

## Status

Stub — no agent runtime or framework selection in Phase 13.0.
