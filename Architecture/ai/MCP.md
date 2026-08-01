# MCP

Model Context Protocol architecture, servers, tools, and security considerations.

## Role in the KORA architecture

MCP (and related integrations) provide **tools**: external capabilities through which KORA reads or acts on the homelab environment.

| Tools / MCP own | Tools / MCP do not own |
| --- | --- |
| Bounded access to filesystem, git, Docker, Home Assistant, DNS, etc. | Platform identity (KORA / Brainiac) |
| Security and permission boundaries for external actions | Council deliberation rules |
| Live environmental facts and controlled operations | Replacement of specialized reasoning members |

Tools sit **beneath** Council reasoning in the conceptual model, not above KORA.

Canonical platform definition: `KORA.md`.  
Integration sequencing: Phase 13.4.

## Status

Stub — no MCP server implementations or technology lock-ins in Phase 13.0.
