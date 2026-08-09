"""Tests for index metadata persistence."""

import tempfile

from ..models.index_state import IndexMetadata, IndexState
from ..storage.index_metadata import InMemoryIndexMetadataStore, SQLiteIndexMetadataStore


def test_in_memory_upsert_get_list_delete():
    store = InMemoryIndexMetadataStore()
    assert store.get("doc-1") is None
    meta = IndexMetadata(
        document_id="doc-1",
        version="v1",
        content_hash="abc",
        index_state=IndexState.INDEXED,
        embedding_model="nomic-embed-text",
        source="src",
        chunk_ids=("doc-1:v1:0",),
        chunk_count=1,
    )
    store.upsert(meta)
    assert store.get("doc-1").version == "v1"
    assert [m.document_id for m in store.list_indexed()] == ["doc-1"]
    store.delete("doc-1")
    assert store.get("doc-1") is None


def test_sqlite_store_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        path = f"{tmp}/index.sqlite3"
        store = SQLiteIndexMetadataStore(path)
        meta = IndexMetadata(
            document_id="doc-2",
            version="v3",
            content_hash="xyz",
            index_state=IndexState.INDEXED,
            embedding_model="nomic-embed-text",
            source="/src/doc.md",
            chunk_ids=("doc-2:v3:0", "doc-2:v3:1"),
            chunk_count=2,
        )
        store.upsert(meta)
        loaded = store.get("doc-2")
        assert loaded is not None
        assert loaded.version == "v3"
        assert loaded.chunk_ids == ("doc-2:v3:0", "doc-2:v3:1")
        assert loaded.chunk_count == 2
        check = store.consistency_check()
        assert check["indexed_documents"] == 1
        store.close()


def test_sqlite_replace_same_document():
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteIndexMetadataStore(f"{tmp}/i.sqlite3")
        store.upsert(
            IndexMetadata(
                document_id="d",
                version="v1",
                content_hash="h1",
                index_state=IndexState.INDEXED,
                embedding_model="m",
                source="s",
                chunk_ids=("d:v1:0",),
                chunk_count=1,
            )
        )
        store.upsert(
            IndexMetadata(
                document_id="d",
                version="v2",
                content_hash="h2",
                index_state=IndexState.INDEXED,
                embedding_model="m",
                source="s",
                chunk_ids=("d:v2:0", "d:v2:1"),
                chunk_count=2,
            )
        )
        assert store.get("d").version == "v2"
        assert store.list_indexed() == [store.get("d")]
        store.close()


def test_failed_state_not_in_indexed_list():
    store = InMemoryIndexMetadataStore()
    store.upsert(
        IndexMetadata(
            document_id="d",
            version="v1",
            content_hash="h",
            index_state=IndexState.FAILED,
            embedding_model="m",
            source="s",
            last_error="backend down",
        )
    )
    assert store.list_indexed() == []
