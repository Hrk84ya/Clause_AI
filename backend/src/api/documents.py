import math
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.file_storage import (
    delete_document_files,
    get_file_path,
    save_upload,
    validate_file,
)
from src.database import get_db
from src.dependencies import get_current_user
from src.models.analysis import Analysis, Clause
from src.models.document import Document
from src.models.job import Job
from src.models.user import User
from src.schemas.document import (
    AnalysisBrief,
    DocumentDetail,
    DocumentListResponse,
    DocumentStatusResponse,
    DocumentSummary,
    DocumentUploadResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a document for analysis."""
    # Validate file
    mime_type = await validate_file(file)

    # Create document record
    title = file.filename or "Untitled"
    doc = Document(
        user_id=current_user.id,
        title=title.rsplit(".", 1)[0] if "." in title else title,
        original_filename=title,
        file_path="",  # Will be updated after save
        mime_type=mime_type,
        status="pending",
    )
    db.add(doc)
    await db.flush()

    # Save file to disk
    file_path, file_size = await save_upload(
        str(current_user.id), str(doc.id), file
    )
    doc.file_path = file_path
    doc.file_size_bytes = file_size

    # Create job record
    job = Job(
        document_id=doc.id,
        job_type="process_document",
        status="pending",
    )
    db.add(job)
    await db.flush()

    # TODO: Enqueue Celery task in T-017
    # process_document.delay(str(doc.id))

    return DocumentUploadResponse(
        document_id=doc.id,
        job_id=job.id,
        status="pending",
        message="Document uploaded successfully. Processing started.",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    doc_type: str | None = Query(None),
    risk_level: str | None = Query(None),
    q: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """List documents for the current user with pagination and filters."""
    # Base query — user-scoped, exclude soft-deleted
    query = select(Document).where(
        Document.user_id == current_user.id,
        Document.deleted_at.is_(None),
    )

    # Apply filters
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    if q:
        query = query.where(Document.title.ilike(f"%{q}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Document.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    documents = result.scalars().all()

    # Build response with risk_score from analysis
    items = []
    for doc in documents:
        # Get risk score from analysis if exists
        analysis_result = await db.execute(
            select(Analysis.risk_score).where(Analysis.document_id == doc.id)
        )
        risk_score = analysis_result.scalar_one_or_none()

        items.append(
            DocumentSummary(
                id=doc.id,
                title=doc.title,
                doc_type=doc.doc_type,
                status=doc.status,
                page_count=doc.page_count,
                word_count=doc.word_count,
                risk_score=risk_score,
                created_at=doc.created_at,
            )
        )

    return DocumentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    """Get document detail by ID."""
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

    # Get analysis info
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.document_id == doc.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    analysis_brief = None
    if analysis:
        clause_count_result = await db.execute(
            select(func.count()).where(Clause.analysis_id == analysis.id)
        )
        clause_count = clause_count_result.scalar() or 0
        anomaly_count = len(analysis.anomalies) if analysis.anomalies else 0

        analysis_brief = AnalysisBrief(
            risk_score=analysis.risk_score,
            clause_count=clause_count,
            anomaly_count=anomaly_count,
        )

    return DocumentDetail(
        id=doc.id,
        title=doc.title,
        original_filename=doc.original_filename,
        doc_type=doc.doc_type,
        status=doc.status,
        page_count=doc.page_count,
        word_count=doc.word_count,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        parties=doc.parties or [],
        effective_date=str(doc.effective_date) if doc.effective_date else None,
        expiry_date=str(doc.expiry_date) if doc.expiry_date else None,
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        analysis=analysis_brief,
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentStatusResponse:
    """Get document processing status."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentStatusResponse.model_validate(doc)


@router.get("/{document_id}/file")
async def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the original document file."""
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

    file_path = get_file_path(str(current_user.id), str(doc.id))
    return FileResponse(
        path=str(file_path),
        filename=doc.original_filename,
        media_type=doc.mime_type,
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a document."""
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

    # Soft delete
    doc.deleted_at = datetime.now(timezone.utc)
    await db.flush()

    return {"message": "Document deleted successfully"}
