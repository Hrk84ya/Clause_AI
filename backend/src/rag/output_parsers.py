import json
import re
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class DocTypeResult(BaseModel):
    doc_type: str
    confidence: str
    reasoning: str


class ExtractedClause(BaseModel):
    clause_type: str
    verbatim_text: str
    section_reference: str | None = None
    plain_english: str | None = None


class ScoredClause(BaseModel):
    clause_type: str
    risk_level: str
    risk_reason: str


class RiskScoringResult(BaseModel):
    risk_score: int
    scored_clauses: list[ScoredClause]
    overall_risk_summary: str


class AnomalyResult(BaseModel):
    anomaly_type: str
    description: str
    severity: str


class AnomaliesResult(BaseModel):
    anomalies: list[AnomalyResult]


class SummaryResult(BaseModel):
    brief: str
    standard: str
    detailed: str


def parse_llm_json(raw: str, model: Type[T]) -> T:
    """
    Parse LLM JSON output into a Pydantic model.
    Strips markdown code fences if present.
    Raises ValueError on invalid JSON, ValidationError on schema mismatch.
    """
    # Strip markdown code fences
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")

    return model.model_validate(data)


def parse_llm_json_list(raw: str, model: Type[T]) -> list[T]:
    """
    Parse LLM JSON array output into a list of Pydantic models.
    Strips markdown code fences if present.
    """
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from LLM: {e}")

    if not isinstance(data, list):
        raise ValueError("Expected JSON array from LLM")

    return [model.model_validate(item) for item in data]
