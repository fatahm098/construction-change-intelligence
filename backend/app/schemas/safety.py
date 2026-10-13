from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict
from ..models import SafetyCategory, SafetyStatus, Severity


# Safety Report Schemas
class SafetyReportCreate(BaseModel):
    report_number: str
    title: str
    category: SafetyCategory = SafetyCategory.INCIDENT
    severity: Severity = Severity.LOW
    description: str
    action_taken: Optional[str] = None
    reported_by: Optional[str] = None
    occurred_at: Optional[datetime] = None


class SafetyReportResponse(BaseModel):
    id: int
    project_id: int
    report_number: str
    title: str
    category: SafetyCategory
    severity: Severity
    description: str
    action_taken: Optional[str] = None
    status: SafetyStatus
    reported_by: Optional[str] = None
    occurred_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SafetyStatusUpdate(BaseModel):
    status: SafetyStatus


class SafetySummaryResponse(BaseModel):
    project_id: int
    total: int
    open: int
    investigating: int
    closed: int
    by_severity: Dict[str, int]
