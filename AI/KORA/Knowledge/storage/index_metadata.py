"""Index metadata persistence.

Stores the synchronization state between authoritative Knowledge and the vector
index. This is KORA-owned workflow/infrastructure metadata — it is NOT
authoritative Knowledge and NEVER stores the authoritative document content
beyond a content hash.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Protocol

from ..models.index_state import IndexMetadata, IndexState


class IndexMetadataStore(Protocol):
    def get(self, document_id: str) -> IndexMetadata | None: ...

    def upsert(self, metadata: IndexMetadata) -> None: ...

    def list_all(self) -> list[IndexMetadata]: ...

    def list_indexed(self) -> list[IndexMetadata]: ...

    def delete(self, document_id: str) -> None: ...

    def close(self) -> None: ...


class InMemoryIndexMetadataStore:
    def __init__(self) -> None:
        self._items: dict[str, IndexMetadata] = {}
        self._lock = threading.RLock()

    def get(self, document_id: str) -> IndexMetadata | None:
        with self._lock:
            return self._items.get(document_id)

    def upsert(self, metadata: IndexMetadata) -> None:
        with self._lock:
            self._items[metadata.document_id] = metadata

    def list_all(self) -> list[IndexMetadata]:
        with self._lock:
            return sorted(
                self._items.values(), key=lambda item: item.document_id
            )

    def list_indexed(self) -> list[IndexMetadata]:
        return [item for item in self.list_all() if item.index_state == IndexState.INDEXED]

    def delete(self, document_id: str) -> None:
        with self._lock:
            self._items.pop(document_id, None)

    def close(self) -> None:
        pass


class SQLiteIndexMetadataStore:
    """SQLite workflow state for Knowledge index synchronization."""

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
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_index (
                    document_id TEXT PRIMARY KEY,
                    version TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    index_state TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chunk_ids_json TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL,
                    indexed_at TEXT NOT NULL,
                    last_error TEXT
                )
                """
            )

    def get(self, document_id: str) -> IndexMetadata | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM knowledge_index WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return self._from_row(row) if row else None

    def upsert(self, metadata: IndexMetadata) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO knowledge_index (
                    document_id, version, content_hash, index_state,
                    embedding_model, source, chunk_ids_json, chunk_count,
                    indexed_at, last_error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    version=excluded.version,
                    content_hash=excluded.content_hash,
                    index_state=excluded.index_state,
                    embedding_model=excluded.embedding_model,
                    source=excluded.source,
                    chunk_ids_json=excluded.chunk_ids_json,
                    chunk_count=excluded.chunk_count,
                    indexed_at=excluded.indexed_at,
                    last_error=excluded.last_error
                """,
                (
                    metadata.document_id,
                    metadata.version,
                    metadata.content_hash,
                    metadata.index_state,
                    metadata.embedding_model,
                    metadata.source,
                    json.dumps(list(metadata.chunk_ids)),
                    metadata.chunk_count,
                    metadata.indexed_at.isoformat(),
                    metadata.last_error,
                ),
            )

    def list_all(self) -> list[IndexMetadata]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM knowledge_index ORDER BY document_id"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def list_indexed(self) -> list[IndexMetadata]:
        return [item for item in self.list_all() if item.index_state == IndexState.INDEXED]

    def delete(self, document_id: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "DELETE FROM knowledge_index WHERE document_id = ?",
                (document_id,),
            )

    def consistency_check(self) -> dict[str, Any]:
        with self._lock:
            total = self._connection.execute(
                "SELECT COUNT(*) AS c FROM knowledge_index"
            ).fetchone()["c"]
            indexed = self._connection.execute(
                "SELECT COUNT(*) AS c FROM knowledge_index WHERE index_state = ?",
                (IndexState.INDEXED,),
            ).fetchone()["c"]
            failed = self._connection.execute(
                "SELECT COUNT(*) AS c FROM knowledge_index WHERE index_state = ?",
                (IndexState.FAILED,),
            ).fetchone()["c"]
        return {
            "status": "ok",
            "repository": "sqlite",
            "total_documents": total,
            "indexed_documents": indexed,
            "failed_documents": failed,
        }

    @staticmethod
    def _from_row(row: sqlite3.Row) -> IndexMetadata:
        return IndexMetadata(
            document_id=str(row["document_id"]),
            version=str(row["version"]),
            content_hash=str(row["content_hash"]),
            index_state=str(row["index_state"]),
            embedding_model=str(row["embedding_model"]),
            source=str(row["source"]),
            chunk_ids=tuple(json.loads(str(row["chunk_ids_json"]) or "[]")),
            chunk_count=int(row["chunk_count"]),
            indexed_at=_parse_dt(str(row["indexed_at"])),
            last_error=row["last_error"],
        )


def _parse_dt(value: str):
    from datetime import datetime, timezone

    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return datetime.now(timezone.utc)
