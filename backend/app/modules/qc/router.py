"""Router modul QC / Mutu (inspeksi mutu pekerjaan)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.qc import (
    InspectionCreate,
    InspectionItemResponse,
    InspectionItemUpdate,
    InspectionResponse,
    InspectionStatusUpdate,
    QCSummaryResponse,
)
from .service import (
    compute_qc_summary,
    create_inspection,
    get_inspection,
    list_inspections,
    set_inspection_status,
    update_inspection_item,
)

router = APIRouter(tags=["QC / Mutu"])


@router.get("/api/qc/summary/{project_id}", response_model=QCSummaryResponse)
def get_qc_summary(project_id: int, db: Session = Depends(get_db)):
    """Rekap mutu sebuah proyek (jumlah inspeksi, pass rate, butir tidak OK)."""
    return compute_qc_summary(db, project_id)


@router.get("/api/qc/inspection/{inspection_id}", response_model=InspectionResponse)
def get_inspection_detail(inspection_id: int, db: Session = Depends(get_db)):
    """Detail satu inspeksi beserta butir-butir pemeriksaannya."""
    try:
        return get_inspection(db, inspection_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/qc/{project_id}", response_model=list[InspectionResponse])
def get_inspections(project_id: int, db: Session = Depends(get_db)):
    """Daftar inspeksi mutu sebuah proyek."""
    return list_inspections(db, project_id)


@router.post("/api/qc/{project_id}", response_model=InspectionResponse)
def post_inspection(
    project_id: int, payload: InspectionCreate, db: Session = Depends(get_db)
):
    """Buat inspeksi mutu baru beserta butir pemeriksaannya."""
    return create_inspection(db, project_id, payload)


@router.patch("/api/qc/item/{item_id}", response_model=InspectionItemResponse)
def patch_inspection_item(
    item_id: int, payload: InspectionItemUpdate, db: Session = Depends(get_db)
):
    """Perbarui hasil dan/atau catatan sebuah butir pemeriksaan."""
    try:
        return update_inspection_item(db, item_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/api/qc/inspection/{inspection_id}/status", response_model=InspectionResponse)
def patch_inspection_status(
    inspection_id: int, payload: InspectionStatusUpdate, db: Session = Depends(get_db)
):
    """Finalisasi status inspeksi setelah seluruh butir diperiksa."""
    try:
        return set_inspection_status(db, inspection_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
