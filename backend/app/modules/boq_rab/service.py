"""Service BOQ & RAB: perhitungan RAB + rekomendasi item BOQ."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...models import AnalysisRun, BOQItem, ChangeRegion, CostImpact, Project, RegionStatus
from ...schemas import BOQSuggestionResponse, RABLineResponse, RABResponse
from ...services.boq_service import suggest_boq_item


def _delta_by_boq_item(db: Session, project_id: int) -> dict[int, float]:
    """Total Δvolume per BOQ item dari region yang sudah diverifikasi."""
    rows = (
        db.query(CostImpact.boq_item_id, func.coalesce(func.sum(CostImpact.delta_volume), 0.0))
        .join(ChangeRegion, CostImpact.change_region_id == ChangeRegion.id)
        .join(AnalysisRun, ChangeRegion.analysis_run_id == AnalysisRun.id)
        .filter(
            AnalysisRun.project_id == project_id,
            ChangeRegion.status == RegionStatus.VERIFIED,
        )
        .group_by(CostImpact.boq_item_id)
        .all()
    )
    return {boq_id: float(total) for boq_id, total in rows}


def compute_rab(db: Session, project_id: int) -> RABResponse:
    """Hitung RAB kontrak & RAB setelah variasi untuk sebuah proyek."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    items = (
        db.query(BOQItem).filter(BOQItem.project_id == project_id).order_by(BOQItem.id.asc()).all()
    )
    delta_map = _delta_by_boq_item(db, project_id)

    verified_region_count = (
        db.query(ChangeRegion)
        .join(AnalysisRun, ChangeRegion.analysis_run_id == AnalysisRun.id)
        .filter(
            AnalysisRun.project_id == project_id,
            ChangeRegion.status == RegionStatus.VERIFIED,
        )
        .count()
    )

    lines: list[RABLineResponse] = []
    total_contract = 0.0
    total_adjusted = 0.0

    for it in items:
        delta_vol = delta_map.get(it.id, 0.0)
        adjusted_vol = it.contract_volume + delta_vol
        contract_amount = it.contract_volume * it.unit_price
        adjusted_amount = adjusted_vol * it.unit_price
        delta_amount = adjusted_amount - contract_amount

        total_contract += contract_amount
        total_adjusted += adjusted_amount

        lines.append(
            RABLineResponse(
                boq_item_id=it.id,
                code=it.code,
                description=it.description,
                unit=it.unit,
                contract_volume=round(it.contract_volume, 3),
                delta_volume=round(delta_vol, 3),
                adjusted_volume=round(adjusted_vol, 3),
                unit_price=it.unit_price,
                contract_amount=round(contract_amount, 2),
                adjusted_amount=round(adjusted_amount, 2),
                delta_amount=round(delta_amount, 2),
                ahsp_item_id=it.ahsp_item_id,
                ahsp_code=it.ahsp_item.code if it.ahsp_item else None,
            )
        )

    return RABResponse(
        project_id=project.id,
        project_name=project.name,
        lines=lines,
        total_contract=round(total_contract, 2),
        total_adjusted=round(total_adjusted, 2),
        total_delta=round(total_adjusted - total_contract, 2),
        item_count=len(lines),
        verified_region_count=verified_region_count,
    )


def suggest_boq_for_region(db: Session, region_id: int) -> BOQSuggestionResponse:
    """Rekomendasikan item BOQ untuk sebuah change region (berbasis kata kunci)."""
    region = db.query(ChangeRegion).filter(ChangeRegion.id == region_id).first()
    if not region:
        raise ValueError("Change region not found")

    run = db.query(AnalysisRun).filter(AnalysisRun.id == region.analysis_run_id).first()
    element_type = "other"
    if region.verification:
        element_type = region.verification.element_type.value

    items = (
        db.query(BOQItem)
        .filter(BOQItem.project_id == run.project_id)
        .order_by(BOQItem.id.asc())
        .all()
    )

    match = suggest_boq_item(element_type, items)

    if match:
        return BOQSuggestionResponse(
            region_id=region_id,
            element_type=element_type,
            suggested_boq_item_id=match.id,
            suggested_code=match.code,
            suggested_description=match.description,
            unit_price=match.unit_price,
            reason=f"Cocok berdasarkan kata kunci tipe elemen '{element_type}' pada uraian pekerjaan.",
        )

    return BOQSuggestionResponse(
        region_id=region_id,
        element_type=element_type,
        reason="Tidak ada item BOQ yang cocok. Pilih manual dari daftar RAB.",
    )
