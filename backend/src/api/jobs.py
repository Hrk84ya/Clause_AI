from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.document import Document
from src.models.job import Job
from src.models.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}")
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get job status by ID."""
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify the job's document belongs to the current user
    if job.document_id:
        doc_result = await db.execute(
            select(Document).where(
                Document.id == job.document_id,
                Document.user_id == current_user.id,
            )
        )
        if doc_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": str(job.id),
        "job_type": job.job_type,
        "status": job.status,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
