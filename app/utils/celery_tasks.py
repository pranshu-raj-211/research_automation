import asyncio
from app.services.ingest import ingest_pdf_background
from app.db.db_utils import mark_ingestion_status
from app.db.db_utils import init_document_model
from app.celery_worker import celery_app
from app.config import logger

@celery_app.task(name="app.utils.celery_tasks.process_pdf_task", queue='ingestion')
def process_pdf_task(filepath: str, task_id: str):
    logger.debug(f"Started on ingestion task: {task_id}")
    try:
        loop = asyncio.get_event_loop()
        chunk_ids = loop.run_until_complete(ingest_pdf_background(filepath, task_id))
        logger.debug(f'Ingestion task: {task_id} done')
        loop.run_until_complete(mark_ingestion_status(task_id, status="done"))

        document_update = {
            "$set": {
                "text": chunk_ids,
                "status": "done"
            }
        }
        loop.run_until_complete(init_document_model({"id": task_id, **document_update}))

        logger.info(f"Document {task_id} processed successfully.")
    except Exception:
        logger.exception(f"Failed to process document {task_id}.")
        loop.run_until_complete(mark_ingestion_status(task_id, status="failed"))