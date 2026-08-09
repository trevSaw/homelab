"""Tests for the generic MCP client and the MCP tool provider."""

import asyncio
import json

import httpx

from ..mcp.client import MCPClient, MCPError, MCPUnavailableError, MCPToolInfo
from ..providers.mcp import MCPToolProvider
from ..executor.executor import ToolExecutor
from ..models.tool import Tool, ToolRisk, tool_id
from ..registry.registry import ToolRegistry
from ..platform import ToolPlatform


class _MCPHandler(httpx.MockTransport):
    def __init__(self, *, fail=False, unavailable=False, tools=None):
        super().__init__(handler=self._handler)
        self._fail = fail
        self._unavailable = unavailable
        self._tools = tools or [
            {"name": "list-metrics", "description": "read metrics", "inputSchema": {"type": "object"}}
        ]
        self.session_id = "sess-1"

    def _handler(self, request: httpx.Request) -> httpx.Response:
        if self._unavailable:
            raise httpx.ConnectError("mcp down")
        if self._fail:
            return httpx.Response(401, json={"error": "unauthorized"})
        payload = json.loads(request.content)
        method = payload.get("method")
        if method == "initialize":
            return httpx.Response(
                200,
                headers={"mcp-session-id": self.session_id},
                json={"jsonrpc": "2.0", "id": payload.get("id"), "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "test", "version": "1"},
                }},
            )
        if method == "notifications/initialized":
            return httpx.Response(202, json={})
        if method == "tools/list":
            return httpx.Response(
                200,
                json={"jsonrpc": "2.0", "id": payload.get("id"), "result": {"tools": self._tools}},
            )
        if method == "tools/call":
            return httpx.Response(
                200,
                json={"jsonrpc": "2.0", "id": payload.get("id"), "result": {
                    "content": [{"type": "text", "text": "metric value: 42"}]
                }},
            )
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": payload.get("id"), "result": {}})


def _client(handler) -> MCPClient:
    return MCPClient(base_url="http://mcp:8080", api_key="k", transport=handler)


def test_mcp_initialize_and_health():
    handler = _MCPHandler()
    client = _client(handler)
    assert asyncio.run(client.health()) is True
    caps = asyncio.run(client.initialize())
    assert "tools" in caps
    asyncio.run(client.close())


def test_mcp_discovery_lists_tools():
    handler = _MCPHandler()
    client = _client(handler)
    tools = asyncio.run(client.list_tools())
    assert len(tools) == 1
    assert tools[0].name == "list-metrics"
    assert tools[0].input_schema == {"type": "object"}
    assert isinstance(tools[0], MCPToolInfo)
    asyncio.run(client.close())


def test_mcp_invocation():
    handler = _MCPHandler()
    client = _client(handler)
    text = asyncio.run(client.call_tool("list-metrics", {}))
    assert "42" in text
    asyncio.run(client.close())


def test_mcp_auth_failure():
    handler = _MCPHandler(fail=True)
    client = _client(handler)
    try:
        asyncio.run(client.list_tools())
        assert False, "expected MCPError"
    except MCPError:
        pass
    asyncio.run(client.close())


def test_mcp_unavailable():
    client = _client(_MCPHandler(unavailable=True))
    try:
        asyncio.run(client.list_tools())
        assert False, "expected MCPUnavailableError"
    except MCPUnavailableError:
        pass
    asyncio.run(client.close())


def test_mcp_provider_discovery_to_registry():
    handler = _MCPHandler()
    client = _client(handler)
    provider = MCPToolProvider(mcp_client=client, server_name="metrics", server_id="m1")
    platform = ToolPlatform()
    raw = asyncio.run(provider.discover())
    platform.discover_tools("metrics", raw)
    tools = platform.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "list-metrics"
    assert tools[0].enabled is False  # discovery != authorization
    asyncio.run(client.close())


def test_mcp_provider_invoke_via_platform():
    handler = _MCPHandler()
    client = _client(handler)
    provider = MCPToolProvider(mcp_client=client, server_name="metrics", server_id="m1")
    platform = ToolPlatform()
    platform.executor = ToolExecutor(providers=[provider])
    raw = asyncio.run(provider.discover())
    platform.discover_tools("metrics", raw)
    tool = platform.list_tools()[0]
    platform.set_enabled(tool.tool_id, True)
    result = asyncio.run(platform.invoke(tool.tool_id, {}))
    assert result.success is True
    assert "42" in str(result.result)
    asyncio.run(client.close())
