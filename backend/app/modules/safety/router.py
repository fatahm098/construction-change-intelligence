"""Router modul K3 / Safety (keselamatan & kesehatan kerja)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.safety import (
    SafetyReportCreate,
    SafetyReportResponse,
    SafetyStatusUpdate,
    SafetySummaryResponse,
)
from .service import (
    compute_safety_summary,
    create_safety_report,
    list_safety_reports,
    update_safety_status,
)

router = APIRouter(tags=["K3 / Safety"])


@router.get("/api/k3/summary/{project_id}", response_model=SafetySummaryResponse)
def get_safety_summary(project_id: int, db: Session = Depends(get_db)):
    """Rekap K3 sebuah proyek (jumlah per status & tingkat keparahan)."""
    return compute_safety_summary(db, project_id)


@router.get("/api/k3/{project_id}", response_model=list[SafetyReportResponse])
def get_safety_reports(project_id: int, db: Session = Depends(get_db)):
    """Daftar laporan K3 sebuah proyek."""
    return list_safety_reports(db, project_id)


@router.post("/api/k3/{project_id}", response_model=SafetyReportResponse)
def post_safety_report(
    project_id: int, payload: SafetyReportCreate, db: Session = Depends(get_db)
):
    """Buat laporan K3 baru untuk sebuah proyek."""
    return create_safety_report(db, project_id, payload)


@router.patch("/api/k3/{report_id}/status", response_model=SafetyReportResponse)
def patch_safety_status(
    report_id: int, payload: SafetyStatusUpdate, db: Session = Depends(get_db)
):
    """Perbarui status sebuah laporan K3."""
    try:
        return update_safety_status(db, report_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
