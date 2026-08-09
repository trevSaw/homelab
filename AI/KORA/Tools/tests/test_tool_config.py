"""Tests for Tool Platform configuration and builder."""

import yaml

from ..config.tool_config import ToolConfig
from ..builder import build_tool_platform


def test_config_from_dict_preserves_tools():
    data = {
        "enabled": True,
        "tools": [
            {"name": "ollama.list_models", "provider": "ollama", "risk": "read_only", "enabled": True},
        ],
    }
    cfg = ToolConfig.from_dict(data)
    assert len(cfg.tools) == 1
    assert cfg.tools[0].name == "ollama.list_models"
    assert cfg.tools[0].enabled is True


def test_with_env_overrides_preserves_tools():
    data = {
        "tools": [
            {"name": "x", "provider": "p", "risk": "read_only", "enabled": True},
        ],
    }
    cfg = ToolConfig.from_dict(data).with_env_overrides()
    assert [t.name for t in cfg.tools] == ["x"]


def test_builder_registers_configured_tools(tmp_path):
    data = yaml.safe_load(
        (tmp_path / "tools.yaml").write_text("""
enabled: true
tools:
  - name: ollama.list_models
    provider: ollama
    risk: read_only
    enabled: true
""", encoding="utf-8")
    ) if False else {
        "enabled": True,
        "tools": [
            {"name": "ollama.list_models", "provider": "ollama", "risk": "read_only", "enabled": True},
        ],
    }
    cfg = ToolConfig.from_dict(data)
    platform = build_tool_platform(config=cfg, ollama_base_url="http://ollama:11434")
    names = [t.name for t in platform.list_tools()]
    assert "ollama.list_models" in names
    assert platform.list_tools(enabled_only=True)


def test_builder_does_not_enable_mcp_discovered_tools():
    data = {
        "mcp_servers": [
            {"name": "metrics", "id": "m1", "base_url": "http://metrics:8080", "enabled": True},
        ],
        "tools": [],
    }
    cfg = ToolConfig.from_dict(data)
    platform = build_tool_platform(config=cfg)
    # Discovery would register tools disabled; none configured, so none enabled.
    assert platform.list_tools(enabled_only=True) == []
