"""KORA-owned Tool Registry.

The registry stores tool metadata, supports registration, lookup, discovery,
enable/disable state, and provider association. Discovery does NOT imply
authorization — the authorization layer decides executability.
"""

from __future__ import annotations

import threading
from typing import Any

from ..models.tool import Tool, tool_id


class ToolAlreadyRegisteredError(ValueError):
    pass


class ToolNotFoundError(KeyError):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._lock = threading.RLock()

    def register(self, tool: Tool, *, replace: bool = False) -> Tool:
        """Register a tool. By default rejects duplicates unless ``replace``."""
        with self._lock:
            existing = self._tools.get(tool.tool_id)
            if existing is not None and not replace:
                raise ToolAlreadyRegisteredError(tool.tool_id)
            self._tools[tool.tool_id] = tool
            return tool

    def unregister(self, tool_id: str) -> None:
        with self._lock:
            self._tools.pop(tool_id, None)

    def get(self, tool_id: str) -> Tool | None:
        with self._lock:
            return self._tools.get(tool_id)

    def require(self, tool_id: str) -> Tool:
        tool = self.get(tool_id)
        if tool is None:
            raise ToolNotFoundError(tool_id)
        return tool

    def list_tools(self) -> list[Tool]:
        with self._lock:
            return sorted(self._tools.values(), key=lambda t: t.name)

    def find_by_name(self, name: str) -> list[Tool]:
        with self._lock:
            return [t for t in self._tools.values() if t.name == name]

    def list_enabled(self) -> list[Tool]:
        return [t for t in self.list_tools() if t.enabled]

    def list_by_provider(self, provider: str) -> list[Tool]:
        return [t for t in self.list_tools() if t.provider == provider]

    def set_enabled(self, tool_id: str, enabled: bool) -> Tool:
        tool = self.require(tool_id)
        updated = Tool(
            tool_id=tool.tool_id,
            name=tool.name,
            description=tool.description,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            capabilities=tool.capabilities,
            risk=tool.risk,
            provider=tool.provider,
            enabled=enabled,
            requires_approval=tool.requires_approval,
            metadata=tool.metadata,
        )
        with self._lock:
            self._tools[tool_id] = updated
        return updated

    def upsert_from_discovery(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        provider: str,
        risk: Any,
        enabled_by_default: bool = False,
        requires_approval: bool | None = None,
    ) -> Tool:
        """Register or update a discovered tool. New tools start disabled unless
        configured otherwise (discovery != authorization)."""
        tid = tool_id(name, provider)
        existing = self.get(tid)
        requires_approval_final = (
            requires_approval
            if requires_approval is not None
            else (existing.requires_approval if existing else False)
        )
        tool = Tool(
            tool_id=tid,
            name=name,
            description=description,
            input_schema=input_schema,
            risk=risk,
            provider=provider,
            enabled=(existing.enabled if existing else enabled_by_default),
            requires_approval=requires_approval_final,
        )
        return self.register(tool, replace=True)
