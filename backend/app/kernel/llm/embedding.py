"""Provider embedding yang dapat ditukar lewat konfigurasi.

Tiga implementasi:

- `HashEmbeddingProvider` — default offline, membungkus `local.hash_embedding`
  (kemiripan leksikal, tanpa API key, tanpa unduhan model).
- `LocalEmbeddingProvider` — model open-source lewat `sentence-transformers`
  (default: `intfloat/multilingual-e5-small`), jalan di CPU, gratis.
- `OpenAICompatibleEmbeddingProvider` — endpoint `/embeddings` milik layanan
  OpenAI-compatible (OpenAI, Gemini, Together, dsb.).

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

    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        """Embedding untuk query pencarian.

        Default sama dengan `embed`. Provider yang membedakan query dan dokumen
        (mis. E5 memakai prefiks `query:` / `passage:`) menimpanya.
        """
        return self.embed(texts)


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


class LocalEmbeddingProvider(EmbeddingProvider):
    """Embedding open-source via sentence-transformers (CPU, tanpa API key).

    Default `intfloat/multilingual-e5-small` (±118 MB, 384 dimensi) yang
    mendukung bahasa Indonesia. Model E5 mewajibkan prefiks `passage:` untuk
    dokumen dan `query:` untuk pertanyaan — tanpa itu kualitas turun.
    """

    name = "local"

    def __init__(self, model_name: str, *, batch_size: int = 32) -> None:
        self.model = model_name
        self.batch_size = batch_size
        self._encoder = None
        self._use_e5_prefix = "e5" in model_name.lower()

    def _ensure_encoder(self):
        if self._encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover - bergantung lingkungan
                raise RuntimeError(
                    "sentence-transformers belum terpasang. Jalankan: "
                    "pip install sentence-transformers"
                ) from exc
            self._encoder = SentenceTransformer(self.model, device="cpu")
            self.dimensions = self._encoder.get_sentence_embedding_dimension()
        return self._encoder

    def _encode(self, texts: list[str], *, is_query: bool) -> list[list[float]]:
        if not texts:
            return []
        encoder = self._ensure_encoder()
        prefix = ""
        if self._use_e5_prefix:
            prefix = "query: " if is_query else "passage: "
        vectors = encoder.encode(
            [f"{prefix}{text}" for text in texts],
            batch_size=self.batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return [vector.tolist() for vector in vectors]

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts, is_query=False)

    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts, is_query=True)


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

    if provider == "local":
        return LocalEmbeddingProvider(settings.embedding_local_model)

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
