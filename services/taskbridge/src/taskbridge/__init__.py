"""KORA Task Bridge — OpenCode execution worker bridge.

A containerized service that lets KORA (Hermes) delegate server-side
engineering tasks to OpenCode running in the same container, with explicit
execution boundaries, persistent task state, and approval gating.

Exposes:
  - REST API  (POST/GET /api/v1/tasks, approve, cancel, status)
  - Streamable HTTP MCP endpoint at /mcp (tools for KORA/Hermes)
"""

__version__ = "1.0.0"