from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.analysis import Analysis, Clause
from src.models.document import Document
from src.models.user import User
from src.rag.chains import compare_documents
from src.schemas.analysis import (
    AnalysisResponse,
    AnomalyResponse,
    ClauseResponse,
    CompareRequest,
    CompareResponse,
    SummaryResponse,
)

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.get("/{document_id}", response_model=AnalysisResponse)
async def get_analysis(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """Get full analysis for a document."""
    # Verify document belongs to user
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None),
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get analysis
    result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get clauses
    clauses_result = await db.execute(
        select(Clause).where(Clause.analysis_id == analysis.id)
    )
    clauses = clauses_result.scalars().all()

    return AnalysisResponse(
        id=analysis.id,
        document_id=analysis.document_id,
        risk_score=analysis.risk_score,
        summary_standard=analysis.summary_standard,
        clauses=[ClauseResponse.model_validate(c) for c in clauses],
        anomalies=[AnomalyResponse(**a) for a in (analysis.anomalies or [])],
    )


@router.get("/{document_id}/clauses", response_model=list[ClauseResponse])
async def get_clauses(
    document_id: UUID,
    clause_type: str | None = Query(None),
    risk_level: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClauseResponse]:
    """Get clauses for a document, optionally filtered."""
    # Verify document belongs to user
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get analysis
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = analysis_result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Build clause query
    query = select(Clause).where(Clause.analysis_id == analysis.id)
    if clause_type:
        query = query.where(Clause.clause_type == clause_type)
    if risk_level:
        # Support comma-separated risk levels
        levels = [l.strip() for l in risk_level.split(",")]
        query = query.where(Clause.risk_level.in_(levels))

    result = await db.execute(query)
    clauses = result.scalars().all()

    return [ClauseResponse.model_validate(c) for c in clauses]


@router.get("/{document_id}/summary", response_model=SummaryResponse)
async def get_summary(
    document_id: UUID,
    level: str = Query("standard", pattern="^(brief|standard|detailed)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SummaryResponse:
    """Get document summary at specified level."""
    # Verify document belongs to user
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get analysis
    result = await db.execute(
        select(Analysis).where(Analysis.document_id == document_id)
    )
    analysis = result.scalar_one_or_none()
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get the requested summary level
    content_map = {
        "brief": analysis.summary_brief,
        "standard": analysis.summary_standard,
        "detailed": analysis.summary_detailed,
    }
    content = content_map.get(level, analysis.summary_standard) or ""

    return SummaryResponse(level=level, content=content)


@router.post("/{document_id}/compare", response_model=CompareResponse)
async def compare(
    document_id: UUID,
    body: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CompareResponse:
    """Compare two documents."""
    # Verify both documents belong to user
    for did in [document_id, body.compare_with_document_id]:
        result = await db.execute(
            select(Document).where(
                Document.id == did,
                Document.user_id == current_user.id,
                Document.deleted_at.is_(None),
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail=f"Document {did} not found")

    comparison = await compare_documents(
        str(document_id),
        str(body.compare_with_document_id),
        db,
    )

    return CompareResponse(**comparison)
