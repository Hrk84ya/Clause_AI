from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.embedder import embed_chunks, search_faiss
from src.models.chunk import Chunk


async def get_relevant_chunks(
    doc_id: str, question: str, db: AsyncSession, k: int = 5
) -> list[Chunk]:
    """
    Get the most relevant chunks for a question using FAISS.
    1. Embed the question
    2. Search FAISS index
    3. Return top-k Chunk DB objects
    """
    # Embed the question (reuse embed_chunks with a single-item list)
    question_embedding = embed_chunks([{"content": question}])[0]

    # Search FAISS index
    chunk_indices = search_faiss(doc_id, question_embedding, k=k)

    if not chunk_indices:
        return []

    # Fetch chunks from DB by document_id and chunk_index
    result = await db.execute(
        select(Chunk)
        .where(
            Chunk.document_id == doc_id,
            Chunk.chunk_index.in_(chunk_indices),
        )
        .order_by(Chunk.chunk_index)
    )
    return list(result.scalars().all())
