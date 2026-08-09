"""Tests for the Tool model, risk classification, and Tool Registry."""

import pytest

from ..models.tool import (
    Tool,
    ToolRisk,
    ToolState,
    requires_approval_for_risk,
    tool_id,
)
from ..registry.registry import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
    ToolRegistry,
)


def test_tool_id_is_deterministic():
    a = tool_id("list-models", "ollama")
    b = tool_id("list-models", "ollama")
    assert a == b
    assert a != tool_id("list-models", "docker")


def test_risk_approval_policy():
    assert requires_approval_for_risk(ToolRisk.READ_ONLY) is False
    assert requires_approval_for_risk(ToolRisk.LOW_RISK_MUTATION) is False
    assert requires_approval_for_risk(ToolRisk.HIGH_RISK_MUTATION) is True
    assert requires_approval_for_risk(ToolRisk.DESTRUCTIVE) is True


def _tool(name="list-models", provider="ollama", risk=ToolRisk.READ_ONLY, enabled=False):
    return Tool(
        tool_id=tool_id(name, provider),
        name=name,
        description="desc",
        input_schema={"type": "object", "properties": {}},
        risk=risk,
        provider=provider,
        enabled=enabled,
    )


def test_registry_register_lookup_discovery():
    registry = ToolRegistry()
    tool = _tool()
    registry.register(tool)
    assert registry.require(tool.tool_id).name == "list-models"
    assert len(registry.list_tools()) == 1
    assert registry.find_by_name("list-models") == [tool]
    assert registry.list_by_provider("ollama") == [tool]


def test_registry_rejects_duplicate_unless_replace():
    registry = ToolRegistry()
    registry.register(_tool())
    with pytest.raises(ToolAlreadyRegisteredError):
        registry.register(_tool())
    registry.register(_tool(), replace=True)  # ok
    assert len(registry.list_tools()) == 1


def test_registry_enable_disable():
    registry = ToolRegistry()
    tool = _tool()
    registry.register(tool)
    registry.set_enabled(tool.tool_id, True)
    assert registry.require(tool.tool_id).enabled is True
    assert [t.tool_id for t in registry.list_enabled()] == [tool.tool_id]
    registry.set_enabled(tool.tool_id, False)
    assert registry.list_enabled() == []


def test_registry_upsert_from_discovery_defaults_disabled():
    registry = ToolRegistry()
    tool = registry.upsert_from_discovery(
        name="get-metrics",
        description="read metrics",
        input_schema={},
        provider="prometheus",
        risk=ToolRisk.READ_ONLY,
    )
    assert tool.enabled is False  # discovery != authorization
    assert tool.provider == "prometheus"


def test_registry_require_missing_raises():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        registry.require("nope")
