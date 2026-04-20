from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.document import Document
from src.models.query import Query
from src.models.user import User
from src.rag.chains import answer_question
from src.schemas.query import (
    QueryHistoryResponse,
    QueryRequest,
    QueryResponse,
    SourceChunk,
)

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post("/{document_id}", response_model=QueryResponse)
async def ask_question(
    document_id: UUID,
    body: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Ask a question about a document using RAG."""
    # Verify document exists and belongs to user
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None),
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Document processing is not complete",
        )

    # Get answer via RAG
    answer_result = await answer_question(str(document_id), body.question, db)

    # Persist query
    query = Query(
        document_id=document_id,
        user_id=current_user.id,
        question=body.question,
        answer=answer_result["answer"],
        source_chunks=answer_result["source_chunks"],
        confidence=answer_result["confidence"],
    )
    db.add(query)
    await db.flush()

    return QueryResponse(
        id=query.id,
        question=query.question,
        answer=query.answer,
        source_chunks=[SourceChunk(**sc) for sc in answer_result["source_chunks"]],
        confidence=query.confidence,
        created_at=query.created_at,
    )


@router.get("/{document_id}/history", response_model=QueryHistoryResponse)
async def get_query_history(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QueryHistoryResponse:
    """Get query history for a document (last 50)."""
    # Verify document belongs to user
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Document not found")

    result = await db.execute(
        select(Query)
        .where(
            Query.document_id == document_id,
            Query.user_id == current_user.id,
        )
        .order_by(Query.created_at.desc())
        .limit(50)
    )
    queries = result.scalars().all()

    items = []
    for q in queries:
        items.append(
            QueryResponse(
                id=q.id,
                question=q.question,
                answer=q.answer or "",
                source_chunks=[SourceChunk(**sc) for sc in (q.source_chunks or [])],
                confidence=q.confidence or "low",
                created_at=q.created_at,
            )
        )

    return QueryHistoryResponse(items=items)
