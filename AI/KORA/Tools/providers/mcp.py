"""MCP tool provider for the Tool Platform.

Bridges the Tool Platform to a generic :class:`MCPClient`. Discovery via
``tools/list`` populates the registry (discovery != authorization). Invocation
calls ``tools/call`` and normalizes results.
"""

from __future__ import annotations

import logging
from typing import Any

from ..mcp.client import MCPClient, MCPError
from ..models.tool import Tool, ToolRisk
from ..executor.executor import ToolProvider, ToolProviderError

log = logging.getLogger("kora.tools.mcp_provider")


class MCPToolProvider:
    def __init__(self, *, mcp_client: MCPClient, server_name: str, server_id: str) -> None:
        self._client = mcp_client
        self._server_name = server_name
        self._server_id = server_id

    @property
    def server_name(self) -> str:
        return self._server_name

    def supports(self, tool: Tool) -> bool:
        return tool.provider == self._server_name

    async def discover(self) -> list[dict[str, Any]]:
        """Return raw tool metadata from the MCP server (tools/list)."""
        try:
            tools = await self._client.list_tools()
        except MCPError as exc:
            log.warning("MCP discovery failed for %s: %s", self._server_name, exc)
            return []
        return [t.to_dict() for t in tools]

    async def invoke(self, tool: Tool, arguments: dict[str, Any]) -> Any:
        try:
            return await self._client.call_tool(tool.name, arguments)
        except MCPError as exc:
            raise ToolProviderError(f"mcp invocation failed: {exc}") from exc

    @staticmethod
    def risk_for_tool(name: str, input_schema: dict[str, Any]) -> ToolRisk:
        """Conservative default: discovered tools are treated as read-only until
        explicitly configured otherwise. Consequential tools must be configured
        with an explicit risk."""
        return ToolRisk.READ_ONLY
