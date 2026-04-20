import json
from datetime import datetime, timezone

import tiktoken
from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.analysis import Analysis, Clause
from src.models.chunk import Chunk
from src.models.document import Document
from src.rag.output_parsers import (
    AnomaliesResult,
    ExtractedClause,
    RiskScoringResult,
    SummaryResult,
    parse_llm_json,
    parse_llm_json_list,
)
from src.rag.prompts import (
    ANOMALY_DETECTION_PROMPT,
    CLAUSE_EXTRACTION_PROMPT,
    EXPECTED_CLAUSES,
    RISK_SCORING_PROMPT,
    SUMMARY_PROMPT,
)
from src.tasks.celery_app import celery_app

_encoder = tiktoken.get_encoding("cl100k_base")

# Separate engine for Celery tasks
_task_engine = None
_task_session_factory = None


def _get_task_session_factory():
    global _task_engine, _task_session_factory
    if _task_engine is None:
        _task_engine = create_async_engine(settings.database_url, echo=False)
        _task_session_factory = async_sessionmaker(
            _task_engine, class_=AsyncSession, expire_on_commit=False
        )
    return _task_session_factory


def _count_tokens(text: str) -> int:
    return len(_encoder.encode(text))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _call_gpt4o(prompt: str, max_tokens: int = 4000) -> str:
    """Call GPT-4o with retry logic."""
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _extract_clauses(full_text: str) -> list[ExtractedClause]:
    """Extract clauses, batching if text exceeds 8000 tokens."""
    token_count = _count_tokens(full_text)

    if token_count <= 8000:
        prompt = CLAUSE_EXTRACTION_PROMPT.format(text=full_text)
        result = _call_gpt4o(prompt)
        return parse_llm_json_list(result, ExtractedClause)

    # Batch processing for long documents
    all_clauses = []
    # Split into segments of ~6000 tokens with overlap
    words = full_text.split()
    segment_size = 4000  # words per segment (rough approximation)
    overlap = 500

    for i in range(0, len(words), segment_size - overlap):
        segment = " ".join(words[i:i + segment_size])
        prompt = CLAUSE_EXTRACTION_PROMPT.format(text=segment)
        try:
            result = _call_gpt4o(prompt)
            clauses = parse_llm_json_list(result, ExtractedClause)
            all_clauses.extend(clauses)
        except Exception:
            continue  # Skip failed segments

    # Deduplicate by clause_type + first 100 chars of verbatim_text
    seen = set()
    unique_clauses = []
    for clause in all_clauses:
        key = (clause.clause_type, clause.verbatim_text[:100])
        if key not in seen:
            seen.add(key)
            unique_clauses.append(clause)

    return unique_clauses


def _score_risks(clauses: list[ExtractedClause]) -> RiskScoringResult:
    """Score risks for extracted clauses."""
    clauses_json = json.dumps(
        [c.model_dump() for c in clauses], indent=2
    )
    prompt = RISK_SCORING_PROMPT.format(clauses_json=clauses_json)
    result = _call_gpt4o(prompt)
    return parse_llm_json(result, RiskScoringResult)


def _detect_anomalies(doc_type: str, clause_types: list[str], text_sample: str) -> AnomaliesResult:
    """Detect missing or unusual clauses."""
    expected = EXPECTED_CLAUSES.get(doc_type, EXPECTED_CLAUSES["other"])
    prompt = ANOMALY_DETECTION_PROMPT.format(
        doc_type=doc_type,
        clause_types_found=", ".join(clause_types),
        text_sample=text_sample[:3000],
        expected_clauses=", ".join(expected),
    )
    result = _call_gpt4o(prompt)
    return parse_llm_json(result, AnomaliesResult)


def _generate_summary(doc_type: str, parties: list[str], text: str) -> SummaryResult:
    """Generate document summary at three levels."""
    prompt = SUMMARY_PROMPT.format(
        doc_type=doc_type or "other",
        parties=", ".join(parties) if parties else "Unknown",
        text=text[:12000],  # Limit text for token budget
    )
    result = _call_gpt4o(prompt, max_tokens=6000)
    return parse_llm_json(result, SummaryResult)


@celery_app.task(
    bind=True,
    name="run_analysis",
    max_retries=3,
    default_retry_delay=60,
)
def run_analysis(self, document_id: str):
    """
    Run AI analysis on a processed document:
    1. Load full document text from chunks
    2. Extract clauses via GPT-4o
    3. Score risks via GPT-4o
    4. Detect anomalies via GPT-4o
    5. Generate summaries via GPT-4o
    6. Persist Analysis + Clauses to DB
    """
    import asyncio

    async def _analyze():
        SessionFactory = _get_task_session_factory()
        async with SessionFactory() as db:
            try:
                # 1. Load document and full text from chunks
                doc_result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = doc_result.scalar_one_or_none()
                if doc is None:
                    raise ValueError(f"Document {document_id} not found")

                # Get chunks ordered by index
                chunks_result = await db.execute(
                    select(Chunk)
                    .where(Chunk.document_id == document_id)
                    .order_by(Chunk.chunk_index)
                )
                chunks = chunks_result.scalars().all()
                full_text = "\n\n".join(c.content for c in chunks)

                if not full_text.strip():
                    raise ValueError("No text content found for document")

                # 2. Extract clauses
                extracted_clauses = _extract_clauses(full_text)

                # 3. Score risks
                risk_result = _score_risks(extracted_clauses)

                # 4. Detect anomalies
                clause_types = list(set(c.clause_type for c in extracted_clauses))
                anomaly_result = _detect_anomalies(
                    doc.doc_type or "other",
                    clause_types,
                    full_text,
                )

                # 5. Generate summary
                summary_result = _generate_summary(
                    doc.doc_type or "other",
                    doc.parties or [],
                    full_text,
                )

                # 6. Persist to DB
                # Check if analysis already exists
                existing = await db.execute(
                    select(Analysis).where(Analysis.document_id == document_id)
                )
                analysis = existing.scalar_one_or_none()

                if analysis is None:
                    analysis = Analysis(
                        document_id=doc.id,
                        risk_score=risk_result.risk_score,
                        summary_brief=summary_result.brief,
                        summary_standard=summary_result.standard,
                        summary_detailed=summary_result.detailed,
                        anomalies=[a.model_dump() for a in anomaly_result.anomalies],
                    )
                    db.add(analysis)
                else:
                    analysis.risk_score = risk_result.risk_score
                    analysis.summary_brief = summary_result.brief
                    analysis.summary_standard = summary_result.standard
                    analysis.summary_detailed = summary_result.detailed
                    analysis.anomalies = [a.model_dump() for a in anomaly_result.anomalies]
                    analysis.updated_at = datetime.now(timezone.utc)

                await db.flush()

                # Create clause records
                # Build a map of risk levels from scoring result
                risk_map = {}
                for sc in risk_result.scored_clauses:
                    risk_map[sc.clause_type] = (sc.risk_level, sc.risk_reason)

                for ec in extracted_clauses:
                    risk_level, risk_reason = risk_map.get(
                        ec.clause_type, ("info", None)
                    )
                    clause = Clause(
                        analysis_id=analysis.id,
                        clause_type=ec.clause_type,
                        verbatim_text=ec.verbatim_text,
                        section_reference=ec.section_reference,
                        plain_english=ec.plain_english,
                        risk_level=risk_level,
                        risk_reason=risk_reason,
                    )
                    db.add(clause)

                await db.commit()

            except Exception as exc:
                await db.rollback()
                raise exc

    try:
        asyncio.run(_analyze())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
