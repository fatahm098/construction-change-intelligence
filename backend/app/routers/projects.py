from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Project, Drawing, AnalysisRun, ChangeRegion, DimensionVerification, CostImpact, BOQItem, RegionStatus
from ..schemas import ProjectCreate, ProjectResponse, ProjectSummaryResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/summary", response_model=ProjectSummaryResponse)
def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    drawings_count = db.query(Drawing).filter(Drawing.project_id == project_id).count()
    analyses_count = db.query(AnalysisRun).filter(AnalysisRun.project_id == project_id).count()

    regions_query = (
        db.query(ChangeRegion)
        .join(AnalysisRun)
        .filter(AnalysisRun.project_id == project_id)
    )
    total_regions = regions_query.count()
    verified_regions = regions_query.filter(ChangeRegion.status == RegionStatus.VERIFIED).count()

    # Total cost impact delta dari seluruh region yang diverifikasi
    total_cost_delta = (
        db.query(func.coalesce(func.sum(CostImpact.total_cost_delta), 0.0))
        .join(ChangeRegion)
        .join(AnalysisRun)
        .filter(AnalysisRun.project_id == project_id, ChangeRegion.status == RegionStatus.VERIFIED)
        .scalar()
    )

    boq_count = db.query(BOQItem).filter(BOQItem.project_id == project_id).count()

    return ProjectSummaryResponse(
        project_id=project.id,
        project_name=project.name,
        total_drawings=drawings_count,
        total_analyses=analyses_count,
        total_changed_regions=total_regions,
        verified_regions=verified_regions,
        total_cost_delta=float(total_cost_delta),
        boq_items_count=boq_count,
    )
