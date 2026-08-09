"""Tool model and risk classification.

A ``Tool`` is a metadata description of a capability exposed through the Tool
Platform. Tools are distinct from Knowledge and Memory: a tool represents what
can be queried or changed now, not what KORA knows or remembers.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ToolRisk(str, Enum):
    READ_ONLY = "read_only"
    LOW_RISK_MUTATION = "low_risk_mutation"
    HIGH_RISK_MUTATION = "high_risk_mutation"
    DESTRUCTIVE = "destructive"


class ToolState(str, Enum):
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    ENABLED = "enabled"
    DISABLED = "disabled"


def tool_id(name: str, provider: str) -> str:
    """Deterministic tool identity from name + provider."""
    raw = f"{provider}::{name}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class Tool:
    tool_id: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None
    capabilities: tuple[str, ...] = ()
    risk: ToolRisk = ToolRisk.READ_ONLY
    provider: str = ""
    enabled: bool = False
    requires_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "capabilities": list(self.capabilities),
            "risk": self.risk.value,
            "provider": self.provider,
            "enabled": self.enabled,
            "requires_approval": self.requires_approval,
            "metadata": self.metadata,
        }


def requires_approval_for_risk(risk: ToolRisk) -> bool:
    """Risk → approval policy. High-risk mutation and destructive tools require
    explicit approval; read-only and low-risk mutation do not."""
    return risk in {ToolRisk.HIGH_RISK_MUTATION, ToolRisk.DESTRUCTIVE}
