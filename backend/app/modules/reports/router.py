"""Router modul Reports: unduhan Excel & PDF (RAB, EVM, QC)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ..boq_rab.service import compute_rab
from ..progress.service import compute_progress_summary
from .service import (
    build_evm_xlsx,
    build_qc_xlsx,
    build_rab_pdf,
    build_rab_xlsx,
    fetch_qc_data,
)

router = APIRouter(tags=["Reports"])

_XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_PDF_MEDIA = "application/pdf"


def _attachment(buf, media_type: str, filename: str) -> StreamingResponse:
    """Bungkus buffer memori menjadi respons unduhan."""
    return StreamingResponse(
        buf,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/reports/rab/{project_id}.xlsx")
def export_rab_xlsx(project_id: int, db: Session = Depends(get_db)):
    """Unduh RAB (Rencana Anggaran Biaya) sebagai Excel."""
    try:
        rab = compute_rab(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _attachment(build_rab_xlsx(rab), _XLSX_MEDIA, f"rab_{project_id}.xlsx")


@router.get("/api/reports/evm/{project_id}.xlsx")
def export_evm_xlsx(project_id: int, db: Session = Depends(get_db)):
    """Unduh ringkasan EVM sebagai Excel."""
    try:
        summary = compute_progress_summary(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _attachment(build_evm_xlsx(summary), _XLSX_MEDIA, f"evm_{project_id}.xlsx")


@router.get("/api/reports/qc/{project_id}.xlsx")
def export_qc_xlsx(project_id: int, db: Session = Depends(get_db)):
    """Unduh laporan inspeksi mutu (QC) sebagai Excel."""
    try:
        project_name, inspections = fetch_qc_data(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _attachment(
        build_qc_xlsx(project_name, inspections), _XLSX_MEDIA, f"qc_{project_id}.xlsx"
    )


@router.get("/api/reports/rab/{project_id}.pdf")
def export_rab_pdf(project_id: int, db: Session = Depends(get_db)):
    """Unduh RAB (Rencana Anggaran Biaya) sebagai PDF."""
    try:
        rab = compute_rab(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _attachment(build_rab_pdf(rab), _PDF_MEDIA, f"rab_{project_id}.pdf")
