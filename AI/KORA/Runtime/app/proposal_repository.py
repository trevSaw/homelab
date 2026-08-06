"""KORA-owned proposal workflow repositories.

SQLite is runtime infrastructure for proposal state, audit, and recovery. It is
never a durable Memory store and terminal proposal content is always redacted.
"""

from __future__ import annotations

import copy
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .memory_models import (
    MemoryProposal,
    PersistenceStatus,
    ProposalStatus,
    ProposedOperation,
)


class ProposalRepository(Protocol):
    def load_all(self) -> list[MemoryProposal]: ...

    def save(self, proposal: MemoryProposal) -> None: ...

    def record_event(
        self,
        proposal_id: str,
        event_type: str,
        actor: str,
        details: dict[str, Any] | None = None,
    ) -> None: ...

    def audit_history(self, proposal_id: str) -> list[dict[str, Any]]: ...

    def consistency_check(self) -> dict[str, Any]: ...


class InMemoryProposalRepository:
    def __init__(self) -> None:
        self.proposals: dict[str, MemoryProposal] = {}
        self.audit: dict[str, list[dict[str, Any]]] = {}

    def load_all(self) -> list[MemoryProposal]:
        return list(self.proposals.values())

    def save(self, proposal: MemoryProposal) -> None:
        self.proposals[proposal.proposal_id] = proposal

    def record_event(
        self,
        proposal_id: str,
        event_type: str,
        actor: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.audit.setdefault(proposal_id, []).append(
            {
                "event_type": event_type,
                "actor": actor,
                "details": details or {},
                "created_at": _now_iso(),
            }
        )

    def audit_history(self, proposal_id: str) -> list[dict[str, Any]]:
        return list(self.audit.get(proposal_id, []))

    def consistency_check(self) -> dict[str, Any]:
        return {"status": "ok", "repository": "memory", "proposal_count": len(self.proposals)}


class SQLiteProposalRepository:
    """SQLite workflow state with enforced terminal-content redaction."""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._initialize()

    def close(self) -> None:
        self._connection.close()

    def _initialize(self) -> None:
        with self._connection:
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    persistence_status TEXT NOT NULL,
                    proposed_content TEXT,
                    proposal_json TEXT NOT NULL,
                    durable_memory_id TEXT,
                    content_hash TEXT,
                    updated_at TEXT NOT NULL,
                    CHECK (
                        status IN ('draft', 'pending_review')
                        OR proposed_content IS NULL
                    )
                )
                """
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS proposal_audit (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (proposal_id) REFERENCES proposals(proposal_id)
                )
                """
            )

    def load_all(self) -> list[MemoryProposal]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM proposals ORDER BY updated_at"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def save(self, proposal: MemoryProposal) -> None:
        terminal = proposal.status not in {
            ProposalStatus.DRAFT,
            ProposalStatus.PENDING_REVIEW,
        }
        content = None if terminal else proposal.proposed_content
        data = proposal.to_dict()
        data.pop("proposed_content", None)
        data["audit_metadata"] = _sanitized_audit(proposal.audit_metadata, terminal=terminal)
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO proposals (
                    proposal_id, status, persistence_status, proposed_content,
                    proposal_json, durable_memory_id, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(proposal_id) DO UPDATE SET
                    status=excluded.status,
                    persistence_status=excluded.persistence_status,
                    proposed_content=excluded.proposed_content,
                    proposal_json=excluded.proposal_json,
                    durable_memory_id=excluded.durable_memory_id,
                    content_hash=excluded.content_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    proposal.proposal_id,
                    proposal.status.value,
                    proposal.persistence_status.value,
                    content,
                    json.dumps(data, sort_keys=True),
                    proposal.durable_memory_id,
                    proposal.content_hash,
                    _now_iso(),
                ),
            )

    def record_event(
        self,
        proposal_id: str,
        event_type: str,
        actor: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        safe_details = _remove_content(copy.deepcopy(details or {}))
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO proposal_audit (
                    proposal_id, event_type, actor, details_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    proposal_id,
                    event_type,
                    actor,
                    json.dumps(safe_details, sort_keys=True),
                    _now_iso(),
                ),
            )

    def audit_history(self, proposal_id: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_type, actor, details_json, created_at
                FROM proposal_audit
                WHERE proposal_id = ?
                ORDER BY audit_id
                """,
                (proposal_id,),
            ).fetchall()
        return [
            {
                "event_type": row["event_type"],
                "actor": row["actor"],
                "details": json.loads(row["details_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def consistency_check(self) -> dict[str, Any]:
        with self._lock:
            result = self._connection.execute("PRAGMA integrity_check").fetchone()[0]
            leaked = self._connection.execute(
                """
                SELECT COUNT(*) FROM proposals
                WHERE status NOT IN ('draft', 'pending_review')
                  AND proposed_content IS NOT NULL
                """
            ).fetchone()[0]
            count = self._connection.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
        return {
            "status": "ok" if result == "ok" and leaked == 0 else "error",
            "repository": "sqlite",
            "integrity": result,
            "terminal_content_rows": leaked,
            "proposal_count": count,
        }

    @staticmethod
    def _from_row(row: sqlite3.Row) -> MemoryProposal:
        data = json.loads(row["proposal_json"])
        return MemoryProposal(
            proposal_id=data["proposal_id"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            conversation_id=data.get("conversation_id"),
            candidate_type=data["candidate_type"],
            confidence=float(data["confidence"]),
            importance=float(data["importance"]),
            proposed_operation=ProposedOperation(data["proposed_operation"]),
            proposed_content=row["proposed_content"],
            related_entities=list(data.get("related_entities") or []),
            related_topics=list(data.get("related_topics") or []),
            status=ProposalStatus(row["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            audit_metadata=dict(data.get("audit_metadata") or {}),
            persistence_status=PersistenceStatus(row["persistence_status"]),
            durable_memory_id=row["durable_memory_id"],
            content_hash=row["content_hash"],
            schema_version=str(data.get("schema_version", "1.0")),
        )


def _sanitized_audit(value: dict[str, Any], *, terminal: bool) -> dict[str, Any]:
    result = copy.deepcopy(value)
    if terminal:
        result = _remove_content(result)
    return result


def _remove_content(value: Any) -> Any:
    sensitive_keys = {
        "content",
        "proposed_content",
        "text",
        "text_final",
        "memory_candidate",
        "payload",
    }
    if isinstance(value, dict):
        return {
            key: ("[redacted]" if key in sensitive_keys else _remove_content(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_remove_content(item) for item in value]
    return value


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
