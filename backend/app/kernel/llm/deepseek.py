"""Provider LLM: DeepSeek (OpenAI-compatible).

Chat memakai endpoint DeepSeek `/chat/completions` (model `deepseek-chat`).
DeepSeek belum menyediakan endpoint embeddings, sehingga `embed()` memakai
hashing lokal (`local.hash_embedding`) agar pipeline RAG tetap berjalan tanpa
layanan tambahan.
"""

from __future__ import annotations

from .local import hash_embedding
from .openai import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    name = "deepseek"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        embedding_model: str = "deepseek-embedding",
        base_url: str = "https://api.deepseek.com/v1",
        timeout: float = 120.0,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            embedding_model=embedding_model,
            base_url=base_url,
            timeout=timeout,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embedding lokal berbasis hashing (DeepSeek tidak punya endpoint ini)."""
        return [hash_embedding(text) for text in texts]
