"""Router modul Progress & EVM."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import ProgressEntry
from ...schemas import (
    ProgressEntryCreate,
    ProgressEntryResponse,
    ProgressSummaryResponse,
)
from .service import compute_progress_summary, upsert_progress_entry

router = APIRouter(tags=["Progress & EVM"])


@router.get("/api/progress/{project_id}", response_model=ProgressSummaryResponse)
def get_progress_summary(project_id: int, db: Session = Depends(get_db)):
    """Ringkasan progres & EVM proyek dari periode terakhir."""
    try:
        return compute_progress_summary(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/progress/{project_id}/entries", response_model=list[ProgressEntryResponse])
def list_progress_entries(project_id: int, db: Session = Depends(get_db)):
    """Daftar catatan progres proyek, terurut periode menaik."""
    return (
        db.query(ProgressEntry)
        .filter(ProgressEntry.project_id == project_id)
        .order_by(ProgressEntry.period.asc())
        .all()
    )


@router.post("/api/progress/{project_id}/entries", response_model=ProgressEntryResponse)
def upsert_progress_entry_route(
    project_id: int, payload: ProgressEntryCreate, db: Session = Depends(get_db)
):
    """Simpan catatan progres periodik (upsert per project + period)."""
    try:
        return upsert_progress_entry(db, project_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
