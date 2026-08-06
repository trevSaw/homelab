import pytest

from ..models.document import KnowledgeDocument
from ..ingestion.processor import process_ingestion, extract_metadata, read_file


def test_deterministic_doc_id():
    content = "sample text"
    doc1 = KnowledgeDocument(content=content, source="src1", metadata={})
    doc2 = KnowledgeDocument(content=content, source="src2", metadata={})
    assert doc1.doc_id == doc2.doc_id


def test_metadata_preservation():
    meta = {"author": "alice", "size": "5"}
    doc = KnowledgeDocument(content="hello", source="src", metadata=meta)
    assert doc.metadata == meta


def test_immutable_behavior():
    doc = KnowledgeDocument(content="x", source="s", metadata={})
    with pytest.raises(AttributeError):
        doc.content = "changed"


def test_local_file_ingestion_and_metadata_extraction(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello world")

    doc = process_ingestion(str(file_path))
    assert doc.content == "hello world"
    assert doc.source == str(file_path)
    assert doc.metadata["filename"] == "doc.txt"
    assert int(doc.metadata["size"]) == len("hello world")


def test_normalization_reads_utf8_text(tmp_path):
    file_path = tmp_path / "notes.md"
    file_path.write_text("line one\nline two\n")
    content = read_file(str(file_path))
    assert content == "line one\nline two\n"
    assert "line one" in content


def test_invalid_input_rejection(tmp_path):
    with pytest.raises(FileNotFoundError):
        process_ingestion(str(tmp_path / "missing.txt"))


def test_empty_input_allowed(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("")
    doc = process_ingestion(str(file_path))
    assert doc.content == ""
    assert int(doc.metadata["size"]) == 0
