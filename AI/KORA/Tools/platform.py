"""KORA Tool Platform facade.

Composes the Tool Registry, authorization, execution, and tool providers behind
a single KORA-owned boundary. The Runtime depends on this facade, not on MCP
endpoints directly. Does NOT become Knowledge/Memory authority.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from app.event_bus import EventBus, EventEnvelope

from .auth.authorizer import (
    ToolApprovalRequiredError,
    ToolAuthorizer,
    ToolDisabledError,
    ToolNotAuthorizedError,
)
from .executor.executor import ToolExecutor, ToolResult
from .models.tool import Tool, ToolRisk, tool_id
from .registry.registry import ToolRegistry

log = logging.getLogger("kora.tools.platform")


@dataclass(slots=True)
class ToolPlatform:
    registry: ToolRegistry = field(default_factory=ToolRegistry)
    authorizer: ToolAuthorizer = field(default_factory=ToolAuthorizer)
    executor: ToolExecutor = field(default_factory=ToolExecutor)
    event_bus: EventBus | None = None

    def register_tool(self, tool: Tool, *, enabled: bool = False) -> Tool:
        registered = self.registry.register(tool)
        if enabled:
            self.registry.set_enabled(tool.tool_id, True)
        self._publish("tool.registered", {"tool_id": tool.tool_id, "name": tool.name})
        return registered

    def set_enabled(self, tool_id: str, enabled: bool) -> Tool:
        tool = self.registry.set_enabled(tool_id, enabled)
        self._publish("tool.enabled" if enabled else "tool.disabled", {"tool_id": tool_id})
        return tool

    def discover_tools(self, provider_name: str, raw_tools: list[dict[str, Any]], *, enabled: bool = False) -> int:
        """Register discovered tools (discovery != authorization). New tools start
        disabled unless ``enabled`` is requested."""
        count = 0
        for raw in raw_tools:
            name = str(raw.get("name") or "")
            if not name:
                continue
            input_schema = dict(raw.get("input_schema") or {})
            risk = ToolRisk.READ_ONLY
            self.registry.upsert_from_discovery(
                name=name,
                description=str(raw.get("description") or ""),
                input_schema=input_schema,
                provider=provider_name,
                risk=risk,
                enabled_by_default=enabled,
            )
            count += 1
        self._publish("tool.discovered", {"provider": provider_name, "count": count})
        return count

    def list_tools(self, *, enabled_only: bool = False) -> list[Tool]:
        return self.registry.list_enabled() if enabled_only else self.registry.list_tools()

    def authorize(self, tool_id: str) -> Tool:
        """Raise unless the tool is enabled and authorized under policy."""
        tool = self.registry.require(tool_id)
        self.authorizer.authorize(tool)
        return tool

    async def invoke(
        self,
        tool_id: str,
        arguments: dict[str, Any],
        *,
        timeout_seconds: float | None = None,
    ) -> ToolResult:
        tool = self.registry.require(tool_id)
        self._publish("tool.invocation.started", {"tool_id": tool_id})
        try:
            self.authorizer.authorize(tool)
        except ToolDisabledError:
            result = ToolExecutor._failure(tool, arguments, error="tool disabled")
            self._publish("tool.invocation.failed", {"tool_id": tool_id, "error": result.error})
            return result
        except ToolApprovalRequiredError:
            result = ToolExecutor._failure(tool, arguments, error="approval required")
            self._publish("tool.invocation.failed", {"tool_id": tool_id, "error": result.error})
            return result
        except ToolNotAuthorizedError:
            result = ToolExecutor._failure(tool, arguments, error="not authorized")
            self._publish("tool.invocation.failed", {"tool_id": tool_id, "error": result.error})
            return result

        result = await self.executor.execute(tool, arguments, timeout_seconds=timeout_seconds)
        event = "tool.invocation.completed" if result.success else "tool.invocation.failed"
        self._publish(
            event,
            {
                "tool_id": tool_id,
                "invocation_id": result.invocation_id,
                "success": result.success,
                "error": result.error,
            },
        )
        return result

    async def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "enabled_tools": len(self.registry.list_enabled()),
            "registered_tools": len(self.registry.list_tools()),
        }

    def _publish(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.event_bus is None:
            return
        try:
            self.event_bus.publish(
                EventEnvelope(
                    event_type=event_type,
                    source="tool-platform",
                    payload=payload,
                )
            )
        except Exception:  # noqa: BLE001
            log.debug("failed to publish tool event %s", event_type)
