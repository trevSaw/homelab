"""Graphify HTTP MCP client.

A minimal MCP Streamable HTTP (JSON-RPC 2.0) client for the Graphify serve layer
(``python -m graphify.serve graph.json --transport http --host 0.0.0.0
--port 8080 --api-key KEY --json-response``).

This talks to a REAL Graphify server exposing the tools documented by Graphify
(``query_graph``, ``get_node``, ``get_neighbors``, ``shortest_path``,
``graph_stats``). A ``transport`` may be injected for tests (mirrors the
Chroma/Honcho adapter pattern).
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import httpx

log = logging.getLogger("kora.knowledge.graphify")


class GraphifyError(RuntimeError):
    pass


class GraphifyUnavailableError(GraphifyError):
    pass


class GraphifyClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 30.0,
        retry_attempts: int = 2,
        transport: httpx.AsyncBaseTransport | None = None,
        path: str = "/mcp",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._retry_attempts = max(1, retry_attempts)
        self._path = path
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            transport=transport,
        )
        self._session_id: str | None = None

    async def close(self) -> None:
        await self._client.aclose()

    async def health(self) -> bool:
        try:
            await self._initialize()
            return True
        except GraphifyError:
            return False

    async def _initialize(self) -> None:
        """Establish a stateful MCP session and capture the session id."""
        if self._session_id:
            return
        request_id = str(uuid.uuid4())
        response = await self._rpc(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "kora", "version": "14.4"},
                },
            },
            establish=True,
        )
        if not self._session_id:
            raise GraphifyError("graphify did not return an mcp-session-id")
        # Notify the server that initialization completed.
        try:
            await self._rpc(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
                no_response=True,
            )
        except GraphifyError:
            pass

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
                    raise GraphifyError("graphify rejected the API key")
                if response.status_code == 404:
                    # Session expired or not found; reset and retry initialize.
                    self._session_id = None
                    raise GraphifyError("graphify session not found")
                if response.status_code >= 400:
                    raise GraphifyError(
                        f"graphify rejected request: HTTP {response.status_code}"
                    )
                if no_response:
                    return {}
                if establish:
                    self._session_id = response.headers.get("mcp-session-id")
                body = response.json()
                if isinstance(body, dict) and body.get("error"):
                    raise GraphifyError(
                        f"graphify RPC error: {json.dumps(body['error'])[:500]}"
                    )
                return body
            except GraphifyError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
        raise GraphifyUnavailableError("graphify unavailable after retries") from last_error

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        await self._initialize()
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
