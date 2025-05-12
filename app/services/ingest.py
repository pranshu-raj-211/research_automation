import pdfplumber
from llama_index.core.node_parser import SentenceSplitter

from app.db.db_utils import insert_doc_chunk, mark_ingestion_status
from app.utils.embeddings import get_embedding


async def ingest_pdf_background(file_bytes: bytes, filename: str):
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)

    try:

        async def process_page(page_text: str, page_num: int):
            if not page_text.strip():
                return

            nodes = splitter.get_nodes_from_documents([page_text])
            for i, node in enumerate(nodes):
                embedding = get_embedding(node.text)
                # TODO: use batch insert instead
                await insert_doc_chunk(
                    topic_id=None,
                    doc_id=filename,
                    page_no=page_num,
                    para_no=i,
                    text=node.text,
                    embedding=embedding,
                )

        with pdfplumber.open(file_bytes) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                await process_page(page_text, page_num)

        await mark_ingestion_status(filename, "success")

    except Exception as e:
        await mark_ingestion_status(filename, "failed")
        raise e
