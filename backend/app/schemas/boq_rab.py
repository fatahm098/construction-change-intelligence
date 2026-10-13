from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from ..models.entities import AHSPComponentType


class AHSPComponentResponse(BaseModel):
    id: int
    component_type: AHSPComponentType
    name: str
    coefficient: float
    unit: str
    base_price: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class AHSPItemResponse(BaseModel):
    id: int
    code: str
    name: str
    unit: str
    category: Optional[str] = None
    unit_price: float
    components: List[AHSPComponentResponse] = []
    model_config = ConfigDict(from_attributes=True)


class RABLineResponse(BaseModel):
    boq_item_id: int
    code: str
    description: str
    unit: str
    contract_volume: float
    delta_volume: float
    adjusted_volume: float
    unit_price: float
    contract_amount: float
    adjusted_amount: float
    delta_amount: float
    ahsp_item_id: Optional[int] = None
    ahsp_code: Optional[str] = None


class RABResponse(BaseModel):
    project_id: int
    project_name: str
    lines: List[RABLineResponse] = []
    total_contract: float
    total_adjusted: float
    total_delta: float
    item_count: int
    verified_region_count: int


class BOQSuggestionResponse(BaseModel):
    region_id: int
    element_type: str
    suggested_boq_item_id: Optional[int] = None
    suggested_code: Optional[str] = None
    suggested_description: Optional[str] = None
    unit_price: Optional[float] = None
    reason: str
