import hashlib
import json
from pathlib import Path

import faiss
import numpy as np
import redis
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import settings

# Initialize clients lazily
_openai_client = None
_redis_client = None


def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.openai_api_key)
    return _openai_client


def _get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_openai_embedding(texts: list[str]) -> list[list[float]]:
    """Call OpenAI embeddings API with retry logic."""
    client = _get_openai_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    """
    Generate embeddings for chunks with Redis caching.

    For each chunk:
    - Compute SHA-256 of content
    - Check Redis cache: embed:{sha256}
    - Cache hit: deserialize from JSON
    - Cache miss: call OpenAI text-embedding-3-small
    - Store in Redis with TTL=86400 (24 hours)

    Returns list of 1536-dim float vectors.
    """
    r = _get_redis_client()
    embeddings: list[list[float]] = [None] * len(chunks)
    uncached_indices: list[int] = []
    uncached_texts: list[str] = []

    # Check cache
    for i, chunk in enumerate(chunks):
        content_hash = hashlib.sha256(chunk["content"].encode()).hexdigest()
        cache_key = f"embed:{content_hash}"
        cached = r.get(cache_key)
        if cached:
            embeddings[i] = json.loads(cached)
        else:
            uncached_indices.append(i)
            uncached_texts.append(chunk["content"])

    # Batch call OpenAI for uncached chunks
    if uncached_texts:
        # Process in batches of 100 (OpenAI limit)
        batch_size = 100
        for batch_start in range(0, len(uncached_texts), batch_size):
            batch_end = min(batch_start + batch_size, len(uncached_texts))
            batch_texts = uncached_texts[batch_start:batch_end]
            batch_embeddings = _call_openai_embedding(batch_texts)

            for j, embedding in enumerate(batch_embeddings):
                idx = uncached_indices[batch_start + j]
                embeddings[idx] = embedding

                # Cache in Redis
                content_hash = hashlib.sha256(chunks[idx]["content"].encode()).hexdigest()
                cache_key = f"embed:{content_hash}"
                r.setex(cache_key, 86400, json.dumps(embedding))

    return embeddings


def build_faiss_index(embeddings: list[list[float]], doc_id: str) -> None:
    """Build FAISS IndexFlatIP, normalize vectors, save to disk."""
    vectors = np.array(embeddings, dtype=np.float32)
    # Normalize for cosine similarity via inner product
    faiss.normalize_L2(vectors)

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    # Save to disk
    faiss_dir = Path(settings.faiss_dir)
    faiss_dir.mkdir(parents=True, exist_ok=True)
    index_path = faiss_dir / f"{doc_id}.index"
    faiss.write_index(index, str(index_path))


def load_faiss_index(doc_id: str) -> faiss.Index:
    """Load a FAISS index from disk."""
    index_path = Path(settings.faiss_dir) / f"{doc_id}.index"
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found for document {doc_id}")
    return faiss.read_index(str(index_path))


def search_faiss(doc_id: str, query_embedding: list[float], k: int = 5) -> list[int]:
    """Search FAISS index and return top-k chunk indices."""
    index = load_faiss_index(doc_id)
    query_vector = np.array([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query_vector)

    distances, indices = index.search(query_vector, min(k, index.ntotal))
    return [int(idx) for idx in indices[0] if idx >= 0]
