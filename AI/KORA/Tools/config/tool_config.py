"""Tool Platform configuration.

Tools are statically configured (allowed tools with explicit risk/enabled state)
plus optionally discovered from configured MCP servers. Discovery does NOT imply
authorization. No environment-specific values are hard-coded.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from ..models.tool import ToolRisk


@dataclass(frozen=True, slots=True)
class MCPToolServerConfig:
    server_name: str
    server_id: str
    base_url: str
    api_key: str = ""
    timeout_seconds: float = 30.0
    enabled: bool = False


@dataclass(frozen=True, slots=True)
class ConfiguredTool:
    name: str
    provider: str
    risk: str = ToolRisk.READ_ONLY.value
    enabled: bool = True
    requires_approval: bool = False
    description: str = ""


@dataclass(frozen=True, slots=True)
class ToolConfig:
    enabled: bool = True
    read_only_automatic: bool = True
    default_timeout_seconds: float = 15.0
    servers: tuple[MCPToolServerConfig, ...] = ()
    tools: tuple[ConfiguredTool, ...] = ()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ToolConfig":
        servers_raw = value.get("mcp_servers") or []
        servers = tuple(
            MCPToolServerConfig(
                server_name=str(s.get("name") or ""),
                server_id=str(s.get("id") or s.get("name") or ""),
                base_url=str(s.get("base_url") or ""),
                api_key=str(s.get("api_key") or ""),
                timeout_seconds=float(s.get("timeout_seconds", 30.0)),
                enabled=bool(s.get("enabled", False)),
            )
            for s in servers_raw
        )
        tools_raw = value.get("tools") or []
        tools = tuple(
            ConfiguredTool(
                name=str(t.get("name") or ""),
                provider=str(t.get("provider") or ""),
                risk=str(t.get("risk") or ToolRisk.READ_ONLY.value),
                enabled=bool(t.get("enabled", True)),
                requires_approval=bool(t.get("requires_approval", False)),
                description=str(t.get("description") or ""),
            )
            for t in tools_raw
        )
        return cls(
            enabled=bool(value.get("enabled", True)),
            read_only_automatic=bool(value.get("read_only_automatic", True)),
            default_timeout_seconds=float(value.get("default_timeout_seconds", 15.0)),
            servers=servers,
            tools=tools,
        )

    @classmethod
    def from_env(cls) -> "ToolConfig":
        """Environment overrides applied on top of defaults."""
        cfg = cls()
        return cls(
            enabled=_env_bool("KORA_TOOLS_ENABLED", cfg.enabled),
            read_only_automatic=_env_bool("KORA_TOOLS_READ_ONLY_AUTOMATIC", cfg.read_only_automatic),
            default_timeout_seconds=float(
                os.environ.get("KORA_TOOLS_TIMEOUT_SECONDS", cfg.default_timeout_seconds)
            ),
            servers=cfg.servers,
            tools=cfg.tools,
        )

    def with_env_overrides(self) -> "ToolConfig":
        """Return a copy preserving YAML-loaded servers/tools with env overrides."""
        return ToolConfig(
            enabled=_env_bool("KORA_TOOLS_ENABLED", self.enabled),
            read_only_automatic=_env_bool(
                "KORA_TOOLS_READ_ONLY_AUTOMATIC", self.read_only_automatic
            ),
            default_timeout_seconds=float(
                os.environ.get("KORA_TOOLS_TIMEOUT_SECONDS", self.default_timeout_seconds)
            ),
            servers=self.servers,
            tools=self.tools,
        )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}
