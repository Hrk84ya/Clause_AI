from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ClauseResponse(BaseModel):
    id: UUID
    clause_type: str
    verbatim_text: str
    section_reference: str | None = None
    page_number: int | None = None
    plain_english: str | None = None
    risk_level: str | None = None
    risk_reason: str | None = None

    model_config = {"from_attributes": True}


class AnomalyResponse(BaseModel):
    anomaly_type: str
    description: str
    severity: str


class AnalysisResponse(BaseModel):
    id: UUID
    document_id: UUID
    risk_score: int | None = None
    summary_standard: str | None = None
    clauses: list[ClauseResponse]
    anomalies: list[AnomalyResponse]


class SummaryResponse(BaseModel):
    level: str
    content: str


class CompareRequest(BaseModel):
    compare_with_document_id: UUID


class CompareResponse(BaseModel):
    document_a: dict
    document_b: dict
    differences: list[dict]
    clauses_only_in_a: list[str]
    clauses_only_in_b: list[str]
    summary: str
