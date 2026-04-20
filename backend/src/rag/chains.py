import json

from openai import OpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.models.analysis import Analysis, Clause
from src.models.document import Document
from src.rag.prompts import RAG_SYSTEM_PROMPT
from src.rag.vector_store import get_relevant_chunks


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _call_gpt4o(system_prompt: str, user_message: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=2000,
    )
    return response.choices[0].message.content


async def answer_question(
    document_id: str, question: str, db: AsyncSession
) -> dict:
    """
    Answer a question about a document using RAG.
    Returns {answer, source_chunks, confidence}.
    """
    # Get relevant chunks
    chunks = await get_relevant_chunks(document_id, question, db, k=5)

    if not chunks:
        return {
            "answer": "I couldn't find relevant information in the document to answer this question.",
            "source_chunks": [],
            "confidence": "low",
        }

    # Build context from chunks
    context_parts = []
    source_chunks = []
    for chunk in chunks:
        context_parts.append(
            f"[Section: {chunk.section_title or 'Unknown'}]\n{chunk.content}"
        )
        source_chunks.append({
            "chunk_id": str(chunk.id),
            "section_title": chunk.section_title,
            "excerpt": chunk.content[:300],
        })

    context = "\n\n---\n\n".join(context_parts)
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    # Call GPT-4o
    answer = _call_gpt4o(system_prompt, question)

    # Determine confidence based on number of relevant chunks
    if len(chunks) >= 3:
        confidence = "high"
    elif len(chunks) >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "answer": answer,
        "source_chunks": source_chunks,
        "confidence": confidence,
    }


async def compare_documents(
    doc_id_a: str, doc_id_b: str, db: AsyncSession
) -> dict:
    """Compare two documents by their analyses."""
    # Load both documents and analyses
    doc_a_result = await db.execute(
        select(Document).where(Document.id == doc_id_a)
    )
    doc_a = doc_a_result.scalar_one_or_none()

    doc_b_result = await db.execute(
        select(Document).where(Document.id == doc_id_b)
    )
    doc_b = doc_b_result.scalar_one_or_none()

    if not doc_a or not doc_b:
        raise ValueError("One or both documents not found")

    # Load analyses
    analysis_a_result = await db.execute(
        select(Analysis).where(Analysis.document_id == doc_id_a)
    )
    analysis_a = analysis_a_result.scalar_one_or_none()

    analysis_b_result = await db.execute(
        select(Analysis).where(Analysis.document_id == doc_id_b)
    )
    analysis_b = analysis_b_result.scalar_one_or_none()

    # Load clauses
    clauses_a = []
    clauses_b = []
    if analysis_a:
        ca_result = await db.execute(
            select(Clause).where(Clause.analysis_id == analysis_a.id)
        )
        clauses_a = list(ca_result.scalars().all())

    if analysis_b:
        cb_result = await db.execute(
            select(Clause).where(Clause.analysis_id == analysis_b.id)
        )
        clauses_b = list(cb_result.scalars().all())

    # Build comparison
    types_a = set(c.clause_type for c in clauses_a)
    types_b = set(c.clause_type for c in clauses_b)

    only_in_a = list(types_a - types_b)
    only_in_b = list(types_b - types_a)

    # Build differences
    differences = []
    common_types = types_a & types_b
    for ct in common_types:
        clause_a = next((c for c in clauses_a if c.clause_type == ct), None)
        clause_b = next((c for c in clauses_b if c.clause_type == ct), None)
        if clause_a and clause_b and clause_a.risk_level != clause_b.risk_level:
            differences.append({
                "field": ct,
                "document_a_value": f"{clause_a.risk_level}: {clause_a.plain_english or clause_a.verbatim_text[:100]}",
                "document_b_value": f"{clause_b.risk_level}: {clause_b.plain_english or clause_b.verbatim_text[:100]}",
                "significance": "high" if clause_a.risk_level in ("critical", "high") or clause_b.risk_level in ("critical", "high") else "medium",
            })

    # Generate comparison summary via GPT-4o
    comparison_prompt = f"""Compare these two legal documents:

Document A: {doc_a.title} (type: {doc_a.doc_type}, risk score: {analysis_a.risk_score if analysis_a else 'N/A'})
Document B: {doc_b.title} (type: {doc_b.doc_type}, risk score: {analysis_b.risk_score if analysis_b else 'N/A'})

Clauses only in A: {', '.join(only_in_a) or 'None'}
Clauses only in B: {', '.join(only_in_b) or 'None'}

Key differences in shared clauses:
{json.dumps(differences, indent=2)}

Provide a 2-3 sentence summary of the key differences between these documents."""

    try:
        summary = _call_gpt4o("You are a legal document comparison specialist.", comparison_prompt)
    except Exception:
        summary = "Unable to generate comparison summary."

    return {
        "document_a": {
            "id": str(doc_a.id),
            "title": doc_a.title,
            "risk_score": analysis_a.risk_score if analysis_a else None,
        },
        "document_b": {
            "id": str(doc_b.id),
            "title": doc_b.title,
            "risk_score": analysis_b.risk_score if analysis_b else None,
        },
        "differences": differences,
        "clauses_only_in_a": only_in_a,
        "clauses_only_in_b": only_in_b,
        "summary": summary,
    }
