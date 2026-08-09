"""Composition boundary for the Tool Platform.

Builds the ToolPlatform from configuration: registers statically-configured
tools, attaches local + MCP providers, and optionally discovers MCP tools.
"""

from __future__ import annotations

from typing import Any

from .config.tool_config import ToolConfig, MCPToolServerConfig
from .executor.executor import ToolExecutor
from .mcp.client import MCPClient
from .models.tool import Tool, ToolRisk, tool_id
from .platform import ToolPlatform
from .providers.local.ollama import OllamaLocalToolProvider
from .providers.mcp import MCPToolProvider


def build_tool_platform(
    *,
    config: ToolConfig,
    event_bus: Any | None = None,
    ollama_base_url: str = "http://ollama:11434",
    mcp_transports: dict[str, Any] | None = None,
) -> ToolPlatform:
    """Build the Tool Platform from configuration.

    ``mcp_transports`` maps server_name → httpx transport for tests.
    """
    providers = []
    mcp_providers: list[MCPToolProvider] = []

    # Local read-only Ollama provider.
    ollama_provider = OllamaLocalToolProvider(base_url=ollama_base_url)
    providers.append(ollama_provider)

    # Configured MCP providers.
    transports = mcp_transports or {}
    for server in config.servers:
        if not server.enabled or not server.base_url:
            continue
        client = MCPClient(
            base_url=server.base_url,
            api_key=server.api_key or None,
            timeout_seconds=server.timeout_seconds,
            transport=transports.get(server.server_name),
            client_name="kora-tools",
            client_version="14.5",
        )
        mcp_provider = MCPToolProvider(
            mcp_client=client,
            server_name=server.server_name,
            server_id=server.server_id,
        )
        providers.append(mcp_provider)
        mcp_providers.append(mcp_provider)

    platform = ToolPlatform(
        event_bus=event_bus,
        executor=ToolExecutor(
            providers=providers,
            default_timeout_seconds=config.default_timeout_seconds,
        ),
    )

    # Register statically configured tools (explicit risk/enabled state).
    for tool in config.tools:
        risk = _parse_risk(tool.risk)
        tid = tool_id(tool.name, tool.provider)
        platform.register_tool(
            Tool(
                tool_id=tid,
                name=tool.name,
                description=tool.description,
                input_schema={"type": "object", "properties": {}},
                risk=risk,
                provider=tool.provider,
                enabled=tool.enabled,
                requires_approval=tool.requires_approval or _risk_requires_approval(risk),
            )
        )

    # Optionally discover MCP tools (discovery != authorization).
    for provider in mcp_providers:
        platform.discover_tools(provider.server_name, [])

    return platform


def _parse_risk(value: str) -> ToolRisk:
    try:
        return ToolRisk(value)
    except ValueError:
        return ToolRisk.READ_ONLY


def _risk_requires_approval(risk: ToolRisk) -> bool:
    return risk in {ToolRisk.HIGH_RISK_MUTATION, ToolRisk.DESTRUCTIVE}
