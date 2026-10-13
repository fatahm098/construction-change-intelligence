"""Service Document Q&A: ingest dokumen & jawab pertanyaan (RAG)."""

from __future__ import annotations

import json
import os

import pymupdf
from sqlalchemy.orm import Session

from ...kernel.rag.chunker import chunk_pages
from ...kernel.rag.embedder import Embedder
from ...kernel.rag.retriever import Retriever
from ...kernel.rag.store import StoredChunk, vector_store
from ...models import Conversation, Document, DocumentChunk, DocumentStatus


def extract_pdf_pages(file_path: str) -> list[tuple[int, str]]:
    """Ekstrak teks per halaman dari PDF. Nomor halaman 1-based untuk sitasi."""
    doc = pymupdf.open(file_path)
    pages: list[tuple[int, str]] = []
    for i in range(len(doc)):
        text = doc[i].get_text().strip()
        if text:
            pages.append((i + 1, text))
    doc.close()
    return pages


def ingest_document(db: Session, document: Document) -> Document:
    """Parse PDF → chunk → embed → simpan ke vector store & DB.

    Mengubah status Document menjadi INDEXED atau FAILED.
    """
    try:
        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"File tidak ditemukan: {document.file_path}")

        pages = extract_pdf_pages(document.file_path)
        if not pages:
            raise ValueError(
                "Tidak ada teks yang dapat diekstrak dari dokumen (mungkin hasil scan gambar)."
            )

        chunks = chunk_pages(pages)
        if not chunks:
            raise ValueError("Dokumen tidak menghasilkan chunk.")

        embedder = Embedder()
        embeddings = embedder.embed_texts([c.text for c in chunks])
        if len(embeddings) != len(chunks):
            raise ValueError("Jumlah embedding tidak cocok dengan jumlah chunk.")

        stored: list[StoredChunk] = []
        for chunk, emb in zip(chunks, embeddings):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk.chunk_index,
                    page=chunk.page,
                    text=chunk.text,
                    embedding_json=json.dumps(emb),
                )
            )
            stored.append(
                StoredChunk(
                    document_id=document.id,
                    project_id=document.project_id,
                    filename=document.filename,
                    text=chunk.text,
                    embedding=emb,
                    chunk_index=chunk.chunk_index,
                    page=chunk.page,
                )
            )

        vector_store.add(stored)
        document.num_chunks = len(chunks)
        document.status = DocumentStatus.INDEXED
        document.error_message = None
        db.commit()
        db.refresh(document)
        return document

    except Exception as e:  # noqa: BLE001 — simpan pesan error ke record
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        db.refresh(document)
        return document


def answer_question(
    db: Session,
    *,
    project_id: int,
    question: str,
    top_k: int = 5,
) -> dict:
    """Jawab pertanyaan dengan RAG dan simpan ke riwayat Conversation."""
    retriever = Retriever()
    result = retriever.answer(question, project_id=project_id, top_k=top_k)

    convo = Conversation(
        project_id=project_id,
        question=question,
        answer=result["answer"],
        sources_json=json.dumps(result["sources"], ensure_ascii=False),
    )
    db.add(convo)
    db.commit()

    return result


def hydrate_vector_store(db: Session) -> int:
    """Muat ulang embedding dari DB ke vector store in-memory.

    Dipanggil saat startup karena store in-memory hilang setiap server restart.
    Kembalikan jumlah chunk yang dimuat.
    """
    if vector_store.count() > 0:
        return 0

    rows = (
        db.query(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.status == DocumentStatus.INDEXED)
        .all()
    )

    stored: list[StoredChunk] = []
    for row in rows:
        if not row.embedding_json:
            continue
        try:
            embedding = json.loads(row.embedding_json)
        except (ValueError, TypeError):
            continue
        stored.append(
            StoredChunk(
                document_id=row.document_id,
                project_id=row.document.project_id,
                filename=row.document.filename,
                text=row.text,
                embedding=embedding,
                chunk_index=row.chunk_index,
                page=row.page,
            )
        )

    if stored:
        vector_store.add(stored)
    return len(stored)
