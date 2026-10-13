"""Router modul Jobs: antrean & status pekerjaan latar belakang (Fase 4).

Endpoint:
  - POST /api/jobs/analysis — masukkan analisis gambar ke antrean
  - GET  /api/jobs/{job_id} — status/ hasil sebuah job

Perilaku:
  - `jobs_enabled=true`  → job di-enqueue ke worker ARQ (butuh Redis).
  - `jobs_enabled=false` → job dieksekusi sinkron di request (tanpa Redis), agar
    pengembangan lokal & test e2e tetap jalan.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...kernel.config import settings
from ...models import Drawing, Job, JobStatus, Project
from ...schemas import AnalysisJobRequest, JobEnqueueResponse, JobResponse
from ...services.analysis_service import run_analysis

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])
# Diekspor dalam bentuk list agar cocok dengan registry modul (`routers`).
routers = [router]

ANALYSIS_JOB_TYPE = "analysis_run"


def _run_sync(db: Session, job: Job, payload: AnalysisJobRequest) -> None:
    """Jalankan analisis langsung (fallback tanpa Redis) dan catat hasilnya ke Job."""
    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()
    try:
        run = run_analysis(
            db,
            project_id=payload.project_id,
            drawing_ref_id=payload.drawing_ref_id,
            drawing_rev_id=payload.drawing_rev_id,
            min_area=payload.min_area,
        )
    except HTTPException as exc:
        job.status = JobStatus.FAILED
        job.error_message = str(exc.detail)
        job.finished_at = datetime.utcnow()
        db.commit()
        raise

    job.status = JobStatus.SUCCESS
    job.result_json = json.dumps({"analysis_run_id": run.id, "total_regions": run.total_regions})
    job.finished_at = datetime.utcnow()
    db.commit()


@router.post("/analysis", response_model=JobEnqueueResponse)
async def enqueue_analysis(payload: AnalysisJobRequest, db: Session = Depends(get_db)):
    """Masukkan analisis gambar ke antrean (atau jalankan sinkron bila jobs nonaktif)."""
    if db.get(Project, payload.project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")

    dwg_ref = (
        db.query(Drawing)
        .filter(Drawing.id == payload.drawing_ref_id, Drawing.project_id == payload.project_id)
        .first()
    )
    dwg_rev = (
        db.query(Drawing)
        .filter(Drawing.id == payload.drawing_rev_id, Drawing.project_id == payload.project_id)
        .first()
    )
    if not dwg_ref or not dwg_rev:
        raise HTTPException(status_code=400, detail="Salah satu atau kedua drawing tidak ditemukan di project ini")

    job = Job(
        project_id=payload.project_id,
        job_type=ANALYSIS_JOB_TYPE,
        status=JobStatus.PENDING,
        payload_json=payload.model_dump_json(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if settings.jobs_enabled:
        # Impor lazily: proses web tidak perlu Redis saat jobs dimatikan.
        from ...kernel.jobs.queue import enqueue_job

        await enqueue_job("run_analysis_job", job.id)
        return JobEnqueueResponse(job_id=job.id, status=JobStatus.PENDING)

    # Fallback sinkron — tidak butuh Redis/worker.
    # Jalankan di thread agar analisis berat tidak memblokir event loop.
    await asyncio.to_thread(_run_sync, db, job, payload)
    db.refresh(job)
    return JobEnqueueResponse(
        job_id=job.id,
        status=job.status,
        message="Analisis dijalankan sinkron (jobs nonaktif).",
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Kembalikan status/ hasil sebuah job berdasarkan id."""
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
