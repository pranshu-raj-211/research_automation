from celery import Celery
from app.config import settings


celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_routes = {
    "app.pipelines.ingest.ingest_doc": {"queue": "ingestion"},
}
