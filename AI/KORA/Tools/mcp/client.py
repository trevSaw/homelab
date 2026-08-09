"""Generic MCP Streamable HTTP client.

A transport-neutral MCP client implementing the MCP Streamable HTTP (JSON-RPC
2.0) protocol. This is the generic layer the Tool Platform uses to talk to MCP
servers. Graphify's client reuses this for its graph-specific operations.

Supports: initialize/capability negotiation, notifications/initialized,
tools/list (discovery), tools/call (invocation), and connection lifecycle.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

log = logging.getLogger("kora.tools.mcp")


class MCPError(RuntimeError):
    pass


class MCPUnavailableError(MCPError):
    pass


@dataclass(frozen=True, slots=True)
class MCPToolInfo:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


class MCPClient:
    """Generic MCP Streamable HTTP client (JSON-RPC 2.0)."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        retry_attempts: int = 2,
        transport: httpx.AsyncBaseTransport | None = None,
        path: str = "/mcp",
        client_name: str = "kora",
        client_version: str = "14.5",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._retry_attempts = max(1, retry_attempts)
        self._path = path
        self._client_name = client_name
        self._client_version = client_version
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            transport=transport,
        )
        self._session_id: str | None = None
        self._server_capabilities: dict[str, Any] = {}

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> bool:
        try:
            await self.initialize()
            return True
        except MCPError:
            return False

    async def initialize(self) -> dict[str, Any]:
        """Perform the MCP initialize handshake and capture the session id."""
        if self._session_id:
            return self._server_capabilities
        request_id = str(uuid.uuid4())
        response = await self._rpc(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": self._client_name, "version": self._client_version},
                },
            },
            establish=True,
        )
        if not self._session_id:
            raise MCPError("MCP server did not return an mcp-session-id")
        result = response.get("result") or {}
        self._server_capabilities = result.get("capabilities") or {}
        # Notify the server that initialization completed.
        try:
            await self._rpc(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                no_response=True,
            )
        except MCPError:
            pass
        return self._server_capabilities

    async def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    async def _rpc(
        self,
        payload: dict[str, Any],
        *,
        establish: bool = False,
        no_response: bool = False,
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for _ in range(self._retry_attempts):
            try:
                response = await self._client.post(
                    f"{self._base_url}{self._path}",
                    headers=await self._headers(),
                    json=payload,
                )
                if response.status_code == 401:
                    raise MCPError("MCP server rejected the API key")
                if response.status_code == 404:
                    self._session_id = None
                    raise MCPError("MCP session not found")
                if response.status_code >= 400:
                    raise MCPError(
                        f"MCP server rejected request: HTTP {response.status_code}"
                    )
                if no_response:
                    return {}
                if establish:
                    self._session_id = response.headers.get("mcp-session-id")
                body = response.json()
                if isinstance(body, dict) and body.get("error"):
                    raise MCPError(
                        f"MCP RPC error: {json.dumps(body['error'])[:500]}"
                    )
                return body
            except MCPError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
        raise MCPUnavailableError("MCP server unavailable after retries") from last_error

    async def list_tools(self) -> list[MCPToolInfo]:
        """MCP tools/list — discover the server's exposed tools."""
        await self.initialize()
        request_id = str(uuid.uuid4())
        response = await self._rpc(
            {"jsonrpc": "2.0", "id": request_id, "method": "tools/list", "params": {}}
        )
        result = response.get("result") or {}
        tools = result.get("tools") or []
        parsed: list[MCPToolInfo] = []
        for tool in tools:
            if not isinstance(tool, dict):
                continue
            parsed.append(
                MCPToolInfo(
                    name=str(tool.get("name", "")),
                    description=str(tool.get("description", "")),
                    input_schema=dict(tool.get("inputSchema") or {}),
                    output_schema=(
                        dict(tool["outputSchema"])
                        if isinstance(tool.get("outputSchema"), dict)
                        else None
                    ),
                )
            )
        return parsed

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """MCP tools/call — invoke a tool and return its text content."""
        await self.initialize()
        request_id = str(uuid.uuid4())
        response = await self._rpc(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        result = response.get("result") or {}
        content = result.get("content") or []
        if content and isinstance(content, list):
            text_parts = [
                item.get("text", "") for item in content if isinstance(item, dict)
            ]
            return "\n".join(text_parts)
        return json.dumps(result) if result else ""
