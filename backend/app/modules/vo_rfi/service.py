"""Service VO & RFI: pencatatan Variation Order dan Request for Information."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ...models import RFI, RFIStatus, VariationOrder
from ...schemas import (
    RFIAnswerRequest,
    RFICreate,
    RFIResponse,
    VariationOrderCreate,
    VariationOrderResponse,
)


def list_variation_orders(db: Session, project_id: int) -> list[VariationOrderResponse]:
    """Daftar Variation Order sebuah proyek, terurut id menaik."""
    rows = (
        db.query(VariationOrder)
        .filter(VariationOrder.project_id == project_id)
        .order_by(VariationOrder.id.asc())
        .all()
    )
    return [VariationOrderResponse.model_validate(r) for r in rows]


def create_variation_order(
    db: Session, project_id: int, payload: VariationOrderCreate
) -> VariationOrderResponse:
    """Buat Variation Order baru untuk sebuah proyek."""
    vo = VariationOrder(
        project_id=project_id,
        vo_number=payload.vo_number,
        title=payload.title,
        description=payload.description,
        amount=payload.amount,
        change_region_id=payload.change_region_id,
    )
    db.add(vo)
    db.commit()
    db.refresh(vo)
    return VariationOrderResponse.model_validate(vo)


def update_vo_status(db: Session, vo_id: int, status) -> VariationOrderResponse:
    """Perbarui status sebuah Variation Order."""
    vo = db.query(VariationOrder).filter(VariationOrder.id == vo_id).first()
    if not vo:
        raise ValueError("Variation order not found")

    vo.status = status
    db.commit()
    db.refresh(vo)
    return VariationOrderResponse.model_validate(vo)


def list_rfis(db: Session, project_id: int) -> list[RFIResponse]:
    """Daftar RFI sebuah proyek, terurut id menaik."""
    rows = db.query(RFI).filter(RFI.project_id == project_id).order_by(RFI.id.asc()).all()
    return [RFIResponse.model_validate(r) for r in rows]


def create_rfi(db: Session, project_id: int, payload: RFICreate) -> RFIResponse:
    """Buat RFI baru untuk sebuah proyek."""
    rfi = RFI(
        project_id=project_id,
        rfi_number=payload.rfi_number,
        subject=payload.subject,
        question=payload.question,
        variation_order_id=payload.variation_order_id,
    )
    db.add(rfi)
    db.commit()
    db.refresh(rfi)
    return RFIResponse.model_validate(rfi)


def answer_rfi(db: Session, rfi_id: int, payload: RFIAnswerRequest) -> RFIResponse:
    """Jawab sebuah RFI dan tandai statusnya sebagai ANSWERED."""
    rfi = db.query(RFI).filter(RFI.id == rfi_id).first()
    if not rfi:
        raise ValueError("RFI not found")

    rfi.answer = payload.answer
    rfi.status = RFIStatus.ANSWERED
    rfi.answered_at = datetime.utcnow()
    db.commit()
    db.refresh(rfi)
    return RFIResponse.model_validate(rfi)
