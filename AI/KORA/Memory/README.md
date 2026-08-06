# Memory Runtime

**Status:** Phase 14.2A foundation implemented

The KORA process now contains logical Event Bus, Memory Runtime, and Approval
Engine services. Memory Runtime consumes relevant general events, requires
explicit candidate data, and manages ephemeral proposals only.

Honcho remains a future persistence candidate per ADR-0005. There are no
durable writes, retrieval paths, autonomous candidate extraction, or approval
UI in Phase 14.2A.

Runtime: `AI/KORA/Runtime/app/{event_bus,memory_runtime,memory_models,approval_engine}.py`

Configuration: `AI/KORA/Config/memory_runtime.yaml`

Architecture decision: `Architecture/decisions/ADR-14.2A-001-Internal-Event-Bus.md`
