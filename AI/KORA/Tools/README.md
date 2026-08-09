# KORA Tool Platform (Phase 14.5)

**Status:** ✅ Implemented and validated

**Capability:** **KORA can interact with the world.**

The Tool Platform provides governed tool registration, discovery, authorization,
execution, and result normalization under KORA Runtime.

- **Tool abstraction** — `AI/KORA/Tools/models/tool.py`
- **Registry** — `AI/KORA/Tools/registry/registry.py`
- **Authorization** — `AI/KORA/Tools/auth/authorizer.py`
- **Execution** — `AI/KORA/Tools/executor/executor.py`
- **Generic MCP** — `AI/KORA/Tools/mcp/client.py`
- **MCP provider** — `AI/KORA/Tools/providers/mcp.py`
- **Local Ollama tools** — `AI/KORA/Tools/providers/local/ollama.py`
- **Facade** — `AI/KORA/Tools/platform.py`
- **Config** — `AI/KORA/Config/tools.yaml`

## Boundaries

- Knowledge ≠ Memory ≠ Tools. Tool results never auto-become Knowledge or Memory.
- Graphify's MCP integration is a Knowledge Graph integration, not the Tool
  Platform.
- Discovery ≠ authorization; consequential tools require approval.
- No autonomous tool loops; no arbitrary MCP endpoint trust.

## Safe default tools

`ollama.list_models` and `ollama.list_running` are registered read-only by
default (`AI/KORA/Config/tools.yaml`).
