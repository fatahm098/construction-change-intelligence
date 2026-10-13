"""Logika inti analisis perubahan gambar (dipakai endpoint sync & worker async).

Dipisah dari router agar bisa dijalankan baik di dalam request
(`jobs_enabled=false`) maupun di worker ARQ (`jobs_enabled=true`) tanpa duplikasi.
"""

from __future__ import annotations

import os

import cv2
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ..models import (
    AnalysisRun,
    ChangeRegion,
    Drawing,
    Project,
    RegionStatus,
)
from .ocr_service import extract_text_and_dimensions
from .vision_service import align_drawings_sift, detect_changed_regions

OUTPUT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "analysis_runs")
)
os.makedirs(OUTPUT_ROOT, exist_ok=True)


def run_analysis(
    db: Session,
    *,
    project_id: int,
    drawing_ref_id: int,
    drawing_rev_id: int,
    min_area: int = 350,
) -> AnalysisRun:
    """Jalankan analisis diff dua revisi gambar lalu simpan hasilnya.

    Mengembalikan `AnalysisRun` lengkap dengan relasi regions. Melempar
    `HTTPException` (404/400/500) bila prasyarat tidak terpenuhi.
    """
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
        db.add(
            ChangeRegion(
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
        )

    db.commit()

    # Muat ulang dengan relasi
    return (
        db.query(AnalysisRun)
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.verification))
        .options(joinedload(AnalysisRun.regions).joinedload(ChangeRegion.cost_impact))
        .filter(AnalysisRun.id == run_record.id)
        .first()
    )
