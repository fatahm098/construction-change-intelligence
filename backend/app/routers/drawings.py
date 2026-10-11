import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project, Drawing
from ..schemas import DrawingResponse
from ..services.pdf_service import rasterize_pdf_page

router = APIRouter(prefix="/api/drawings", tags=["Drawings"])

UPLOAD_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
os.makedirs(UPLOAD_ROOT, exist_ok=True)


@router.post("/upload", response_model=DrawingResponse)
def upload_drawing(
    project_id: int = Form(...),
    revision: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file berekstensi .pdf yang diperbolehkan")

    # Folder simpan per project
    project_dir = os.path.join(UPLOAD_ROOT, f"project_{project_id}")
    os.makedirs(project_dir, exist_ok=True)

    pdf_path = os.path.join(project_dir, f"rev{revision}_{file.filename}")
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Otomatis rasterize halaman 0 ke PNG 150 DPI
    try:
        png_path, width_px, height_px = rasterize_pdf_page(pdf_path, page_number=0, dpi=150, output_dir=project_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal me-rasterize PDF: {str(e)}")

    drawing = Drawing(
        project_id=project_id,
        filename=file.filename,
        file_path=pdf_path,
        revision=revision,
        png_path=png_path,
        width_px=width_px,
        height_px=height_px,
    )
    db.add(drawing)
    db.commit()
    db.refresh(drawing)
    return drawing


@router.get("/by-project/{project_id}", response_model=list[DrawingResponse])
def get_project_drawings(project_id: int, db: Session = Depends(get_db)):
    return db.query(Drawing).filter(Drawing.project_id == project_id).order_by(Drawing.revision.asc()).all()
