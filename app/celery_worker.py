from celery import Celery
from app.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.imports = ['app.utils.celery_tasks']

celery_app.conf.task_routes = {
    "app.utils.celery_tasks.process_pdf_task": {"queue": "ingestion"},
}
