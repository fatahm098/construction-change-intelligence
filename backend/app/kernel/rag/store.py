"""Vector store in-memory (dev).

Menyimpan chunk + embedding di memori proses. Interface (`add`, `search`,
`delete_document`) disiapkan agar implementasi pgvector bisa menggantikannya
tanpa mengubah kode pemanggil.

Catatan: store ini tidak persisten — data hilang saat server restart.
Untuk produksi, ganti dengan `PgVectorStore` (tabel document_chunks).
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class StoredChunk:
    document_id: int
    project_id: int
    filename: str
    text: str
    embedding: list[float]
    chunk_index: int
    page: int | None = None


@dataclass
class SearchHit:
    chunk: StoredChunk
    score: float


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class InMemoryVectorStore:
    """Vector store sederhana berbasis dict, cukup untuk pengembangan lokal."""

    def __init__(self) -> None:
        self._chunks: list[StoredChunk] = []

    def add(self, chunks: list[StoredChunk]) -> int:
        self._chunks.extend(chunks)
        return len(chunks)

    def search(
        self,
        query_embedding: list[float],
        *,
        project_id: int | None = None,
        top_k: int = 5,
    ) -> list[SearchHit]:
        candidates = self._chunks
        if project_id is not None:
            candidates = [c for c in candidates if c.project_id == project_id]

        scored = [SearchHit(chunk=c, score=_cosine(query_embedding, c.embedding)) for c in candidates]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]

    def delete_document(self, document_id: int) -> int:
        before = len(self._chunks)
        self._chunks = [c for c in self._chunks if c.document_id != document_id]
        return before - len(self._chunks)

    def count(self) -> int:
        return len(self._chunks)


# Singleton store tingkat proses
vector_store = InMemoryVectorStore()
