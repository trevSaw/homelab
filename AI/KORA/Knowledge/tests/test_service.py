import asyncio

from app.event_bus import InProcessEventBus, EventEnvelope

from ..storage.in_memory import InMemoryKnowledgeStore
from ..ingestion.service import KnowledgeIngestionService


def test_end_to_end_ingestion(tmp_path):
    event_bus = InProcessEventBus()
    store = InMemoryKnowledgeStore()
    service = KnowledgeIngestionService(store=store, event_bus=event_bus)

    events = []
    def collector(ev: EventEnvelope):
        events.append(ev)
    event_bus.subscribe("knowledge.*", collector)

    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello world")

    asyncio.run(service.ingest(str(file_path)))

    docs = asyncio.run(store.list_documents())
    assert len(docs) == 1
    assert docs[0].content == "hello world"
    assert any(e.event_type == "knowledge.ingestion.file" for e in events)
