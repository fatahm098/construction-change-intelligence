"""Script uji manual Fase 2: ingest PDF RKS lalu tanya jawab (RAG)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal  # noqa: E402
from app.models import Document, DocumentType, Project  # noqa: E402
from app.modules.doc_qa.service import answer_question, ingest_document  # noqa: E402

db = SessionLocal()

# Ambil project pertama
project = db.query(Project).first()
if not project:
    project = Project(name="Proyek Uji RAG", description="Test Fase 2")
    db.add(project)
    db.commit()
    db.refresh(project)
print(f"Project: #{project.id} {project.name}")

pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "_test_rks.pdf")

doc = Document(
    project_id=project.id,
    filename="_test_rks.pdf",
    file_path=pdf_path,
    doc_type=DocumentType.RKS,
)
db.add(doc)
db.commit()
db.refresh(doc)

print("Ingesting...")
doc = ingest_document(db, doc)
print(f"Status: {doc.status.value}, chunks: {doc.num_chunks}, error: {doc.error_message}")

if doc.status.value == "indexed":
    question = "Apa syarat pengajuan Variation Order dan berapa lama batas waktu pengajuan Extension of Time?"
    print(f"\nQ: {question}")
    result = answer_question(db, project_id=project.id, question=question, top_k=3)
    print(f"\nA: {result['answer']}")
    print("\nSumber:")
    for s in result["sources"]:
        print(f"  - {s['filename']} hal.{s['page']} (score {s['score']})")

db.close()
