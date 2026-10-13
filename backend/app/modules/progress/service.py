"""Service Progress & EVM: kurva-S dan analisis nilai hasil (deterministik)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ...models import BOQItem, ProgressEntry, Project
from ...schemas import (
    ProgressEntryCreate,
    ProgressEntryResponse,
    ProgressPointResponse,
    ProgressSummaryResponse,
)


def _bac(db: Session, project_id: int) -> float:
    """Budget at Completion = Σ (volume_kontrak × harga_satuan) seluruh item BOQ."""
    items = db.query(BOQItem).filter(BOQItem.project_id == project_id).all()
    return sum((it.contract_volume or 0.0) * (it.unit_price or 0.0) for it in items)


def compute_progress_summary(db: Session, project_id: int) -> ProgressSummaryResponse:
    """Hitung ringkasan progres & EVM proyek dari periode terakhir."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    entries = (
        db.query(ProgressEntry)
        .filter(ProgressEntry.project_id == project_id)
        .order_by(ProgressEntry.period.asc())
        .all()
    )
    bac = _bac(db, project_id)

    periods = [
        ProgressPointResponse(
            period=e.period,
            planned_pct=round(e.planned_pct or 0.0, 4),
            actual_pct=round(e.actual_pct or 0.0, 4),
            planned_value=round((e.planned_pct or 0.0) / 100 * bac, 2),
            earned_value=round((e.actual_pct or 0.0) / 100 * bac, 2),
            actual_cost=round(e.actual_cost or 0.0, 2),
        )
        for e in entries
    ]

    if not entries:
        return ProgressSummaryResponse(
            project_id=project.id,
            project_name=project.name,
            bac=round(bac, 2),
            pv=0.0,
            ev=0.0,
            ac=0.0,
            sv=0.0,
            cv=0.0,
            spi=0.0,
            cpi=0.0,
            eac=round(bac, 2),
            etc=round(bac, 2),
            vac=0.0,
            progress_pct=0.0,
            periods=[],
        )

    latest = entries[-1]
    planned_pct = latest.planned_pct or 0.0
    actual_pct = latest.actual_pct or 0.0
    ac = latest.actual_cost or 0.0

    pv = planned_pct / 100 * bac
    ev = actual_pct / 100 * bac
    sv = ev - pv
    cv = ev - ac
    spi = ev / pv if pv else 0.0
    cpi = ev / ac if ac else 0.0
    eac = bac / cpi if cpi else bac
    etc = eac - ac
    vac = bac - eac

    return ProgressSummaryResponse(
        project_id=project.id,
        project_name=project.name,
        bac=round(bac, 2),
        pv=round(pv, 2),
        ev=round(ev, 2),
        ac=round(ac, 2),
        sv=round(sv, 2),
        cv=round(cv, 2),
        spi=round(spi, 4),
        cpi=round(cpi, 4),
        eac=round(eac, 2),
        etc=round(etc, 2),
        vac=round(vac, 2),
        progress_pct=round(actual_pct, 4),
        periods=periods,
    )


def upsert_progress_entry(
    db: Session, project_id: int, payload: ProgressEntryCreate
) -> ProgressEntryResponse:
    """Simpan catatan progres; perbarui bila periode yang sama sudah ada."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    entry = (
        db.query(ProgressEntry)
        .filter(
            ProgressEntry.project_id == project_id,
            ProgressEntry.period == payload.period,
        )
        .first()
    )

    if entry:
        entry.planned_pct = payload.planned_pct
        entry.actual_pct = payload.actual_pct
        entry.actual_cost = payload.actual_cost
        entry.note = payload.note
    else:
        entry = ProgressEntry(
            project_id=project_id,
            period=payload.period,
            planned_pct=payload.planned_pct,
            actual_pct=payload.actual_pct,
            actual_cost=payload.actual_cost,
            note=payload.note,
        )
        db.add(entry)

    db.commit()
    db.refresh(entry)
    return ProgressEntryResponse.model_validate(entry)
