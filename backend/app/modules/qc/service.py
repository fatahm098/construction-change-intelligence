"""Service QC / Mutu: inspeksi mutu beserta butir pemeriksaan."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ...models import CheckResult, Inspection, InspectionItem, InspectionStatus
from ...schemas.qc import (
    InspectionCreate,
    InspectionItemResponse,
    InspectionItemUpdate,
    InspectionResponse,
    QCSummaryResponse,
)


def list_inspections(db: Session, project_id: int) -> list[InspectionResponse]:
    """Daftar inspeksi sebuah proyek, terurut id menaik."""
    rows = (
        db.query(Inspection)
        .filter(Inspection.project_id == project_id)
        .order_by(Inspection.id.asc())
        .all()
    )
    return [InspectionResponse.model_validate(r) for r in rows]


def create_inspection(
    db: Session, project_id: int, payload: InspectionCreate
) -> InspectionResponse:
    """Buat inspeksi baru beserta butir-butir pemeriksaannya (status DRAFT)."""
    inspection = Inspection(
        project_id=project_id,
        inspection_number=payload.inspection_number,
        title=payload.title,
        location=payload.location,
        category=payload.category,
        status=InspectionStatus.DRAFT,
        inspector=payload.inspector,
        inspected_at=payload.inspected_at,
        note=payload.note,
    )
    inspection.items = [
        InspectionItem(
            description=it.description,
            standard=it.standard,
            result=it.result,
            note=it.note,
        )
        for it in payload.items
    ]
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return InspectionResponse.model_validate(inspection)


def get_inspection(db: Session, inspection_id: int) -> InspectionResponse:
    """Ambil detail satu inspeksi beserta butir-butirnya."""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise ValueError("Inspection not found")
    return InspectionResponse.model_validate(inspection)


def update_inspection_item(
    db: Session, item_id: int, payload: InspectionItemUpdate
) -> InspectionItemResponse:
    """Perbarui hasil dan/atau catatan sebuah butir pemeriksaan."""
    item = db.query(InspectionItem).filter(InspectionItem.id == item_id).first()
    if not item:
        raise ValueError("Inspection item not found")

    if payload.result is not None:
        item.result = payload.result
    if payload.note is not None:
        item.note = payload.note

    db.commit()
    db.refresh(item)
    return InspectionItemResponse.model_validate(item)


def compute_qc_summary(db: Session, project_id: int) -> QCSummaryResponse:
    """Rekap mutu proyek: jumlah inspeksi per status, pass rate, dan butir tidak OK."""
    inspections = db.query(Inspection).filter(Inspection.project_id == project_id).all()
    total = len(inspections)
    passed = sum(1 for i in inspections if i.status == InspectionStatus.PASSED)
    failed = sum(1 for i in inspections if i.status == InspectionStatus.FAILED)
    draft = sum(1 for i in inspections if i.status == InspectionStatus.DRAFT)
    pass_rate = round(passed / total, 4) if total else 0.0

    base_items = (
        db.query(InspectionItem)
        .join(Inspection, InspectionItem.inspection_id == Inspection.id)
        .filter(Inspection.project_id == project_id)
    )
    total_items = base_items.count()
    not_ok_items = base_items.filter(InspectionItem.result == CheckResult.NOT_OK).count()

    return QCSummaryResponse(
        project_id=project_id,
        total=total,
        passed=passed,
        failed=failed,
        draft=draft,
        pass_rate=pass_rate,
        total_items=total_items,
        not_ok_items=not_ok_items,
    )
