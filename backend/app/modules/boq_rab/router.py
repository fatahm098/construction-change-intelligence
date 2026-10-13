"""Router modul BOQ & RAB (AHSP)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import AHSPItem
from ...schemas import (
    AHSPComponentResponse,
    AHSPItemResponse,
    BOQSuggestionResponse,
    RABResponse,
)
from ...services.ahsp_seed import seed_ahsp
from .service import compute_rab, suggest_boq_for_region

router = APIRouter(tags=["BOQ & RAB"])


@router.get("/api/ahsp", response_model=list[AHSPItemResponse])
def list_ahsp(db: Session = Depends(get_db)):
    """Daftar katalog AHSP beserta harga satuan (tanpa rincian komponen)."""
    items = db.query(AHSPItem).order_by(AHSPItem.code.asc()).all()
    return [
        AHSPItemResponse(
            id=it.id,
            code=it.code,
            name=it.name,
            unit=it.unit,
            category=it.category,
            unit_price=it.unit_price,
            components=[],
        )
        for it in items
    ]


@router.get("/api/ahsp/{ahsp_id}", response_model=AHSPItemResponse)
def get_ahsp_detail(ahsp_id: int, db: Session = Depends(get_db)):
    """Detail AHSP beserta rincian komponen tenaga/bahan/alat."""
    item = db.query(AHSPItem).filter(AHSPItem.id == ahsp_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="AHSP item not found")

    components = [
        AHSPComponentResponse(
            id=c.id,
            component_type=c.component_type,
            name=c.name,
            coefficient=c.coefficient,
            unit=c.unit,
            base_price=c.base_price,
            subtotal=round(c.coefficient * c.base_price, 2),
        )
        for c in item.components
    ]
    return AHSPItemResponse(
        id=item.id,
        code=item.code,
        name=item.name,
        unit=item.unit,
        category=item.category,
        unit_price=item.unit_price,
        components=components,
    )


@router.post("/api/ahsp/seed")
def reseed_ahsp(db: Session = Depends(get_db)):
    """Isi ulang katalog AHSP dari data bawaan (idempotent)."""
    count = seed_ahsp(db, force=True)
    return {"seeded": count}


@router.get("/api/rab/{project_id}", response_model=RABResponse)
def get_rab(project_id: int, db: Session = Depends(get_db)):
    """Hitung RAB kontrak & RAB setelah variasi untuk sebuah proyek."""
    try:
        return compute_rab(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/boq/suggest/{region_id}", response_model=BOQSuggestionResponse)
def suggest_boq(region_id: int, db: Session = Depends(get_db)):
    """Rekomendasikan item BOQ/RAB untuk sebuah change region."""
    try:
        return suggest_boq_for_region(db, region_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
