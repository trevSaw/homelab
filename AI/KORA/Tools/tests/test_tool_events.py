"""Tests for Tool Platform EventBus lifecycle events."""

import asyncio

from app.event_bus import InProcessEventBus, EventEnvelope

from ..executor.executor import ToolExecutor, ToolProvider
from ..models.tool import Tool, ToolRisk, tool_id
from ..platform import ToolPlatform


class _OkProvider:
    def supports(self, tool):
        return True

    async def invoke(self, tool, arguments):
        return {"ok": True}


def _tool(name="read-x", enabled=True, risk=ToolRisk.READ_ONLY):
    return Tool(
        tool_id=tool_id(name, "test"),
        name=name,
        description="d",
        input_schema={},
        risk=risk,
        provider="test",
        enabled=enabled,
    )


def _collector(bus):
    events = []

    def handler(event: EventEnvelope):
        events.append(event.event_type)

    bus.subscribe("tool.*", handler)
    return events


def test_tool_lifecycle_events_published():
    bus = InProcessEventBus()
    events = _collector(bus)
    platform = ToolPlatform(event_bus=bus)
    tool = _tool()
    platform.register_tool(tool)
    platform.set_enabled(tool.tool_id, True)
    platform.executor = ToolExecutor(providers=[_OkProvider()])

    asyncio.run(platform.invoke(tool.tool_id, {}))
    assert "tool.registered" in events
    assert "tool.enabled" in events
    assert "tool.invocation.started" in events
    assert "tool.invocation.completed" in events


def test_tool_disabled_publishes_event():
    bus = InProcessEventBus()
    events = _collector(bus)
    platform = ToolPlatform(event_bus=bus)
    tool = _tool(enabled=False)
    platform.registry.register(tool)
    platform.set_enabled(tool.tool_id, True)
    platform.set_enabled(tool.tool_id, False)
    assert "tool.enabled" in events
    assert "tool.disabled" in events


def test_tool_invocation_failure_publishes_event():
    bus = InProcessEventBus()
    events = _collector(bus)
    platform = ToolPlatform(event_bus=bus)
    tool = _tool()
    platform.registry.register(tool)
    platform.set_enabled(tool.tool_id, True)
    platform.executor = ToolExecutor(providers=[])  # no provider -> failure
    asyncio.run(platform.invoke(tool.tool_id, {}))
    assert "tool.invocation.failed" in events
