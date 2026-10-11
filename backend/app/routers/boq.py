import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project, BOQItem, ChangeRegion, CostImpact
from ..schemas import BOQItemResponse, CostImpactResponse
from ..services.boq_service import parse_boq_excel

router = APIRouter(prefix="/api/boq", tags=["BOQ"])

UPLOAD_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))


@router.post("/upload", response_model=list[BOQItemResponse])
def upload_boq_spreadsheet(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Hanya file Excel (.xlsx / .xls) yang diperbolehkan")

    project_dir = os.path.join(UPLOAD_ROOT, f"project_{project_id}")
    os.makedirs(project_dir, exist_ok=True)

    excel_path = os.path.join(project_dir, file.filename)
    with open(excel_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed_items = parse_boq_excel(excel_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mem-parsing spreadsheet BOQ: {str(e)}")

    if not parsed_items:
        raise HTTPException(status_code=400, detail="Tidak ada baris pekerjaan valid yang berhasil diekstrak dari file")

    # Bersihkan item lama jika ada
    db.query(BOQItem).filter(BOQItem.project_id == project_id).delete()

    created_items = []
    for item in parsed_items:
        boq_record = BOQItem(
            project_id=project_id,
            code=item["code"],
            description=item["description"],
            unit=item["unit"],
            contract_volume=item["contract_volume"],
            unit_price=item["unit_price"],
        )
        db.add(boq_record)
        created_items.append(boq_record)

    db.commit()
    for it in created_items:
        db.refresh(it)

    return created_items


@router.get("/by-project/{project_id}", response_model=list[BOQItemResponse])
def get_project_boq(project_id: int, db: Session = Depends(get_db)):
    return db.query(BOQItem).filter(BOQItem.project_id == project_id).order_by(BOQItem.id.asc()).all()


@router.post("/link-region", response_model=CostImpactResponse)
def link_region_to_boq(
    region_id: int,
    boq_item_id: int,
    db: Session = Depends(get_db),
):
    region = db.query(ChangeRegion).filter(ChangeRegion.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Change region not found")

    if not region.verification:
        raise HTTPException(status_code=400, detail="Region belum diverifikasi dimensinya. Lakukan verifikasi dimensi terlebih dahulu.")

    boq_item = db.query(BOQItem).filter(BOQItem.id == boq_item_id).first()
    if not boq_item:
        raise HTTPException(status_code=404, detail="BOQ item not found")

    cost_impact = db.query(CostImpact).filter(CostImpact.change_region_id == region_id).first()
    if not cost_impact:
        cost_impact = CostImpact(change_region_id=region_id)
        db.add(cost_impact)

    delta_vol = region.verification.delta_volume_m3
    cost_impact.boq_item_id = boq_item.id
    cost_impact.delta_volume = delta_vol
    cost_impact.unit_price = boq_item.unit_price
    cost_impact.total_cost_delta = round(delta_vol * boq_item.unit_price, 2)

    db.commit()
    db.refresh(cost_impact)
    return cost_impact
