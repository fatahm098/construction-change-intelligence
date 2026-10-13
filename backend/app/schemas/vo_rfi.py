from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from ..models import RFIStatus, VOStatus


# Variation Order Schemas
class VariationOrderCreate(BaseModel):
    vo_number: str
    title: str
    description: Optional[str] = None
    amount: float = 0
    change_region_id: Optional[int] = None


class VariationOrderResponse(BaseModel):
    id: int
    project_id: int
    vo_number: str
    title: str
    description: Optional[str] = None
    status: VOStatus
    amount: float
    change_region_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VOStatusUpdate(BaseModel):
    status: VOStatus


# RFI Schemas
class RFICreate(BaseModel):
    rfi_number: str
    subject: str
    question: str
    variation_order_id: Optional[int] = None


class RFIResponse(BaseModel):
    id: int
    project_id: int
    rfi_number: str
    subject: str
    question: str
    answer: Optional[str] = None
    status: RFIStatus
    variation_order_id: Optional[int] = None
    created_at: datetime
    answered_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class RFIAnswerRequest(BaseModel):
    answer: str
