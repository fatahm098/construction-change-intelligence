import os
import cv2
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import (
    Project,
    Drawing,
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
from ..services.vision_service import align_drawings_sift, detect_changed_regions
from ..services.ocr_service import extract_text_and_dimensions
from ..services.calc_service import calculate_element_volumes

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

OUTPUT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "analysis_runs"))
os.makedirs(OUTPUT_ROOT, exist_ok=True)


@router.post("/run", response_model=AnalysisRunResponse)
def run_analysis(
    project_id: int = Query(...),
    drawing_ref_id: int = Query(...),
    drawing_rev_id: int = Query(...),
    min_area: int = Query(350),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    dwg_ref = db.query(Drawing).filter(Drawing.id == drawing_ref_id, Drawing.project_id == project_id).first()
    dwg_rev = db.query(Drawing).filter(Drawing.id == drawing_rev_id, Drawing.project_id == project_id).first()

    if not dwg_ref or not dwg_rev:
        raise HTTPException(status_code=400, detail="Salah satu atau kedua drawing tidak ditemukan di project ini")

    if not os.path.exists(dwg_ref.png_path) or not os.path.exists(dwg_rev.png_path):
        raise HTTPException(status_code=500, detail="File PNG raster untuk salah satu drawing tidak tersedia di disk")

    # Siapkan output run folder
    run_record = AnalysisRun(
        project_id=project_id,
        drawing_ref_id=drawing_ref_id,
        drawing_rev_id=drawing_rev_id,
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    run_dir = os.path.join(OUTPUT_ROOT, f"run_{run_record.id}")
    os.makedirs(run_dir, exist_ok=True)

    img_v0 = cv2.imread(dwg_ref.png_path)
    img_v1 = cv2.imread(dwg_rev.png_path)

    # 1. Alignment (SIFT)
    img_v0_aligned, _ = align_drawings_sift(img_v1, img_v0)

    # 2. Difference Detection
    regions_detected, diff_image_path = detect_changed_regions(
        img_v0_aligned, img_v1, min_area=min_area, output_dir=run_dir
    )

    run_record.diff_image_path = diff_image_path
    run_record.total_regions = len(regions_detected)

    # 3. Ekstraksi OCR per region
    for r in regions_detected:
        text_v0, dims_v0 = extract_text_and_dimensions(r["crop_v0"])
        text_v1, dims_v1 = extract_text_and_dimensions(r["crop_v1"])

        dim_str_v0 = f"{dims_v0[0]}x{dims_v0[1]}" if dims_v0 else None
        dim_str_v1 = f"{dims_v1[0]}x{dims_v1[1]}" if dims_v1 else None

        bx, by, bw, bh = r["bbox"]
        region_entity = ChangeRegion(
            analysis_run_id=run_record.id,
            region_index=r["region_index"],
            bbox_x=bx,
            bbox_y=by,
            bbox_w=bw,
            bbox_h=bh,
            area=r["area"],
            crop_v0_path=r["crop_v0_path"],
            crop_v1_path=r["crop_v1_path"],
            raw_text_v0=text_v0,
            raw_text_v1=text_v1,
            suggested_dim_v0=dim_str_v0,
            suggested_dim_v1=dim_str_v1,
            status=RegionStatus.PENDING,
        )
        db.add(region_entity)

    db.commit()

    # Muat ulang dengan relasi
    run_with_relations = (
        db.query(AnalysisRun)
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.verification))
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.cost_impact))
        .filter(AnalysisRun.id == run_record.id)
        .first()
    )
    return run_with_relations


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
