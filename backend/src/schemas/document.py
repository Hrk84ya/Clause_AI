from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    job_id: UUID
    status: str
    message: str


class DocumentSummary(BaseModel):
    id: UUID
    title: str
    doc_type: str | None = None
    status: str
    page_count: int | None = None
    word_count: int | None = None
    risk_score: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisBrief(BaseModel):
    risk_score: int | None = None
    clause_count: int = 0
    anomaly_count: int = 0


class DocumentDetail(BaseModel):
    id: UUID
    title: str
    original_filename: str
    doc_type: str | None = None
    status: str
    page_count: int | None = None
    word_count: int | None = None
    file_size_bytes: int | None = None
    mime_type: str | None = None
    parties: list = Field(default_factory=list)
    effective_date: str | None = None
    expiry_date: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    analysis: AnalysisBrief | None = None

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int
    pages: int


class DocumentStatusResponse(BaseModel):
    id: UUID
    status: str
    error_message: str | None = None

    model_config = {"from_attributes": True}
