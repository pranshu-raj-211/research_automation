from fastapi import APIRouter, UploadFile, File, HTTPException
from app.main import app
from app.db.db_utils import init_document_model
from app.utils.celery_tasks import process_pdf_task
from app.config import logger, settings
import uuid
import os

router = APIRouter(prefix='/docs/')


@app.post('/upload/')
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_size = len(await file.read()) / (1024 * 1024)  # Convert bytes to MB
    if file_size > settings.MAX_DOC_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_DOC_SIZE_MB} MB limit.")

    task_id = str(uuid.uuid4())
    filepath = f'tmp/{task_id}.pdf'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'wb') as f:
        f.write(await file.read())

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