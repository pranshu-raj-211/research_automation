import asyncio
from app.services.ingest import ingest_pdf_background
from app.db.db_utils import mark_ingestion_status
from app.celery_worker import celery_app


@celery_app.task(name="process_pdf_task")
def process_pdf_task(file_bytes: bytes, filename: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ingest_pdf_background(file_bytes, filename))
    loop.run_until_complete(mark_ingestion_status(filename, status="completed"))