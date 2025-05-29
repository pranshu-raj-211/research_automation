from app.db import db
from app.config import logger


async def insert_doc_chunk(
    topic_id: str,
    doc_id: str,
    page_no: int,
    para_no: int,
    text: str,
    embedding: list[float],
    schema_version: int = 1
):
    """Insert one embedded text chunk into MongoDB."""
    try:
        chunk = {
            "topic_id": topic_id,
            "doc_id": doc_id,
            "page_no": page_no,
            "para_no": para_no,
            "text": text,
            "embedding": embedding,
            "schema_version": schema_version
        }
        await db.text.insert_one(chunk)
    except Exception:
        logger.exception(f"Failed to add chunk into db: {chunk}")
        raise Exception("Could not insert doc chunk into db.")


async def insert_many_chunks(chunks: list[dict]):
    """Bulk insert multiple embedded chunks (use for better performance)."""
    try:
        if chunks:
            result = await db.text.insert_many(chunks)
            return result
        return None
    except Exception:
        logger.exception("Failed to insert multiple chunks into db")
        raise Exception("Could not insert chunks into db.")


async def mark_ingestion_status(filename: str, status: str):
    """Store or update the ingestion status of a document."""
    logger.info(f"Marking ingestion status for {filename} as {status}")
    try:
        await db.docs.update_one(
            {"doc_id": filename},
            {"$set": {"status": status}},
            upsert=True
        )
        logger.info('Ingestion status updated')
    except Exception:
        logger.exception("Ingestion status could not be updated.")
        raise Exception("Failed to update doc ingestion status")

async def get_ingestion_status(filename: str) -> str:
    """Check status of a document by name."""
    record = await db.docs.find_one({"doc_id": filename})
    return record["status"] if record else "not_found"


# TODO: doc record validation acc to schemas, improve fields
async def init_document_model(document_record:dict):
    try:
        await db.docs.insert_one(document_record)
    except Exception:
        logger.exception(f"Failed to init document model: {document_record}")
        raise Exception("Could not initialize document.")