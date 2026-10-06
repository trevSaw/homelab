"""KORA explainability record store (smallest mechanism: JSON-lines file).

Proves KORA can maintain a structured out-of-band record per request —
NOT a production API.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/opt/data"))
EXPLAIN_DIR = _HERMES_HOME / "kora-explain"
EXPLAIN_PATH = EXPLAIN_DIR / "records.jsonl"

_lock = threading.Lock()
_CURRENT: dict[str, dict[str, Any]] = {}
_SESSIONS: dict[str, Any] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_session(session_id: str, data: dict[str, Any]) -> None:
    _SESSIONS[session_id] = data


def begin_record(*, turn_id: str, session_id: str, request: str,
                 classification: dict[str, Any], strategy: dict[str, Any], model: str) -> dict[str, Any]:
    return {
        "request_id": turn_id,
        "session_id": session_id,
        "timestamp": _now(),
        "identity": "KORA",
        "classification": classification.get("label", ""),
        "strategy": strategy.get("name", ""),
        "governance": "allowed",
        "services_used": [],
        "tools": [],
        "model": model,
        "request_text": request,
        "response_text": "",
        "refused": False,
    }


def set_current(session_id: str, rec: dict[str, Any]) -> None:
    with _lock:
        _CURRENT[session_id] = rec


def current_record(session_id: str) -> dict[str, Any] | None:
    with _lock:
        return _CURRENT.get(session_id)


def record_tool(session_id: str, tool: str, decision: str, reason: str) -> None:
    rec = current_record(session_id)
    if rec is None:
        return
    with _lock:
        rec.setdefault("tools", []).append({"tool": tool, "decision": decision, "reason": reason})


def finalize(rec: dict[str, Any]) -> None:
    rec["finalized_at"] = _now()
    with _lock:
        EXPLAIN_DIR.mkdir(parents=True, exist_ok=True)
        with EXPLAIN_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")


def write_state(state: dict[str, Any]) -> None:
    with _lock:
        try:
            EXPLAIN_DIR.mkdir(parents=True, exist_ok=True)
            (EXPLAIN_DIR / "state.json").write_text(json.dumps(state, sort_keys=True), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
