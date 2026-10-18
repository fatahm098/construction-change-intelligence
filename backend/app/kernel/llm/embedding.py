"""Provider embedding yang dapat ditukar lewat konfigurasi.

Dua implementasi:

- `HashEmbeddingProvider` — default offline, membungkus `local.hash_embedding`
  (kemiripan leksikal, tanpa API key).
- `OpenAICompatibleEmbeddingProvider` — endpoint `/embeddings` milik layanan
  OpenAI-compatible (OpenAI, Together, dsb.) untuk embedding semantik.

Dimensi vektor berbeda antar provider/model, sehingga korpus lama harus
di-reindex setelah mengganti provider (lihat `POST /api/doc-qa/reindex`).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from ..config import settings
from .local import hash_embedding

_BATCH_SIZE = 64
_TIMEOUT_SECONDS = 60.0


class EmbeddingProvider(ABC):
    """Antarmuka provider embedding."""

    name: str = "base"
    dimensions: int | None = None
    model: str | None = None

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Kembalikan satu vektor untuk setiap teks (urutan dipertahankan)."""
        raise NotImplementedError


class HashEmbeddingProvider(EmbeddingProvider):
    """Embedding hashing lokal — deterministik, tanpa panggilan jaringan."""

    name = "hash"

    def __init__(self, dimensions: int = 512) -> None:
        self.dimensions = dimensions
        self.model = f"hash-{dimensions}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [hash_embedding(text, self.dimensions) for text in texts]


class OpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    """Provider embedding via `POST {base_url}/embeddings`."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        base_url: str = "https://api.openai.com/v1",
        *,
        batch_size: int = _BATCH_SIZE,
        timeout: float = _TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.batch_size = batch_size
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            vectors.extend(self._embed_batch(batch))
        return vectors

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        payload = {"model": self.model, "input": batch}

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers=self._headers(),
            )

        if resp.status_code != 200:
            detail = (resp.text or "")[:300]
            raise RuntimeError(
                f"Embedding gagal (HTTP {resp.status_code}) di {self.base_url} "
                f"untuk model '{self.model}': {detail}"
            )

        data = resp.json()
        items = sorted(data.get("data", []), key=lambda item: item.get("index", 0))
        if len(items) != len(batch):
            raise RuntimeError(
                f"Embedding mengembalikan {len(items)} vektor untuk {len(batch)} teks "
                f"(model '{self.model}' di {self.base_url})."
            )
        return [item["embedding"] for item in items]


def get_embedding_provider() -> EmbeddingProvider:
    """Provider embedding sesuai config; default/fallback ke hashing lokal."""
    provider = (settings.embedding_provider or "hash").strip().lower()

    if provider == "openai":
        api_key = settings.embedding_api_key or settings.openai_api_key
        if not api_key:
            raise RuntimeError("EMBEDDING_API_KEY belum diisi")
        return OpenAICompatibleEmbeddingProvider(
            api_key=api_key,
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
        )

    return HashEmbeddingProvider()
