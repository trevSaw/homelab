# Hermes — Thin Execution Layer

ADR-0004 substrate. Hermes is **not** KORA.

## Phase 14.1 posture

- Keep Hermes deployed for continuity and later Distributed stages
- Primary Solo chat path does **not** route through Hermes
- Hermes must not own product identity, Council, Memory SoT, or ungated Execute

Registration: `../KORA/Config/hermes_registration.yaml`  
Compose SoT: `services/hermes/`
