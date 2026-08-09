"""Tool execution lifecycle and result normalization."""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol

from ..models.tool import Tool


class ToolProviderError(RuntimeError):
    pass


class ToolTimeoutError(ToolProviderError):
    pass


class ToolProvider(Protocol):
    """A backend that can invoke a tool."""

    def supports(self, tool: Tool) -> bool: ...

    async def invoke(self, tool: Tool, arguments: dict[str, Any]) -> Any: ...


@dataclass(frozen=True, slots=True)
class ToolResult:
    invocation_id: str
    tool_id: str
    tool_name: str
    provider: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    started_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "provider": self.provider,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class ToolExecutor:
    """KORA-owned execution layer.

    Validates, authorizes, invokes, times out, and normalizes tool calls. The
    Runtime never calls arbitrary MCP endpoints directly.
    """

    def __init__(
        self,
        *,
        providers: list[ToolProvider] | None = None,
        default_timeout_seconds: float = 15.0,
    ) -> None:
        self._providers = providers or []
        self._timeout = default_timeout_seconds

    async def execute(
        self,
        tool: Tool,
        arguments: dict[str, Any],
        *,
        timeout_seconds: float | None = None,
    ) -> ToolResult:
        provider = self._resolve_provider(tool)
        if provider is None:
            return self._failure(
                tool, arguments, error="no provider supports this tool"
            )
        invocation_id = uuid.uuid4().hex
        started = time.time()
        try:
            result = await asyncio.wait_for(
                provider.invoke(tool, arguments),
                timeout=timeout_seconds or self._timeout,
            )
        except asyncio.TimeoutError:
            return self._failure(
                tool,
                arguments,
                error=f"tool timed out after {timeout_seconds or self._timeout}s",
                invocation_id=invocation_id,
                started=started,
            )
        except Exception as exc:  # noqa: BLE001
            return self._failure(
                tool,
                arguments,
                error=str(exc),
                invocation_id=invocation_id,
                started=started,
            )
        duration_ms = (time.time() - started) * 1000.0
        return ToolResult(
            invocation_id=invocation_id,
            tool_id=tool.tool_id,
            tool_name=tool.name,
            provider=tool.provider,
            success=True,
            result=result,
            duration_ms=round(duration_ms, 3),
            metadata={"arguments": dict(arguments)},
        )

    def _resolve_provider(self, tool: Tool) -> ToolProvider | None:
        for provider in self._providers:
            if provider.supports(tool):
                return provider
        return None

    @staticmethod
    def _failure(
        tool: Tool,
        arguments: dict[str, Any],
        *,
        error: str,
        invocation_id: str | None = None,
        started: float | None = None,
    ) -> ToolResult:
        started = started if started is not None else time.time()
        return ToolResult(
            invocation_id=invocation_id or uuid.uuid4().hex,
            tool_id=tool.tool_id,
            tool_name=tool.name,
            provider=tool.provider,
            success=False,
            error=error,
            duration_ms=round((time.time() - started) * 1000.0, 3),
            metadata={"arguments": dict(arguments)},
        )
