from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from ..models.entities import DocumentType, DocumentStatus


class DocumentResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    doc_type: DocumentType
    status: DocumentStatus
    num_chunks: int
    error_message: Optional[str] = None
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


class ChatSource(BaseModel):
    filename: str
    page: Optional[int] = None
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = []
