"""Knowledge ingestion event model.

The ingestion pipeline publishes an :class:`EventEnvelope` with ``event_type`` prefixed
by ``knowledge.`` (e.g. ``knowledge.ingestion.file``).  Consumers can subscribe to the
``knowledge.*`` namespace using the shared KORA ``EventBus``.
"""
