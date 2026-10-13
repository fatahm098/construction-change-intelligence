"""Router modul VO & RFI (Variation Order & Request for Information)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import (
    RFIAnswerRequest,
    RFICreate,
    RFIResponse,
    VariationOrderCreate,
    VariationOrderResponse,
    VOStatusUpdate,
)
from .service import (
    answer_rfi,
    create_rfi,
    create_variation_order,
    list_rfis,
    list_variation_orders,
    update_vo_status,
)

router = APIRouter(tags=["VO & RFI"])


@router.get("/api/vo/{project_id}", response_model=list[VariationOrderResponse])
def get_variation_orders(project_id: int, db: Session = Depends(get_db)):
    """Daftar Variation Order sebuah proyek."""
    return list_variation_orders(db, project_id)


@router.post("/api/vo/{project_id}", response_model=VariationOrderResponse)
def post_variation_order(
    project_id: int, payload: VariationOrderCreate, db: Session = Depends(get_db)
):
    """Buat Variation Order baru untuk sebuah proyek."""
    return create_variation_order(db, project_id, payload)


@router.patch("/api/vo/{vo_id}/status", response_model=VariationOrderResponse)
def patch_vo_status(vo_id: int, payload: VOStatusUpdate, db: Session = Depends(get_db)):
    """Perbarui status sebuah Variation Order."""
    try:
        return update_vo_status(db, vo_id, payload.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/rfi/{project_id}", response_model=list[RFIResponse])
def get_rfis(project_id: int, db: Session = Depends(get_db)):
    """Daftar RFI sebuah proyek."""
    return list_rfis(db, project_id)


@router.post("/api/rfi/{project_id}", response_model=RFIResponse)
def post_rfi(project_id: int, payload: RFICreate, db: Session = Depends(get_db)):
    """Buat RFI baru untuk sebuah proyek."""
    return create_rfi(db, project_id, payload)


@router.post("/api/rfi/{rfi_id}/answer", response_model=RFIResponse)
def post_rfi_answer(rfi_id: int, payload: RFIAnswerRequest, db: Session = Depends(get_db)):
    """Jawab sebuah RFI."""
    try:
        return answer_rfi(db, rfi_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
