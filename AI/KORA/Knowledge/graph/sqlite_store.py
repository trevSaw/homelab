"""SQLite-backed GraphStore for production persistence.

Persists graph entities and relationships derived from authoritative Knowledge.
This is workflow/graph state — never authoritative Knowledge and never Memory.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .models import GraphEntity, GraphRelationship


class SQLiteGraphStore:
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
                CREATE TABLE IF NOT EXISTS graph_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    canonical_name TEXT NOT NULL,
                    aliases_json TEXT NOT NULL,
                    source_knowledge_id TEXT NOT NULL,
                    source_version TEXT NOT NULL,
                    source_content_hash TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_entity TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    target_entity TEXT NOT NULL,
                    source_knowledge_id TEXT NOT NULL,
                    source_version TEXT NOT NULL,
                    source_content_hash TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_rel_source ON graph_relationships(source_entity)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_rel_target ON graph_relationships(target_entity)"
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_ent_knowledge ON graph_entities(source_knowledge_id)"
            )

    def get_entity(self, entity_id: str) -> GraphEntity | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM graph_entities WHERE entity_id = ?", (entity_id,)
            ).fetchone()
        return _entity_from_row(row) if row else None

    def upsert_entity(self, entity: GraphEntity) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO graph_entities (
                    entity_id, entity_type, canonical_name, aliases_json,
                    source_knowledge_id, source_version, source_content_hash,
                    source_ref, created_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_id) DO UPDATE SET
                    entity_type=excluded.entity_type,
                    canonical_name=excluded.canonical_name,
                    aliases_json=excluded.aliases_json,
                    source_knowledge_id=excluded.source_knowledge_id,
                    source_version=excluded.source_version,
                    source_content_hash=excluded.source_content_hash,
                    source_ref=excluded.source_ref,
                    created_at=excluded.created_at,
                    metadata_json=excluded.metadata_json
                """,
                (
                    entity.entity_id,
                    entity.entity_type,
                    entity.canonical_name,
                    json.dumps(list(entity.aliases)),
                    entity.source_knowledge_id,
                    entity.source_version,
                    entity.source_content_hash,
                    entity.source_ref,
                    entity.created_at.isoformat(),
                    json.dumps(entity.metadata),
                ),
            )

    def list_entities(self) -> list[GraphEntity]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM graph_entities ORDER BY canonical_name"
            ).fetchall()
        return [_entity_from_row(row) for row in rows]

    def find_entities_by_name(self, name: str) -> list[GraphEntity]:
        needle = _normalize(name)
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM graph_entities"
            ).fetchall()
        return [
            e
            for e in (_entity_from_row(row) for row in rows)
            if _normalize(e.canonical_name) == needle
            or any(_normalize(a) == needle for a in e.aliases)
        ]

    def get_relationship(self, relationship_id: str) -> GraphRelationship | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM graph_relationships WHERE relationship_id = ?",
                (relationship_id,),
            ).fetchone()
        return _relationship_from_row(row) if row else None

    def upsert_relationship(self, relationship: GraphRelationship) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO graph_relationships (
                    relationship_id, source_entity, relationship_type, target_entity,
                    source_knowledge_id, source_version, source_content_hash,
                    source_ref, confidence, created_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(relationship_id) DO UPDATE SET
                    source_entity=excluded.source_entity,
                    relationship_type=excluded.relationship_type,
                    target_entity=excluded.target_entity,
                    source_knowledge_id=excluded.source_knowledge_id,
                    source_version=excluded.source_version,
                    source_content_hash=excluded.source_content_hash,
                    source_ref=excluded.source_ref,
                    confidence=excluded.confidence,
                    created_at=excluded.created_at,
                    metadata_json=excluded.metadata_json
                """,
                (
                    relationship.relationship_id,
                    relationship.source_entity,
                    relationship.relationship_type,
                    relationship.target_entity,
                    relationship.source_knowledge_id,
                    relationship.source_version,
                    relationship.source_content_hash,
                    relationship.source_ref,
                    relationship.confidence,
                    relationship.created_at.isoformat(),
                    json.dumps(relationship.metadata),
                ),
            )

    def list_relationships(self) -> list[GraphRelationship]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM graph_relationships ORDER BY source_entity"
            ).fetchall()
        return [_relationship_from_row(row) for row in rows]

    def relationships_for_entity(self, entity_id: str) -> list[GraphRelationship]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM graph_relationships WHERE source_entity = ? OR target_entity = ?",
                (entity_id, entity_id),
            ).fetchall()
        return [_relationship_from_row(row) for row in rows]

    def neighbors(self, entity_id: str) -> list[str]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT source_entity, target_entity FROM graph_relationships "
                "WHERE source_entity = ? OR target_entity = ?",
                (entity_id, entity_id),
            ).fetchall()
        result: list[str] = []
        for row in rows:
            if row["source_entity"] == entity_id:
                result.append(row["target_entity"])
            if row["target_entity"] == entity_id:
                result.append(row["source_entity"])
        return sorted(set(result))

    def delete_by_knowledge(self, source_knowledge_id: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "DELETE FROM graph_relationships WHERE source_knowledge_id = ?",
                (source_knowledge_id,),
            )
            self._connection.execute(
                "DELETE FROM graph_entities WHERE source_knowledge_id = ?",
                (source_knowledge_id,),
            )

    def consistency_check(self) -> dict[str, Any]:
        with self._lock:
            entities = self._connection.execute(
                "SELECT COUNT(*) AS c FROM graph_entities"
            ).fetchone()["c"]
            relationships = self._connection.execute(
                "SELECT COUNT(*) AS c FROM graph_relationships"
            ).fetchone()["c"]
        return {
            "status": "ok",
            "repository": "sqlite",
            "entities": entities,
            "relationships": relationships,
        }


def _entity_from_row(row) -> GraphEntity:
    from datetime import datetime, timezone

    created = datetime.fromisoformat(str(row["created_at"]))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return GraphEntity(
        entity_id=str(row["entity_id"]),
        entity_type=str(row["entity_type"]),
        canonical_name=str(row["canonical_name"]),
        aliases=tuple(json.loads(str(row["aliases_json"]) or "[]")),
        source_knowledge_id=str(row["source_knowledge_id"]),
        source_version=str(row["source_version"]),
        source_content_hash=str(row["source_content_hash"]),
        source_ref=str(row["source_ref"]),
        created_at=created,
        metadata=json.loads(str(row["metadata_json"]) or "{}"),
    )


def _relationship_from_row(row) -> GraphRelationship:
    from datetime import datetime, timezone

    created = datetime.fromisoformat(str(row["created_at"]))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return GraphRelationship(
        relationship_id=str(row["relationship_id"]),
        source_entity=str(row["source_entity"]),
        relationship_type=str(row["relationship_type"]),
        target_entity=str(row["target_entity"]),
        source_knowledge_id=str(row["source_knowledge_id"]),
        source_version=str(row["source_version"]),
        source_content_hash=str(row["source_content_hash"]),
        source_ref=str(row["source_ref"]),
        confidence=str(row["confidence"]),
        created_at=created,
        metadata=json.loads(str(row["metadata_json"]) or "{}"),
    )


def _normalize(value: str) -> str:
    return "".join(ch for ch in value.lower().strip() if ch.isalnum())
