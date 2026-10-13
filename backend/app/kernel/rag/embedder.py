"""Embedder — membungkus provider LLM untuk menghasilkan embedding."""

from __future__ import annotations

from ..llm.base import LLMProvider
from ..llm.factory import get_llm_provider


class Embedder:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or get_llm_provider()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.provider.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        vectors = self.provider.embed([text])
        return vectors[0] if vectors else []
