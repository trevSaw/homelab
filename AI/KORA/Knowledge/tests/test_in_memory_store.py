import asyncio

from ..storage.in_memory import InMemoryKnowledgeStore
from ..models.document import KnowledgeDocument


def test_save_and_find():
    store = InMemoryKnowledgeStore()
    doc = KnowledgeDocument(content="abc", source="src", metadata={})
    asyncio.run(store.save(doc))
    retrieved = asyncio.run(store.find_by_id(doc.doc_id))
    assert retrieved == doc


def test_list_and_duplicate_handling():
    store = InMemoryKnowledgeStore()
    doc1 = KnowledgeDocument(content="first", source="src", metadata={})
    doc2 = KnowledgeDocument(content="first", source="src2", metadata={})  # same content => same id
    asyncio.run(store.save(doc1))
    asyncio.run(store.save(doc2))  # should overwrite same id
    docs = asyncio.run(store.list_documents())
    assert len(docs) == 1
    assert docs[0].doc_id == doc1.doc_id
