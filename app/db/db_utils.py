import asyncio
from app import get_embedding_model
from app.db import db
from app.config import logger
from typing import Optional
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle


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
    except Exception as e:
        logger.exception(f"Failed to add chunk into db: {chunk}")
        raise e


async def insert_many_chunks(chunks: list[dict]):
    """Bulk insert multiple embedded chunks (use for better performance)."""
    try:
        if chunks:
            result = await db.text.insert_many(chunks)
            return result
        return None
    except Exception as e:
        logger.exception("Failed to insert multiple chunks into db")
        raise e


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
    except Exception as e:
        logger.exception("Ingestion status could not be updated.")
        raise e

async def get_ingestion_status(filename: str) -> str:
    """Check status of a document by name."""
    record = await db.docs.find_one({"doc_id": filename})
    return record["status"] if record else "not_found"


# TODO: doc record validation acc to schemas, improve fields
async def init_document_model(document_record:dict):
    try:
        await db.docs.insert_one(document_record)
    except Exception as e:
        logger.exception(f"Failed to init document model: {document_record}")
        raise e


async def retrieve_similar_chunks(
    query: str,
    topic_id: Optional[str] = None,
    similarity_top_k: int = 10,
    similarity_threshold: float = 0.7,
) -> list[NodeWithScore]:
    """
    Retrieve similar chunks from MongoDB using vector search

    Args:
        query: Search query
        topic_id: Optional topic ID to filter results
        similarity_top_k: Number of similar chunks to retrieve
        similarity_threshold: Minimum similarity score threshold

    Returns:
        List of NodeWithScore objects
    """
    try:
        embedding_model = get_embedding_model()
        query_embedding = embedding_model.get_text_embedding(query)

        # Build MongoDB aggregation pipeline for vector search
        pipeline = []
        if topic_id:
            pipeline.append({"$match": {"topic_id": topic_id}})
        pipeline.extend(
            [
                {
                    "$vectorSearch": {
                        "index": "embedding_vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": similarity_top_k * 3,
                        "limit": similarity_top_k,
                    }
                },
                {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
            ]
        )

        results = []
        async for result in db.Text.aggregate(pipeline):
            results.append(result)

        nodes_with_scores = []
        for result in results:
            score = result.get("score", 0)
            if score < similarity_threshold:
                continue
            node = TextNode(
                text=result["text"],
                metadata={
                    "doc_id": result["doc_id"],
                    "page_no": result.get("page_no"),
                    "para_no": result.get("para_no"),
                    "topic_id": result["topic_id"],
                    "score": score,
                },
            )

            node_with_score = NodeWithScore(node=node, score=score)
            nodes_with_scores.append(node_with_score)

        return nodes_with_scores

    except Exception as e:
        logger.error(f"Error retrieving from MongoDB: {str(e)}")
        return []


class AsyncMongoRetriever:
    """Async retriever wrapper for LlamaIndex compatibility"""

    def __init__(
        self,
        topic_id: Optional[str] = None,
        similarity_top_k: int = 10,
        similarity_threshold: float = 0.7,
    ):
        self.topic_id = topic_id
        self.similarity_top_k = similarity_top_k
        self.similarity_threshold = similarity_threshold

    async def aretrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Async retrieve method"""
        return await retrieve_similar_chunks(
            query=query_bundle.query_str,
            topic_id=self.topic_id,
            similarity_top_k=self.similarity_top_k,
            similarity_threshold=self.similarity_threshold,
        )

    def retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Sync retrieve method for compatibility"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.aretrieve(query_bundle))
        except RuntimeError:
            return asyncio.run(self.aretrieve(query_bundle))
