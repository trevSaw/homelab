# KORA Council (runtime skeleton)

Phase 14.1 registers Council members for Solo conceptual mode only.
Deliberation / Simulated / Distributed Council is **not** implemented here.

Config: `../Config/council_registration.yaml`  
Architecture: `Architecture/ai/Council/`

**Phase 15 design note:** The future Council architecture is hardware-agnostic.
It supports configurable member count, model assignment, and sequential/parallel
inference. Members do not inherently require separate models; multiple archetypes
may share one local model with different role/system prompts. This is a design
note only — no Council functionality is implemented here.
