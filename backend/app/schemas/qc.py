from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from ..models import CheckResult, InspectionCategory, InspectionStatus


# Inspection Item Schemas
class InspectionItemCreate(BaseModel):
    description: str
    standard: Optional[str] = None
    result: CheckResult = CheckResult.OK
    note: Optional[str] = None


class InspectionItemResponse(BaseModel):
    id: int
    inspection_id: int
    description: str
    standard: Optional[str] = None
    result: CheckResult
    note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class InspectionItemUpdate(BaseModel):
    result: Optional[CheckResult] = None
    note: Optional[str] = None


# Inspection Schemas
class InspectionCreate(BaseModel):
    inspection_number: str
    title: str
    location: Optional[str] = None
    category: InspectionCategory = InspectionCategory.OTHER
    inspector: Optional[str] = None
    inspected_at: Optional[datetime] = None
    note: Optional[str] = None
    items: List[InspectionItemCreate] = []


class InspectionResponse(BaseModel):
    id: int
    project_id: int
    inspection_number: str
    title: str
    location: Optional[str] = None
    category: InspectionCategory
    status: InspectionStatus
    inspector: Optional[str] = None
    inspected_at: Optional[datetime] = None
    note: Optional[str] = None
    created_at: datetime
    items: List[InspectionItemResponse] = []
    model_config = ConfigDict(from_attributes=True)


class QCSummaryResponse(BaseModel):
    project_id: int
    total: int
    passed: int
    failed: int
    draft: int
    pass_rate: float
    total_items: int
    not_ok_items: int
