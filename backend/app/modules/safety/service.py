"""Service K3 / Safety: laporan keselamatan & kesehatan kerja."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ...models import SafetyReport, SafetyStatus, Severity
from ...schemas.safety import (
    SafetyReportCreate,
    SafetyReportResponse,
    SafetySummaryResponse,
)


def list_safety_reports(db: Session, project_id: int) -> list[SafetyReportResponse]:
    """Daftar laporan K3 sebuah proyek, terurut id menaik."""
    rows = (
        db.query(SafetyReport)
        .filter(SafetyReport.project_id == project_id)
        .order_by(SafetyReport.id.asc())
        .all()
    )
    return [SafetyReportResponse.model_validate(r) for r in rows]


def create_safety_report(
    db: Session, project_id: int, payload: SafetyReportCreate
) -> SafetyReportResponse:
    """Buat laporan K3 baru untuk sebuah proyek (status OPEN)."""
    report = SafetyReport(
        project_id=project_id,
        report_number=payload.report_number,
        title=payload.title,
        category=payload.category,
        severity=payload.severity,
        description=payload.description,
        action_taken=payload.action_taken,
        status=SafetyStatus.OPEN,
        reported_by=payload.reported_by,
        occurred_at=payload.occurred_at,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return SafetyReportResponse.model_validate(report)


def update_safety_status(
    db: Session, report_id: int, status: SafetyStatus
) -> SafetyReportResponse:
    """Perbarui status sebuah laporan K3."""
    report = db.query(SafetyReport).filter(SafetyReport.id == report_id).first()
    if not report:
        raise ValueError("Safety report not found")

    report.status = status
    db.commit()
    db.refresh(report)
    return SafetyReportResponse.model_validate(report)


def compute_safety_summary(db: Session, project_id: int) -> SafetySummaryResponse:
    """Rekap K3 proyek: jumlah laporan per status dan per tingkat keparahan."""
    reports = (
        db.query(SafetyReport).filter(SafetyReport.project_id == project_id).all()
    )
    total = len(reports)
    open_count = sum(1 for r in reports if r.status == SafetyStatus.OPEN)
    investigating = sum(1 for r in reports if r.status == SafetyStatus.INVESTIGATING)
    closed = sum(1 for r in reports if r.status == SafetyStatus.CLOSED)

    by_severity: dict[str, int] = {s.value: 0 for s in Severity}
    for r in reports:
        by_severity[r.severity.value] += 1

    return SafetySummaryResponse(
        project_id=project_id,
        total=total,
        open=open_count,
        investigating=investigating,
        closed=closed,
        by_severity=by_severity,
    )
