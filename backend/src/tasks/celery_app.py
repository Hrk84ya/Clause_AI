from celery import Celery
from src.config import settings

celery_app = Celery(
    "legal_doc_analyzer",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=False,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["src.tasks"])
