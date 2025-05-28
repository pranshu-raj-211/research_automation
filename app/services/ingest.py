import pdfplumber
from llama_index.core.node_parser import SentenceSplitter

from app.db.db_utils import insert_many_chunks, mark_ingestion_status
from app.utils.embeddings import get_embedding
from app.config import logger


async def ingest_pdf_background(file_bytes: bytes, filename: str):
    logger.info(f"Received request to ingest file: {filename}")
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)

    try:
        async def process_page(page_text: str, page_num: int):
            if not page_text.strip():
                return []

            nodes = splitter.get_nodes_from_documents([page_text])
            chunks = []
            for i, node in enumerate(nodes):
                embedding = await get_embedding(node.text)
                chunks.append({
                    "topic_id": None,
                    "doc_id": filename,
                    "page_no": page_num,
                    "para_no": i,
                    "text": node.text,
                    "embedding": embedding,
                })
            return chunks

        all_chunks = []
        with pdfplumber.open(file_bytes) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                logger.info(f"Processing page {page_num + 1} of {len(pdf.pages)}")
                chunks = await process_page(page_text, page_num)
                all_chunks.extend(chunks)

        if all_chunks:
            result = await insert_many_chunks(all_chunks)
            chunk_ids = [str(chunk.inserted_id) for chunk in result.inserted_ids]
            logger.info(f"Successfully inserted {len(all_chunks)} chunks into the database.")

        await mark_ingestion_status(filename, "success")
        logger.info(f"Ingestion completed successfully for file: {filename}")

        return chunk_ids

    except Exception as e:
        logger.exception(f"Ingestion failed for file: {filename}")
        await mark_ingestion_status(filename, "failed")
        raise e
