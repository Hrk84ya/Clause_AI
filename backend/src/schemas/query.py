from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    chunk_id: str
    section_title: str | None = None
    excerpt: str


class QueryResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    source_chunks: list[SourceChunk]
    confidence: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryHistoryResponse(BaseModel):
    items: list[QueryResponse]
