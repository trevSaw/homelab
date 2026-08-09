"""Graphify HTTP MCP client — Graphify-specific integration (Phase 14.4).

This client reuses the generic :class:`MCPClient` for MCP Streamable HTTP
transport/protocol handling, and keeps Graphify-specific operations
(``query_graph``, ``get_node``, ``get_neighbors``, ``shortest_path``,
``graph_stats``) here. It remains a Knowledge Graph integration — NOT the
Phase 14.5 Tool Platform.
"""

from __future__ import annotations

import logging
from typing import Any

from Tools.mcp.client import MCPClient

log = logging.getLogger("kora.knowledge.graphify")


class GraphifyError(RuntimeError):
    pass


class GraphifyUnavailableError(GraphifyError):
    pass


class GraphifyClient:
    """Graphify serve-layer client built on the generic MCP client."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        retry_attempts: int = 2,
        transport: Any | None = None,
        path: str = "/mcp",
    ) -> None:
        self._mcp = MCPClient(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
            transport=transport,
            path=path,
            client_name="kora-graphify",
            client_version="14.4",
        )

    async def close(self) -> None:
        await self._mcp.close()

    async def health(self) -> bool:
        return await self._mcp.health()

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        from Tools.mcp.client import MCPUnavailableError

        try:
            return await self._mcp.call_tool(name, arguments)
        except MCPUnavailableError as exc:
            raise GraphifyUnavailableError("graphify unavailable after retries") from exc
        except Exception as exc:  # noqa: BLE001
            raise GraphifyError(f"graphify call failed: {exc}") from exc

    async def query_graph(self, question: str, **kwargs: Any) -> str:
        args: dict[str, Any] = {"question": question}
        args.update(kwargs)
        return await self.call_tool("query_graph", args)

    async def get_node(self, label: str) -> str:
        return await self.call_tool("get_node", {"label": label})

    async def get_neighbors(self, label: str, **kwargs: Any) -> str:
        args: dict[str, Any] = {"label": label}
        args.update(kwargs)
        return await self.call_tool("get_neighbors", args)

    async def shortest_path(self, source: str, target: str, **kwargs: Any) -> str:
        args: dict[str, Any] = {"source": source, "target": target}
        args.update(kwargs)
        return await self.call_tool("shortest_path", args)

    async def graph_stats(self) -> str:
        return await self.call_tool("graph_stats", {})
