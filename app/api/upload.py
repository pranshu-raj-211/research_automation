from fastapi import APIRouter, UploadFile, File
from app.main import app
from app.db.db_utils import init_document_model
import uuid

router = APIRouter(prefix='/docs/')


@app.post('/upload/')
async def upload_document(file:UploadFile=File(...)):
    print(file.content_type)
    task_id = str(uuid.uuid4())
    contents = await file.read()
    filepath = f'tmp/{task_id}.pdf'
    with open(filepath, 'wb') as f:
        f.write(contents)
    print(file.size)
    # TODO: fill this in
    document_record = None
    await init_document_model(document_record)
    return {'code':202, 'message':"Uploaded file for processing", 'task_id':task_id}