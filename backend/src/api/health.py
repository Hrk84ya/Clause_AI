import redis
from fastapi import APIRouter
from sqlalchemy import text

from src.config import settings
from src.database import async_session

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Check service health: DB, Redis, and overall status."""
    services = {}
    overall = "ok"

    # Check database
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        services["database"] = "ok"
    except Exception:
        services["database"] = "error"
        overall = "degraded"

    # Check Redis
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        services["redis"] = "ok"
    except Exception:
        services["redis"] = "error"
        overall = "degraded"

    # Check Celery (basic — just verify broker is reachable)
    services["celery"] = services.get("redis", "error")  # Celery uses Redis as broker

    return {
        "status": overall,
        "services": services,
        "version": "1.0.0",
    }
