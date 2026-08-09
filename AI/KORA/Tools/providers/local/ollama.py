"""Local Ollama read-only tool provider.

Provides safe, read-only tools backed by the local Ollama instance (list models,
list running models). These require no external MCP server and are governed by
the same Tool Platform authorization. No mutating/destructive tools are exposed.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from ...executor.executor import ToolProvider, ToolProviderError

log = logging.getLogger("kora.tools.ollama")


class OllamaLocalToolProvider:
    """Read-only Ollama tools (list models / list running models)."""

    TOOLS = ("ollama.list_models", "ollama.list_running")

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=timeout_seconds, transport=transport)

    async def close(self) -> None:
        await self._client.aclose()

    def supports(self, tool: Any) -> bool:
        return tool.name in self.TOOLS

    async def invoke(self, tool: Any, arguments: dict[str, Any]) -> Any:
        if tool.name == "ollama.list_models":
            return await self._list_models()
        if tool.name == "ollama.list_running":
            return await self._list_running()
        raise ToolProviderError(f"unknown ollama tool: {tool.name}")

    async def _list_models(self) -> Any:
        try:
            response = await self._client.get(f"{self._base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models") or []
            return {"models": [m.get("name") for m in models]}
        except Exception as exc:  # noqa: BLE001
            raise ToolProviderError(f"ollama list models failed: {exc}") from exc

    async def _list_running(self) -> Any:
        try:
            response = await self._client.get(f"{self._base_url}/api/ps")
            response.raise_for_status()
            running = response.json().get("models") or []
            return {"running": [m.get("name") for m in running]}
        except Exception as exc:  # noqa: BLE001
            raise ToolProviderError(f"ollama list running failed: {exc}") from exc
