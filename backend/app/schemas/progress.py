from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# Progress Entry Schemas
class ProgressEntryCreate(BaseModel):
    period: str
    planned_pct: float = 0
    actual_pct: float = 0
    actual_cost: float = 0
    note: Optional[str] = None


class ProgressEntryResponse(BaseModel):
    id: int
    project_id: int
    period: str
    planned_pct: float
    actual_pct: float
    actual_cost: float
    note: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Earned Value Management Schemas
class ProgressPointResponse(BaseModel):
    period: str
    planned_pct: float
    actual_pct: float
    planned_value: float
    earned_value: float
    actual_cost: float


class ProgressSummaryResponse(BaseModel):
    project_id: int
    project_name: str
    bac: float
    pv: float
    ev: float
    ac: float
    sv: float
    cv: float
    spi: float
    cpi: float
    eac: float
    etc: float
    vac: float
    progress_pct: float
    periods: List[ProgressPointResponse] = []
