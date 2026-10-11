from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from ..models.entities import RegionStatus, ElementType


# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Drawing Schemas
class DrawingResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    revision: int
    png_path: Optional[str] = None
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Dimension Verification Schemas
class DimensionVerificationCreate(BaseModel):
    element_type: ElementType = ElementType.COLUMN
    dim_before_w: float
    dim_before_h: float
    dim_after_w: float
    dim_after_h: float
    height_or_length_m: float = 4.0
    link_boq_item_id: Optional[int] = None


class DimensionVerificationResponse(BaseModel):
    id: int
    change_region_id: int
    element_type: ElementType
    dim_before_w: float
    dim_before_h: float
    dim_after_w: float
    dim_after_h: float
    height_or_length_m: float
    volume_before_m3: float
    volume_after_m3: float
    delta_volume_m3: float
    verified_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Cost Impact Schemas
class CostImpactResponse(BaseModel):
    id: int
    change_region_id: int
    boq_item_id: int
    delta_volume: float
    unit_price: float
    total_cost_delta: float
    calculated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Change Region Schemas
class ChangeRegionResponse(BaseModel):
    id: int
    analysis_run_id: int
    region_index: int
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int
    area: float
    crop_v0_path: Optional[str] = None
    crop_v1_path: Optional[str] = None
    raw_text_v0: Optional[str] = None
    raw_text_v1: Optional[str] = None
    suggested_dim_v0: Optional[str] = None
    suggested_dim_v1: Optional[str] = None
    status: RegionStatus
    verification: Optional[DimensionVerificationResponse] = None
    cost_impact: Optional[CostImpactResponse] = None
    model_config = ConfigDict(from_attributes=True)


# Analysis Run Schemas
class AnalysisRunResponse(BaseModel):
    id: int
    project_id: int
    drawing_ref_id: int
    drawing_rev_id: int
    diff_image_path: Optional[str] = None
    total_regions: int
    created_at: datetime
    regions: List[ChangeRegionResponse] = []
    model_config = ConfigDict(from_attributes=True)


# BOQ Schemas
class BOQItemBase(BaseModel):
    code: str
    description: str
    unit: str
    contract_volume: float = 0.0
    unit_price: float


class BOQItemCreate(BOQItemBase):
    pass


class BOQItemResponse(BOQItemBase):
    id: int
    project_id: int
    model_config = ConfigDict(from_attributes=True)


# Project Summary with Cost Delta
class ProjectSummaryResponse(BaseModel):
    project_id: int
    project_name: str
    total_drawings: int
    total_analyses: int
    total_changed_regions: int
    verified_regions: int
    total_cost_delta: float
    boq_items_count: int
