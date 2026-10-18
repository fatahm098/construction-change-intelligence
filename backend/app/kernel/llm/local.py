"""Provider LLM lokal (offline) — untuk dev/demo tanpa API key.

Tujuan: pipeline RAG tetap bisa dijalankan (ingest + pencarian + sitasi)
tanpa memanggil layanan eksternal. Kualitasnya BUKAN semantik seperti model
embedding sungguhan, melainkan kemiripan leksikal (kata/bigram) via hashing —
cukup untuk menguji alur dan pencarian berbasis kata kunci.

Untuk kualitas produksi, gunakan `LLM_PROVIDER=deepseek` (atau `ollama`).
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from .base import ChatMessage, ChatResult, LLMProvider

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_DEFAULT_DIM = 512


def _tokens(text: str) -> list[str]:
    """Tokenisasi sederhana: kata + bigram (huruf kecil)."""
    words = _TOKEN_RE.findall(text.lower())
    bigrams = [f"{a}_{b}" for a, b in zip(words, words[1:])]
    return words + bigrams


def hash_embedding(text: str, dim: int = _DEFAULT_DIM) -> list[float]:
    """Embedding deterministik berbasis hashing (signed hashing trick).

    Bobot sublinear (1 + log tf) lalu dinormalisasi L2, sehingga cosine
    similarity mendekati tumpang-tindih kata antar teks.
    """
    vec = [0.0] * dim
    tokens = _tokens(text)
    if not tokens:
        return vec

    for token, count in Counter(tokens).items():
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16)
        idx = h % dim
        sign = 1.0 if (h >> 31) & 1 else -1.0
        vec[idx] += sign * (1.0 + math.log(count))

    norm = math.sqrt(sum(v * v for v in vec))
    if norm:
        vec = [v / norm for v in vec]
    return vec


class LocalProvider(LLMProvider):
    """Provider offline: embedding hashing + jawaban ekstraktif (tanpa model)."""

    name = "local"

    def __init__(self, dim: int = _DEFAULT_DIM) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [hash_embedding(t, self.dim) for t in texts]

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> ChatResult:
        """Kembalikan potongan konteks teratas apa adanya (bukan rangkuman AI)."""
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        context = user
        marker = "Konteks dokumen:"
        if marker in user:
            context = user.split(marker, 1)[1]
        if "\n\nPertanyaan:" in context:
            context = context.split("\n\nPertanyaan:", 1)[0]
        context = context.strip()

        note = (
            "[Mode offline: LLM tidak dikonfigurasi, jadi ini BUKAN jawaban yang "
            "dirangkum AI — teks di bawah diambil langsung dari potongan dokumen "
            "paling relevan. Set LLM_PROVIDER=deepseek + DEEPSEEK_API_KEY untuk "
            "jawaban yang dirangkum.]"
        )
        content = f"{note}\n\n{context[:2000]}"
        return ChatResult(content=content, model="local-extractive", provider=self.name)

    def is_available(self) -> bool:
        return True
