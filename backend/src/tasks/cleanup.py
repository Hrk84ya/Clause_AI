from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings
from src.core.file_storage import delete_document_files
from src.models.document import Document
from src.tasks.celery_app import celery_app


@celery_app.task(name="cleanup_deleted_files")
def cleanup_deleted_files():
    """Find documents with deleted_at older than 1 day and delete their files."""
    import asyncio

    async def _cleanup():
        engine = create_async_engine(settings.database_url, echo=False)
        SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with SessionFactory() as db:
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)
            result = await db.execute(
                select(Document).where(
                    Document.deleted_at.isnot(None),
                    Document.deleted_at < cutoff,
                )
            )
            documents = result.scalars().all()

            for doc in documents:
                try:
                    delete_document_files(str(doc.user_id), str(doc.id))
                except Exception:
                    pass  # Log but don't fail

                await db.delete(doc)

            await db.commit()

        await engine.dispose()

    asyncio.run(_cleanup())
