from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from ..models.entities import JobStatus


class JobResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    job_type: str
    status: JobStatus
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class JobEnqueueResponse(BaseModel):
    job_id: int
    status: JobStatus
    message: str = "Pekerjaan dimasukkan ke antrean."


class AnalysisJobRequest(BaseModel):
    """Payload untuk memasukkan analisis gambar ke antrean (POST /api/jobs/analysis)."""

    project_id: int
    drawing_ref_id: int
    drawing_rev_id: int
    min_area: int = 350
