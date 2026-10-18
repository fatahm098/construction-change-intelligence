"""Embedder — membungkus provider embedding untuk menghasilkan vektor."""

from __future__ import annotations

from ..llm.embedding import EmbeddingProvider, get_embedding_provider


class Embedder:
    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        # Pemanggil lama (Retriever) mengoper LLMProvider sebagai argumen posisi;
        # itu bukan provider embedding, jadi diabaikan dan config yang dipakai.
        if isinstance(provider, EmbeddingProvider):
            self.provider = provider
        else:
            self.provider = get_embedding_provider()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.provider.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        vectors = self.provider.embed([text])
        return vectors[0] if vectors else []
