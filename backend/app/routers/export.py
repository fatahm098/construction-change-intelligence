import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Project, AnalysisRun

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/csv/{project_id}")
def export_project_changes_csv(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output = io.StringIO()
    writer = csv.writer(output)

    # Header CSV
    writer.writerow([
        "Region ID",
        "Analysis Run ID",
        "Status",
        "Bounding Box (x,y,w,h)",
        "Raw OCR Rev 0",
        "Raw OCR Rev 1",
        "Tipe Elemen",
        "Dimensi Rev 0 (w x h mm)",
        "Dimensi Rev 1 (w x h mm)",
        "Tinggi / Panjang (m)",
        "Vol Rev 0 (m3)",
        "Vol Rev 1 (m3)",
        "Delta Vol (m3)",
        "Linked BOQ Item",
        "Harga Satuan (IDR)",
        "Total Dampak Biaya (IDR)",
    ])

    runs = db.query(AnalysisRun).filter(AnalysisRun.project_id == project_id).all()
    for run in runs:
        for reg in run.regions:
            status_str = reg.status.value
            bbox_str = f"({reg.bbox_x},{reg.bbox_y},{reg.bbox_w},{reg.bbox_h})"

            v = reg.verification
            ci = reg.cost_impact

            elem_type = v.element_type.value if v else "-"
            dim_v0_str = f"{v.dim_before_w}x{v.dim_before_h}" if v else (reg.suggested_dim_v0 or "-")
            dim_v1_str = f"{v.dim_after_w}x{v.dim_after_h}" if v else (reg.suggested_dim_v1 or "-")
            height_str = str(v.height_or_length_m) if v else "-"
            vol0_str = str(v.volume_before_m3) if v else "-"
            vol1_str = str(v.volume_after_m3) if v else "-"
            delta_vol_str = str(v.delta_volume_m3) if v else "-"

            boq_str = f"{ci.boq_item.code} - {ci.boq_item.description}" if (ci and ci.boq_item) else "-"
            unit_price_str = f"{ci.unit_price:,.2f}" if ci else "-"
            cost_delta_str = f"{ci.total_cost_delta:,.2f}" if ci else "-"

            writer.writerow([
                reg.id,
                run.id,
                status_str,
                bbox_str,
                reg.raw_text_v0 or "",
                reg.raw_text_v1 or "",
                elem_type,
                dim_v0_str,
                dim_v1_str,
                height_str,
                vol0_str,
                vol1_str,
                delta_vol_str,
                boq_str,
                unit_price_str,
                cost_delta_str,
            ])

    csv_data = output.getvalue()
    filename = f"change_intelligence_project_{project_id}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
