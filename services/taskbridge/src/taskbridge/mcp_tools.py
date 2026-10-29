"""MCP (Streamable HTTP) server exposing task tools to KORA/Hermes."""
from __future__ import annotations

import logging

from .executor import Executor
from .store import TaskStore

log = logging.getLogger("taskbridge.mcp")

from mcp.server.fastmcp import FastMCP


def build_mcp_app(store: TaskStore, executor: Executor, api_token: str):
    # streamable_http_path="/" because FastAPI mounts this app at "/mcp" and
    # strips the mount prefix before passing the remaining path to the sub-app.
    # DNS-rebinding protection is disabled: the service is internal-only on the
    # proxy Docker network (not publicly exposed) and every endpoint is
    # token-authenticated. Host validation would otherwise reject the internal
    # service name ("taskbridge") used by the Hermes MCP client.
    from mcp.server.transport_security import TransportSecuritySettings

    mcp = FastMCP(
        "kora-taskbridge",
        streamable_http_path="/",
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )

    @mcp.tool()
    def create_task(request: str, permission_profile: str, requested_by: str = "kora",
                    session_id: str = "", timeout_seconds: int = 0) -> dict:
        """Create a task for the OpenCode worker.

        permission_profile: read_only (inspect only), test_write (edits in an
        isolated worktree), or production_write (canonical repo, approval-gated).
        Returns the task record immediately; execution continues asynchronously.
        """
        task = executor.create(
            request=request,
            permission_profile=permission_profile,
            requested_by=requested_by or "kora",
            session_id=session_id or None,
            timeout_seconds=timeout_seconds or None,
        )
        return {k: v for k, v in task.items() if k not in ("result",)}

    @mcp.tool()
    def get_task(task_id: str) -> dict:
        """Get a task's current status and result (by KORA-YYYYMMDD-XXXX id)."""
        task = store.get_task(task_id)
        if not task:
            raise ValueError(f"task {task_id} not found")
        return task

    @mcp.tool()
    def list_tasks(limit: int = 10, status: str = "") -> list[dict]:
        """List recent tasks, optionally filtered by status."""
        return store.list_tasks(limit=min(int(limit or 10), 100), status=status or None)

    @mcp.tool()
    def cancel_task(task_id: str, by: str = "kora") -> dict:
        """Cancel a queued/running task."""
        return executor.cancel(task_id, by or "kora")

    @mcp.tool()
    def approve_task(task_id: str, approver: str = "kora") -> dict:
        """Approve a WAITING_FOR_APPROVAL task so it can run.

        Only call after the homelab owner explicitly confirmed approval for the
        production change described in the task.
        """
        return executor.approve(task_id, approver or "kora")

    app = mcp.streamable_http_app()
    session_manager = mcp.session_manager

    if api_token:
        app = _AuthMiddleware(app, api_token)
    return app, session_manager


class _AuthMiddleware:
    """ASGI middleware enforcing a bearer token on all MCP requests."""

    def __init__(self, app, token: str):
        self.app = app
        self.token = token

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        if auth != f"Bearer {self.token}":
            from starlette.responses import JSONResponse

            await JSONResponse({"jsonrpc": "2.0", "error": {"code": -32001, "message": "Unauthorized"}})(scope, receive, send)
            return
        await self.app(scope, receive, send)