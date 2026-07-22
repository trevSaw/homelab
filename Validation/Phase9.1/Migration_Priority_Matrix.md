## Migration Priority Matrix

| Service | Priority | Justification |
|--------|----------|---------------|
| **EchoOS / echoos** | **P0** | Duplicate name collision → must be resolved before any migration. |
| **odysseus** | **P1** | Complex configuration, many env vars, explicit healthcheck only for `searxng`; high operational risk. |
| **traefik** | **P2** | Central reverse‑proxy; any change impacts many services. |
| **ollama** | **P2** | Provides GPU‑enabled LLM backend; shared network with odysseus. |
| **portainer** | **P3** | Management UI; moderate impact. |
| **jellyfin**, **Hotio**, **n8n**, **NZBget**, **code‑server**, **authentic**, **beszel**, **beszel_agent**, **calibre‑web**, **CosmoOS**, **homepage**, **honcho**, **hermes** | **P4‑P5** (P4 for services that expose ports, P5 for low‑risk utilities) | No explicit healthchecks, no resource limits, documentation missing – low‑risk but should be migrated after higher‑priority services. |