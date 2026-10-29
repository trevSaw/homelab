"""Persistent SQLite task store (thread-safe)."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id                  TEXT PRIMARY KEY,
    request             TEXT NOT NULL,
    permission_profile  TEXT NOT NULL,
    working_directory   TEXT,
    requested_by        TEXT,
    approved_by         TEXT,
    session_id          TEXT,
    timeout_seconds     INTEGER NOT NULL DEFAULT 3600,
    status              TEXT NOT NULL,
    opencode_session    TEXT,
    process_pid         INTEGER,
    created_at          TEXT NOT NULL,
    started_at          TEXT,
    completed_at        TEXT,
    exit_code           INTEGER,
    result              TEXT,
    error               TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    ts      TEXT NOT NULL,
    event   TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStore:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    # -- low-level ----------------------------------------------------------
    def _execute(self, sql: str, params=()):
        with self._lock:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
            return cur

    def _query(self, sql: str, params=()):
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    # -- tasks --------------------------------------------------------------
    def create_task(self, task_id, request, permission_profile, requested_by,
                    session_id, timeout_seconds, working_directory=None) -> dict:
        with self._lock:
            self._conn.execute(
                "INSERT INTO tasks (id, request, permission_profile, working_directory,"
                " requested_by, session_id, timeout_seconds, status, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (task_id, request, permission_profile, working_directory, requested_by,
                 session_id, timeout_seconds, "QUEUED", _now()),
            )
            self._conn.execute(
                "INSERT INTO events (task_id, ts, event) VALUES (?,?,?)",
                (task_id, _now(), "created"),
            )
            self._conn.commit()
        return self.get_task(task_id)

    def next_id(self, day_prefix: str) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS c FROM tasks WHERE id LIKE ?", (day_prefix + "-%",)
            ).fetchone()
            return int(row["c"]) + 1

    def get_task(self, task_id: str) -> dict | None:
        rows = self._query("SELECT * FROM tasks WHERE id=?", (task_id,))
        if not rows:
            return None
        t = dict(rows[0])
        t["result"] = json.loads(t["result"]) if t["result"] else None
        return t

    def list_tasks(self, limit=50, status=None) -> list[dict]:
        sql = "SELECT * FROM tasks"
        params = []
        if status:
            sql += " WHERE status=?"
            params.append(status)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self._query(sql, tuple(params))]

    def set_status(self, task_id: str, status: str, event: str | None = None, **fields):
        fields["status"] = status
        if status in ("STARTING", "RUNNING") and fields.get("started_at") is None:
            fields["started_at"] = _now()
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            fields["completed_at"] = _now()
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._lock:
            self._conn.execute(f"UPDATE tasks SET {cols} WHERE id=?", tuple(fields.values()) + (task_id,))
            if event:
                self._conn.execute(
                    "INSERT INTO events (task_id, ts, event) VALUES (?,?,?)",
                    (task_id, _now(), event),
                )
            self._conn.commit()

    def update_fields(self, task_id: str, **fields):
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._lock:
            self._conn.execute(f"UPDATE tasks SET {cols} WHERE id=?", tuple(fields.values()) + (task_id,))
            self._conn.commit()

    def add_event(self, task_id: str, event: str):
        with self._lock:
            self._conn.execute(
                "INSERT INTO events (task_id, ts, event) VALUES (?,?,?)",
                (task_id, _now(), event),
            )
            self._conn.commit()

    def events(self, task_id: str) -> list[dict]:
        return [dict(r) for r in self._query(
            "SELECT ts, event FROM events WHERE task_id=? ORDER BY id", (task_id,))]

    def running_tasks(self) -> list[str]:
        rows = self._query("SELECT id FROM tasks WHERE status IN ('STARTING','RUNNING')")
        return [r["id"] for r in rows]

    def queued_task(self) -> dict | None:
        rows = self._query(
            "SELECT id FROM tasks WHERE status='QUEUED' ORDER BY created_at ASC LIMIT 1"
        )
        return self.get_task(rows[0]["id"]) if rows else None

    def count_active(self) -> int:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS c FROM tasks WHERE status IN ('STARTING','RUNNING')"
            ).fetchone()
            return int(row["c"])

    def close(self):
        with self._lock:
            self._conn.close()