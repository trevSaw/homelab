"""Tests for Tool authorization, execution, and result normalization."""

import asyncio

import pytest

from ..auth.authorizer import (
    ToolApprovalRequiredError,
    ToolDisabledError,
    ToolNotAuthorizedError,
    ToolAuthorizer,
)
from ..executor.executor import ToolExecutor, ToolProvider, ToolProviderError, ToolResult
from ..models.tool import Tool, ToolRisk, tool_id
from ..registry.registry import ToolRegistry
from ..platform import ToolPlatform


def _tool(name="list-models", risk=ToolRisk.READ_ONLY, provider="ollama", enabled=True, requires_approval=False):
    return Tool(
        tool_id=tool_id(name, provider),
        name=name,
        description="desc",
        input_schema={"type": "object"},
        risk=risk,
        provider=provider,
        enabled=enabled,
        requires_approval=requires_approval,
    )


class FakeProvider:
    def __init__(self, *, fail=False, result="ok", supports=True):
        self._fail = fail
        self._result = result
        self._supports = supports
        self.calls = 0

    def supports(self, tool):
        return self._supports

    async def invoke(self, tool, arguments):
        self.calls += 1
        if self._fail:
            raise ToolProviderError("provider failure")
        return {"value": self._result}


def test_authorizer_read_only_auto():
    auth = ToolAuthorizer()
    auth.authorize(_tool())  # enabled read-only -> ok
    destructive = _tool(name="wipe", risk=ToolRisk.DESTRUCTIVE)
    auth.grant_approval(destructive.tool_id)
    auth.authorize(destructive)


def test_authorizer_disabled_rejected():
    auth = ToolAuthorizer()
    with pytest.raises(ToolDisabledError):
        auth.authorize(_tool(enabled=False))


def test_authorizer_destructive_requires_approval():
    auth = ToolAuthorizer()
    with pytest.raises(ToolApprovalRequiredError):
        auth.authorize(_tool(name="wipe", risk=ToolRisk.DESTRUCTIVE))


def test_authorizer_not_auto_without_flag():
    auth = ToolAuthorizer(read_only_automatic=False)
    with pytest.raises(ToolNotAuthorizedError):
        auth.authorize(_tool(name="restart", risk=ToolRisk.LOW_RISK_MUTATION))


def test_executor_success_normalizes_result():
    provider = FakeProvider()
    executor = ToolExecutor(providers=[provider])
    tool = _tool()
    result = asyncio.run(executor.execute(tool, {"model": "x"}))
    assert result.success is True
    assert result.result == {"value": "ok"}
    assert result.tool_name == "list-models"
    assert result.provider == "ollama"
    assert result.duration_ms >= 0


def test_executor_provider_failure():
    executor = ToolExecutor(providers=[FakeProvider(fail=True)])
    result = asyncio.run(executor.execute(_tool(), {}))
    assert result.success is False
    assert "provider failure" in result.error


def test_executor_timeout():
    class SlowProvider:
        def supports(self, tool):
            return True

        async def invoke(self, tool, arguments):
            await asyncio.sleep(5)

    executor = ToolExecutor(providers=[SlowProvider()], default_timeout_seconds=0.05)
    result = asyncio.run(executor.execute(_tool(), {}))
    assert result.success is False
    assert "timed out" in result.error


def test_executor_no_provider():
    executor = ToolExecutor(providers=[])
    result = asyncio.run(executor.execute(_tool(), {}))
    assert result.success is False
    assert "no provider" in result.error


def test_tool_platform_invoke_authorized_read_only():
    platform = ToolPlatform()
    tool = _tool()
    platform.registry.register(tool)
    platform.set_enabled(tool.tool_id, True)
    platform.executor = ToolExecutor(providers=[FakeProvider()])
    result = asyncio.run(platform.invoke(tool.tool_id, {}))
    assert result.success is True


def test_tool_platform_invoke_disabled_fails():
    platform = ToolPlatform()
    tool = _tool(enabled=False)
    platform.registry.register(tool)
    platform.executor = ToolExecutor(providers=[FakeProvider()])
    result = asyncio.run(platform.invoke(tool.tool_id, {}))
    assert result.success is False
    assert "disabled" in result.error


def test_tool_platform_destructive_requires_approval():
    platform = ToolPlatform()
    tool = _tool(name="wipe", risk=ToolRisk.DESTRUCTIVE, requires_approval=True)
    platform.registry.register(tool)
    platform.set_enabled(tool.tool_id, True)
    platform.executor = ToolExecutor(providers=[FakeProvider()])
    result = asyncio.run(platform.invoke(tool.tool_id, {}))
    assert result.success is False
    assert "approval" in result.error

    platform.authorizer.grant_approval(tool.tool_id)
    result = asyncio.run(platform.invoke(tool.tool_id, {}))
    assert result.success is True
