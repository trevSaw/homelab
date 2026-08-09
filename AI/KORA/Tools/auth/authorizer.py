"""Tool authorization and governance.

Enforces the distinction: discovered → registered → enabled → authorized →
executable. High-risk/destructive tools require explicit approval.
"""

from __future__ import annotations

import threading

from ..models.tool import Tool, ToolRisk, requires_approval_for_risk


class ToolNotAuthorizedError(PermissionError):
    pass


class ToolDisabledError(PermissionError):
    pass


class ToolApprovalRequiredError(PermissionError):
    pass


class ToolAuthorizer:
    def __init__(self, *, read_only_automatic: bool = True) -> None:
        """``read_only_automatic`` allows read-only/low-risk tools to execute
        automatically when authorized; mutating/destructive tools always require
        approval per risk policy."""
        self._read_only_automatic = read_only_automatic
        self._approvals: set[str] = set()
        self._lock = threading.RLock()

    def authorize(self, tool: Tool) -> None:
        """Raise if the tool cannot be executed under current policy."""
        if not tool.enabled:
            raise ToolDisabledError(tool.tool_id)
        if tool.requires_approval or requires_approval_for_risk(tool.risk):
            if tool.tool_id not in self._approvals:
                raise ToolApprovalRequiredError(tool.tool_id)
            return
        # Read-only / low-risk tools.
        if tool.risk == ToolRisk.READ_ONLY:
            return
        # Low-risk mutation: automatic only when read_only_automatic is enabled.
        if not self._read_only_automatic:
            raise ToolNotAuthorizedError(tool.tool_id)

    def grant_approval(self, tool_id: str) -> None:
        with self._lock:
            self._approvals.add(tool_id)

    def revoke_approval(self, tool_id: str) -> None:
        with self._lock:
            self._approvals.discard(tool_id)

    def is_approved(self, tool_id: str) -> bool:
        with self._lock:
            return tool_id in self._approvals

    def reset(self) -> None:
        with self._lock:
            self._approvals.clear()
