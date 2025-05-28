from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.db.db_utils import init_document_model, get_ingestion_status
from app.utils.celery_tasks import process_pdf_task
from app.config import logger, settings
import uuid
import os

router = APIRouter(prefix='/docs')


@router.post('/upload')
async def upload_document(file: UploadFile = File(...)):
    logger.debug("Document uploaded")
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    contents = await file.read()
    file_size = len(contents) / (1024 * 1024)
    if file_size > settings.MAX_DOC_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_DOC_SIZE_MB} MB limit.")

    task_id = str(uuid.uuid4())
    filepath = f'tmp/{task_id}.pdf'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as f:
        f.write(contents)

    document_record = {
        "id": task_id,
        "topic_id": None,  # To be updated later
        "user_id": None,  # To be updated later
        "text": [],
        "authors": [],
        "citations": [],
        "schema_version": "1",
        "status": "pending"
    }

    await init_document_model(document_record)
    process_pdf_task.delay(filepath, task_id)

    logger.info(f"Document {task_id} uploaded and queued for processing.")

    return {"code": 202, "message": "Uploaded file for processing", "task_id": task_id}


@router.get('/status')
async def check_document_status(task_id: str = Query(...)):
    """Check the processing status of a document."""
    status = await get_ingestion_status(task_id)
    if status == "not_found":
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"task_id": task_id, "status": status}