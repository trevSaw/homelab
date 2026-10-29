"""Routing regression tests for the canonical KORA plugin."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_DIR.parent))

import kora as plugin  # noqa: E402
import kora.kora_classify as kc  # noqa: E402


@pytest.mark.parametrize(
    "text",
    [
        "Traefik is returning 502 for the Jellyfin route; investigate",
        "Why is the sonarr container unhealthy? Check docker logs.",
        "The docker compose service for radarr keeps crashing, can you diagnose it?",
        "Help me troubleshoot why my Traefik router is not working",
        "Docker containers are not starting after reboot, investigate",
        "restart the sonarr container",
    ],
)
def test_infrastructure_troubleshooting_is_operational_and_tool_enabled(text):
    classification = kc.classify(text)
    strategy = kc.select_strategy(classification)

    assert classification["label"] == "operational"
    assert strategy["name"] == "solo_operational"
    assert strategy["query_tools"] is True
    assert "tools" in strategy["stores_queried"]
    assert strategy["budgets"]["tools"] == 1


@pytest.mark.parametrize(
    "text",
    [
        "What is Docker?",
        "How does Traefik route traffic?",
        "Explain how Docker Compose networking works",
        "What does a Traefik middleware do?",
        "Why do Docker containers crash?",
        "Can you explain why Docker containers crash?",
        "Why do we use Traefik?",
        "Can you explain how Docker Compose networking works?",
    ],
)
def test_conceptual_infrastructure_questions_remain_non_tool(text):
    classification = kc.classify(text)
    strategy = kc.select_strategy(classification)

    assert classification["label"] not in kc.FORBIDDEN_LABELS
    assert strategy["query_tools"] is False
    assert "tools" not in strategy["stores_queried"]


@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("delete the sonarr volume", "execute_forbidden"),
        ("wipe the zfs dataset now", "execute_forbidden"),
        ("docker compose down -v", "execute_forbidden"),
        ("restart all containers now", "execute_forbidden"),
        ("disable traefik auth", "administrative_forbidden"),
    ],
)
def test_destructive_and_admin_requests_keep_governance(text, label):
    classification = kc.classify(text)
    strategy = kc.select_strategy(classification)

    assert classification["label"] == label
    assert classification["label"] in kc.FORBIDDEN_LABELS
    assert strategy["query_tools"] is False


def test_governance_blocks_destructive_and_unconfirmed_writes():
    assert plugin.pre_tool_call(tool_name="kora.wipe_volume", session_id="t")["action"] == "block"
    assert plugin.pre_tool_call(tool_name="kora.docker_remove", session_id="t")["action"] == "block"

    blocked = plugin.pre_tool_call(
        tool_name="kora.docker_restart",
        tool_args={"name": "sonarr", "confirm": False},
        session_id="t",
    )
    assert blocked["action"] == "block"

    assert plugin.pre_tool_call(
        tool_name="kora.docker_restart",
        tool_args={"name": "sonarr", "confirm": True},
        session_id="t",
    ) is None
    assert plugin.pre_tool_call(
        tool_name="kora.docker_logs",
        tool_args={"name": "sonarr"},
        session_id="t",
    ) is None


class _RecordingContext:
    def __init__(self):
        self.hooks = {}
        self.tools = []

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def register_tool(self, name, group, schema, handler, **kwargs):
        self.tools.append(name)

    def register_terminal_environment_provider(self, provider):
        self.provider = provider


def test_intended_tools_are_registered_and_delegation_path_is_present():
    ctx = _RecordingContext()
    plugin.register(ctx)

    assert plugin.DOCKER_ADMIN_TOOLS <= set(ctx.tools)
    assert "kora.knowledge_query" in ctx.tools
    assert "kora.qbit_torrents" in ctx.tools
    assert {"pre_llm_call", "pre_tool_call", "transform_llm_output"} <= set(ctx.hooks)

    context = plugin.pre_llm_call(
        user_message="Traefik is returning 502 for the Jellyfin route; investigate",
        turn_id="routing-test",
        session_id="routing-test",
        model="test-model",
    )
    assert '"classification": "operational"' in context
    assert '"strategy": "solo_operational"' in context
    assert '"services_used": ["tools"]' in context
    assert "kora.docker_list" in context
    assert "delegate_task" in context
    assert "OpenCode Go" in context
