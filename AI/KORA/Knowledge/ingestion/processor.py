"""Processor for knowledge ingestion events.

The processor normalises the raw file content, extracts minimal metadata and
produces a :class:`KnowledgeDocument`.  It is deliberately simple – only
local‑file ingestion is supported in this phase.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

from ..models.document import KnowledgeDocument


def read_file(file_path: str) -> str:
    """Read a local file as UTF‑8 text.

    Raises ``FileNotFoundError`` if the path does not exist and ``UnicodeDecodeError``
    for non‑text files.  The function is deliberately small to keep the ingestion
    pipeline deterministic for testing.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_metadata(file_path: str) -> Mapping[str, str]:
    """Return a simple metadata mapping for the given file.

    Currently includes ``filename`` and ``size`` (bytes).  The mapping is kept
    minimal to avoid coupling to external services.
    """
    p = Path(file_path)
    return {
        "filename": p.name,
        "size": str(p.stat().st_size),
    }


def process_ingestion(file_path: str) -> KnowledgeDocument:
    """Full ingestion processing pipeline.

    1. Read the file content.
    2. Extract metadata.
    3. Create a :class:`KnowledgeDocument`.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    content = read_file(file_path)
    metadata = extract_metadata(file_path)
    return KnowledgeDocument(content=content, source=file_path, metadata=metadata)
