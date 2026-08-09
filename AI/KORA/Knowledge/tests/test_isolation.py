"""Phase 14.2D production-readiness tests for Knowledge isolation.

These tests validate existing behavior only. No production functionality is
added to satisfy them.
"""

import asyncio

from app.event_bus import InProcessEventBus
from app.memory_runtime import EventDrivenMemoryRuntime, MemoryRuntimeConfig

from ..storage.in_memory import InMemoryKnowledgeStore
from ..ingestion.service import KnowledgeIngestionService


def test_knowledge_ingestion_does_not_create_memory(tmp_path):
    bus = InProcessEventBus()
    memory_runtime = EventDrivenMemoryRuntime(
        bus,
        MemoryRuntimeConfig(),
    )
    knowledge_store = InMemoryKnowledgeStore()
    service = KnowledgeIngestionService(store=knowledge_store, event_bus=bus)

    file_path = tmp_path / "doc.txt"
    file_path.write_text("external reference material")

    asyncio.run(service.ingest(str(file_path)))

    assert memory_runtime.list_pending() == []
    assert memory_runtime.list_all() == []


def test_knowledge_events_do_not_route_to_memory_subscriptions(tmp_path):
    bus = InProcessEventBus()
    memory_runtime = EventDrivenMemoryRuntime(
        bus,
        MemoryRuntimeConfig(),
    )
    knowledge_store = InMemoryKnowledgeStore()
    service = KnowledgeIngestionService(store=knowledge_store, event_bus=bus)

    events = []
    bus.subscribe("knowledge.*", lambda ev: events.append(ev.event_type))

    file_path = tmp_path / "doc.txt"
    file_path.write_text("isolated")

    asyncio.run(service.ingest(str(file_path)))

    assert events == ["knowledge.ingestion.file"]
    assert memory_runtime.list_all() == []
