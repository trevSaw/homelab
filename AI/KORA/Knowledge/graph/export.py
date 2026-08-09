"""Export KORA's graph to Graphify's ``graph.json`` (NetworkX node-link format).

Graphify serves a graph via ``python -m graphify.serve graph.json``. This export
produces a compatible node-link document from KORA's derived graph representation
so the same Graphify container can serve, query, and visualize KORA's
relationships. Graphify is a derived representation — never authoritative
Knowledge.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .store import GraphStore


def build_graphify_document(store: GraphStore) -> dict[str, Any]:
    """Build a Graphify-compatible node-link graph document from a GraphStore."""
    nodes: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []

    for entity in store.list_entities():
        nodes.append(
            {
                "id": entity.entity_id,
                "label": entity.canonical_name,
                "file_type": entity.entity_type,
                "norm_label": entity.canonical_name.lower(),
                "type": entity.entity_type,
                "source_ref": entity.source_ref,
                "source_knowledge_id": entity.source_knowledge_id,
                "source_version": entity.source_version,
                "source_content_hash": entity.source_content_hash,
            }
        )

    for relationship in store.list_relationships():
        links.append(
            {
                "relation": relationship.relationship_type,
                "confidence": relationship.confidence,
                "confidence_score": _confidence_score(relationship.confidence),
                "source": relationship.source_entity,
                "target": relationship.target_entity,
                "weight": 1.0,
                "source_knowledge_id": relationship.source_knowledge_id,
                "source_version": relationship.source_version,
            }
        )

    return {
        "directed": False,
        "multigraph": False,
        "graph": {},
        "nodes": nodes,
        "links": links,
        "hyperedges": [],
    }


def _confidence_score(confidence: str) -> float:
    return {"EXTRACTED": 1.0, "INFERRED": 0.5, "AMBIGUOUS": 0.2}.get(confidence, 0.5)


def export_to_graphify(store: GraphStore, output_path: str | Path) -> Path:
    """Write the KORA graph as a Graphify ``graph.json`` file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = build_graphify_document(store)
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    return path
