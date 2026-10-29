"""Task Bridge FastAPI application: REST API + mounted MCP endpoint."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Header

from .config import load_config
from .executor import Executor
from .mcp_tools import build_mcp_app
from .store import TaskStore

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("taskbridge")

cfg = load_config()
store = TaskStore(cfg.db_path)
executor = Executor(cfg, store)

_mcp_app, _mcp_session_manager = None, None
try:
    _mcp_app, _mcp_session_manager = build_mcp_app(store, executor, cfg.api_token)
    log.info("built MCP endpoint")
except Exception as exc:  # pragma: no cover
    log.error("MCP endpoint failed to build: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    executor.start()
    try:
        if _mcp_session_manager is not None:
            async with _mcp_session_manager.run():
                yield
        else:
            yield
    finally:
        executor.stop()


app = FastAPI(title="KORA Task Bridge", version="1.0.0", lifespan=lifespan)


async def _auth(authorization: str = Header(default="")) -> None:
    if not cfg.api_token:
        return
    if authorization != f"Bearer {cfg.api_token}":
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "taskbridge"}


@app.post("/api/v1/tasks", dependencies=[Depends(_auth)])
async def create_task(payload: dict):
    try:
        task = executor.create(
            request=payload.get("request", ""),
            permission_profile=payload.get("permission_profile", "read_only"),
            requested_by=payload.get("requested_by", "api"),
            session_id=payload.get("session_id"),
            timeout_seconds=payload.get("timeout_seconds"),
            working_directory=payload.get("working_directory"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return task


@app.get("/api/v1/tasks/{task_id}", dependencies=[Depends(_auth)])
async def get_task(task_id: str):
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.get("/api/v1/tasks", dependencies=[Depends(_auth)])
async def list_tasks(limit: int = 25, status: str = ""):
    return store.list_tasks(limit=min(max(limit, 1), 100), status=status or None)


@app.post("/api/v1/tasks/{task_id}/approve", dependencies=[Depends(_auth)])
async def approve_task(task_id: str, payload: dict = {}):
    try:
        return executor.approve(task_id, payload.get("approver", "api"))
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/v1/tasks/{task_id}/cancel", dependencies=[Depends(_auth)])
async def cancel_task(task_id: str, payload: dict = {}):
    try:
        return executor.cancel(task_id, payload.get("by", "api"))
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# Mount the Streamable HTTP MCP endpoint for KORA/Hermes.
if _mcp_app is not None:
    app.mount("/mcp", _mcp_app)
    log.info("mounted MCP endpoint at /mcp")