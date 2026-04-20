import re
from datetime import datetime, timezone

import spacy
from dateutil import parser as date_parser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings
from src.core.chunker import chunk_document
from src.core.embedder import build_faiss_index, embed_chunks
from src.core.parser import extract_text
from src.models.chunk import Chunk
from src.models.document import Document
from src.models.job import Job
from src.rag.output_parsers import DocTypeResult, parse_llm_json
from src.rag.prompts import DOC_TYPE_PROMPT
from src.tasks.celery_app import celery_app

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

# Create a separate async engine for Celery tasks
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


def _extract_parties(text: str) -> list[str]:
    """Extract party names using spaCy NER."""
    if nlp is None:
        return []
    # Only process first 10000 chars for performance
    doc = nlp(text[:10000])
    parties = set()
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG"):
            name = ent.text.strip()
            if len(name) > 2:  # Filter out very short names
                parties.add(name)
    return list(parties)[:20]  # Limit to 20 parties


def _extract_dates(text: str) -> tuple[str | None, str | None]:
    """Extract effective and expiry dates from text using regex + dateutil."""
    effective_date = None
    expiry_date = None

    # Common date patterns
    date_patterns = [
        r"effective\s+(?:date|as\s+of)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"dated?\s+(?:as\s+of\s+)?([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"commence[sd]?\s+(?:on\s+)?([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ]

    expiry_patterns = [
        r"expir(?:es?|ation)\s+(?:date)?[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"terminat(?:es?|ion)\s+(?:date)?[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"end\s+date[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ]

    # Search first 5000 chars
    search_text = text[:5000].lower()
    original_text = text[:5000]

    for pattern in date_patterns:
        match = re.search(pattern, original_text, re.IGNORECASE)
        if match:
            try:
                parsed = date_parser.parse(match.group(1), fuzzy=True)
                effective_date = parsed.strftime("%Y-%m-%d")
                break
            except (ValueError, OverflowError):
                continue

    for pattern in expiry_patterns:
        match = re.search(pattern, original_text, re.IGNORECASE)
        if match:
            try:
                parsed = date_parser.parse(match.group(1), fuzzy=True)
                expiry_date = parsed.strftime("%Y-%m-%d")
                break
            except (ValueError, OverflowError):
                continue

    return effective_date, expiry_date


def _classify_doc_type(text: str) -> str:
    """Classify document type using GPT-4o."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = DOC_TYPE_PROMPT.format(text=text[:2000])

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        result_text = response.choices[0].message.content
        result = parse_llm_json(result_text, DocTypeResult)
        return result.doc_type
    except Exception:
        return "other"


@celery_app.task(
    bind=True,
    name="process_document",
    max_retries=3,
    default_retry_delay=60,
)
def process_document(self, document_id: str):
    """
    Full document processing pipeline:
    1. Set status = 'processing'
    2. Extract text
    3. Chunk document
    4. Persist chunks to DB
    5. Generate embeddings
    6. Update chunk embeddings in DB
    7. Build FAISS index
    8. Classify doc type
    9. Extract parties via spaCy
    10. Extract dates
    11. Update document record
    12. Enqueue run_analysis task
    13. Set status = 'completed'
    """
    import asyncio

    async def _process():
        SessionFactory = _get_task_session_factory()
        async with SessionFactory() as db:
            try:
                # 1. Get document and set status
                result = await db.execute(
                    select(Document).where(Document.id == document_id)
                )
                doc = result.scalar_one_or_none()
                if doc is None:
                    raise ValueError(f"Document {document_id} not found")

                doc.status = "processing"
                await db.commit()

                # Update job status
                job_result = await db.execute(
                    select(Job).where(
                        Job.document_id == document_id,
                        Job.job_type == "process_document",
                    )
                )
                job = job_result.scalar_one_or_none()
                if job:
                    job.status = "running"
                    job.started_at = datetime.now(timezone.utc)
                    await db.commit()

                # 2. Extract text
                full_text, page_count, word_count = extract_text(
                    doc.file_path, doc.mime_type
                )
                doc.page_count = page_count
                doc.word_count = word_count

                # 3. Chunk document
                chunks = chunk_document(full_text, str(doc.id))

                # 4. Persist chunks to DB
                chunk_records = []
                for chunk_data in chunks:
                    chunk_record = Chunk(
                        document_id=doc.id,
                        chunk_index=chunk_data["chunk_index"],
                        content=chunk_data["content"],
                        section_title=chunk_data["section_title"],
                        token_count=chunk_data["token_count"],
                    )
                    db.add(chunk_record)
                    chunk_records.append(chunk_record)
                await db.flush()

                # 5. Generate embeddings
                embeddings = embed_chunks(chunks)

                # 6. Update chunk embeddings in DB
                for i, chunk_record in enumerate(chunk_records):
                    chunk_record.embedding = embeddings[i]
                await db.flush()

                # 7. Build FAISS index
                build_faiss_index(embeddings, str(doc.id))

                # 8. Classify doc type
                doc.doc_type = _classify_doc_type(full_text)

                # 9. Extract parties
                doc.parties = _extract_parties(full_text)

                # 10. Extract dates
                effective_date, expiry_date = _extract_dates(full_text)
                if effective_date:
                    doc.effective_date = effective_date
                if expiry_date:
                    doc.expiry_date = expiry_date

                # 11. Update document
                doc.updated_at = datetime.now(timezone.utc)

                # 12. Enqueue run_analysis task
                from src.tasks.run_analysis import run_analysis
                run_analysis.delay(document_id)

                # 13. Set status = 'completed'
                doc.status = "completed"
                if job:
                    job.status = "completed"
                    job.completed_at = datetime.now(timezone.utc)

                await db.commit()

            except Exception as exc:
                await db.rollback()

                # Update document status to failed
                try:
                    result = await db.execute(
                        select(Document).where(Document.id == document_id)
                    )
                    doc = result.scalar_one_or_none()
                    if doc:
                        doc.status = "failed"
                        doc.error_message = str(exc)[:500]
                        await db.commit()
                except Exception:
                    pass

                raise exc

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(asyncio.run, _process()).result()
        else:
            asyncio.run(_process())
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))