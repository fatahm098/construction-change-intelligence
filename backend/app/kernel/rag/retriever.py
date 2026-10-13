"""Retriever — cari chunk relevan dan susun konteks bersitasi."""

from __future__ import annotations

from ..llm.base import ChatMessage, LLMProvider
from ..llm.factory import get_llm_provider
from .embedder import Embedder
from .store import SearchHit, vector_store

SYSTEM_PROMPT = (
    "Kamu adalah asisten teknik sipil untuk kontraktor Indonesia. "
    "Jawab HANYA berdasarkan konteks dokumen yang diberikan. "
    "Jika jawaban tidak ada di konteks, katakan dengan jujur bahwa informasinya "
    "tidak ditemukan di dokumen. Selalu sebutkan sumber (nama file dan halaman) "
    "untuk setiap klaim. JANGAN mengarang angka, volume, atau harga — "
    "perhitungan volume/biaya dilakukan oleh sistem deterministik, bukan olehmu."
)


class Retriever:
    def __init__(
        self,
        provider: LLMProvider | None = None,
        embedder: Embedder | None = None,
    ) -> None:
        self.provider = provider or get_llm_provider()
        self.embedder = embedder or Embedder(self.provider)

    def retrieve(
        self,
        query: str,
        *,
        project_id: int | None = None,
        top_k: int = 5,
    ) -> list[SearchHit]:
        query_vec = self.embedder.embed_query(query)
        if not query_vec:
            return []
        return vector_store.search(query_vec, project_id=project_id, top_k=top_k)

    def answer(
        self,
        query: str,
        *,
        project_id: int | None = None,
        top_k: int = 5,
        history: list[ChatMessage] | None = None,
    ) -> dict:
        """Jawab pertanyaan dengan konteks bersitasi.

        Mengembalikan dict: { answer, sources: [{filename, page, snippet, score}] }.
        """
        hits = self.retrieve(query, project_id=project_id, top_k=top_k)

        if not hits:
            return {
                "answer": (
                    "Belum ada dokumen yang relevan untuk proyek ini. "
                    "Unggah dokumen (RKS/kontrak/SNI) terlebih dahulu."
                ),
                "sources": [],
            }

        context_blocks = []
        for i, hit in enumerate(hits, start=1):
            c = hit.chunk
            loc = f"{c.filename}" + (f" hal. {c.page}" if c.page else "")
            context_blocks.append(f"[Sumber {i}] {loc}\n{c.text}")
        context = "\n\n".join(context_blocks)

        messages: list[ChatMessage] = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
        if history:
            messages.extend(history)
        messages.append(
            ChatMessage(
                role="user",
                content=f"Konteks dokumen:\n{context}\n\nPertanyaan: {query}",
            )
        )

        result = self.provider.chat(messages, temperature=0.2)

        sources = [
            {
                "filename": hit.chunk.filename,
                "page": hit.chunk.page,
                "snippet": hit.chunk.text[:200],
                "score": round(hit.score, 4),
            }
            for hit in hits
        ]

        return {"answer": result.content, "sources": sources}
