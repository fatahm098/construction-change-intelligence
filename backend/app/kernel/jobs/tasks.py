"""Tugas background ARQ (Fase 4).

Setiap tugas membuka sesi DB sendiri (tanpa request context) dan memperbarui
baris `Job` (status, result_json, error_message, timestamp).
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from ..db import SessionLocal
from ...models import Job, JobStatus
from ...services.analysis_service import run_analysis


def _execute_analysis(job_id: int) -> dict:
    """Jalankan analisis untuk sebuah Job secara sinkron (dipanggil di thread)."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} tidak ditemukan")

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()

        payload = json.loads(job.payload_json or "{}")
        run = run_analysis(
            db,
            project_id=payload["project_id"],
            drawing_ref_id=payload["drawing_ref_id"],
            drawing_rev_id=payload["drawing_rev_id"],
            min_area=payload.get("min_area", 350),
        )
        result = {"analysis_run_id": run.id, "total_regions": run.total_regions}

        job.status = JobStatus.SUCCESS
        job.result_json = json.dumps(result)
        job.finished_at = datetime.utcnow()
        db.commit()
        return result
    except Exception as exc:  # noqa: BLE001 — catat kegagalan ke baris Job lalu teruskan
        db.rollback()
        job = db.get(Job, job_id)
        if job is not None:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.finished_at = datetime.utcnow()
            db.commit()
        raise
    finally:
        db.close()


async def run_analysis_job(ctx, job_id: int) -> dict:
    """Entrypoint worker: jalankan analisis di thread agar loop ARQ tetap responsif."""
    return await asyncio.to_thread(_execute_analysis, job_id)
