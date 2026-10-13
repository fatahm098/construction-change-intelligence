from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import (
    AnalysisRun,
    ChangeRegion,
    DimensionVerification,
    CostImpact,
    BOQItem,
    RegionStatus,
)
from ..schemas import (
    AnalysisRunResponse,
    ChangeRegionResponse,
    DimensionVerificationCreate,
    DimensionVerificationResponse,
)
from ..services.analysis_service import run_analysis as run_analysis_service
from ..services.calc_service import calculate_element_volumes

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/run", response_model=AnalysisRunResponse)
def run_analysis(
    project_id: int = Query(...),
    drawing_ref_id: int = Query(...),
    drawing_rev_id: int = Query(...),
    min_area: int = Query(350),
    db: Session = Depends(get_db),
):
    """Jalankan analisis gambar secara sinkron (jalur default `jobs_enabled=false`)."""
    return run_analysis_service(
        db,
        project_id=project_id,
        drawing_ref_id=drawing_ref_id,
        drawing_rev_id=drawing_rev_id,
        min_area=min_area,
    )


@router.get("/by-project/{project_id}", response_model=AnalysisRunResponse)
def get_latest_run_for_project(project_id: int, db: Session = Depends(get_db)):
    """Ambil analysis run terbaru untuk sebuah project."""
    run = (
        db.query(AnalysisRun)
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.verification))
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.cost_impact))
        .filter(AnalysisRun.project_id == project_id)
        .order_by(AnalysisRun.created_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Belum ada analisis untuk project ini")
    return run


@router.get("/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(AnalysisRun)
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.verification))
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.cost_impact))
        .filter(AnalysisRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run


@router.post("/region/{region_id}/verify", response_model=DimensionVerificationResponse)
def verify_region_dimension(
    region_id: int,
    payload: DimensionVerificationCreate,
    db: Session = Depends(get_db),
):
    region = db.query(ChangeRegion).filter(ChangeRegion.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Change region not found")

    # Hitung volume deterministik
    vol0, vol1, delta_vol = calculate_element_volumes(
        element_type=payload.element_type,
        dim_before_w_mm=payload.dim_before_w,
        dim_before_h_mm=payload.dim_before_h,
        dim_after_w_mm=payload.dim_after_w,
        dim_after_h_mm=payload.dim_after_h,
        height_or_length_m=payload.height_or_length_m,
    )

    # Simpan atau update verifikasi
    verification = db.query(DimensionVerification).filter(DimensionVerification.change_region_id == region_id).first()
    if not verification:
        verification = DimensionVerification(change_region_id=region_id)
        db.add(verification)

    verification.element_type = payload.element_type
    verification.dim_before_w = payload.dim_before_w
    verification.dim_before_h = payload.dim_before_h
    verification.dim_after_w = payload.dim_after_w
    verification.dim_after_h = payload.dim_after_h
    verification.height_or_length_m = payload.height_or_length_m
    verification.volume_before_m3 = vol0
    verification.volume_after_m3 = vol1
    verification.delta_volume_m3 = delta_vol

    region.status = RegionStatus.VERIFIED

    # Jika user menghubungkan ke item BOQ saat verifikasi
    if payload.link_boq_item_id:
        boq_item = db.query(BOQItem).filter(BOQItem.id == payload.link_boq_item_id).first()
        if boq_item:
            cost_impact = db.query(CostImpact).filter(CostImpact.change_region_id == region_id).first()
            if not cost_impact:
                cost_impact = CostImpact(change_region_id=region_id)
                db.add(cost_impact)

            cost_impact.boq_item_id = boq_item.id
            cost_impact.delta_volume = delta_vol
            cost_impact.unit_price = boq_item.unit_price
            cost_impact.total_cost_delta = round(delta_vol * boq_item.unit_price, 2)

    db.commit()
    db.refresh(verification)
    return verification


@router.post("/region/{region_id}/reject", response_model=ChangeRegionResponse)
def reject_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(ChangeRegion).filter(ChangeRegion.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Change region not found")

    region.status = RegionStatus.REJECTED
    # Hapus verifikasi atau cost impact jika ada
    if region.verification:
        db.delete(region.verification)
    if region.cost_impact:
        db.delete(region.cost_impact)

    db.commit()
    db.refresh(region)
    return region
