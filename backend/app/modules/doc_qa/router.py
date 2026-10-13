"""Router modul Document Q&A."""

from __future__ import annotations

import json
import os
import shutil

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Conversation, Document, DocumentType, Project
from ...schemas import ChatRequest, ChatResponse, DocumentResponse
from .service import answer_question, ingest_document

router = APIRouter(prefix="/api/projects", tags=["Document Q&A"])

DOC_UPLOAD_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "documents")
)
os.makedirs(DOC_UPLOAD_ROOT, exist_ok=True)


@router.post("/{project_id}/documents", response_model=DocumentResponse)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(DocumentType.OTHER),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang diperbolehkan.")

    project_dir = os.path.join(DOC_UPLOAD_ROOT, f"project_{project_id}")
    os.makedirs(project_dir, exist_ok=True)
    pdf_path = os.path.join(project_dir, file.filename)
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        project_id=project_id,
        filename=file.filename,
        file_path=pdf_path,
        doc_type=doc_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Ingest sinkron (Fase 2). Akan dipindah ke background job di Fase 4.
    document = ingest_document(db, document)
    return document


@router.get("/{project_id}/documents", response_model=list[DocumentResponse])
def list_documents(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.project_id == project_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


@router.post("/{project_id}/chat", response_model=ChatResponse)
def chat(project_id: int, payload: ChatRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Pertanyaan tidak boleh kosong.")

    try:
        result = answer_question(
            db,
            project_id=project_id,
            question=payload.question,
            top_k=payload.top_k,
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Gagal memproses pertanyaan: {e}")

    return ChatResponse(answer=result["answer"], sources=result["sources"])


@router.get("/{project_id}/conversations")
def list_conversations(project_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Conversation)
        .filter(Conversation.project_id == project_id)
        .order_by(Conversation.created_at.asc())
        .all()
    )
    return [
        {
            "id": r.id,
            "question": r.question,
            "answer": r.answer,
            "sources": json.loads(r.sources_json) if r.sources_json else [],
            "created_at": r.created_at,
        }
        for r in rows
    ]
