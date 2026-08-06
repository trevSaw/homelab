"""Knowledge document model.

A ``KnowledgeDocument`` is an immutable representation of a piece of knowledge
(e.g. the contents of a local file).  It carries the raw content, a generated
identifier, source information and an optional metadata dictionary.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class KnowledgeDocument:
    doc_id: str = field(init=False)
    content: str
    source: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # deterministic id based on content hash (SHA‑256) – stable across runs
        object.__setattr__(self, "doc_id", hashlib.sha256(self.content.encode()).hexdigest())
