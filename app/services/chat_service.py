from typing import Any, Optional
from llama_index.core.schema import NodeWithScore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from app.config import logger
from app.db.db_utils import AsyncMongoRetriever, retrieve_similar_chunks


def format_citations(source_nodes: list[NodeWithScore]) -> str:
    """Format citations from source nodes"""
    if not source_nodes:
        return ""

    citations = []
    seen_docs = set()

    for i, node_with_score in enumerate(source_nodes, 1):
        metadata = node_with_score.node.metadata
        doc_id = metadata.get("doc_id")
        page_no = metadata.get("page_no")
        score = metadata.get("score", 0)

        if doc_id not in seen_docs:
            citation = f"[{i}] Document: {doc_id}"
            if page_no:
                citation += f", Page: {page_no}"
            citation += f" (Relevance: {score:.3f})"
            citations.append(citation)
            seen_docs.add(doc_id)

    return "\n\n**Sources:**\n" + "\n".join(citations)


async def chat_with_rag(
    query: str,
    topic_id: Optional[str] = None,
    similarity_top_k: int = 10,
    include_sources: bool = True,
    similarity_threshold: float = 0.7,
) -> dict[str, Any]:
    """
    Process a chat query using RAG

    Args:
        query: User's question
        topic_id: Optional topic ID to filter results
        similarity_top_k: Number of similar chunks to retrieve
        include_sources: Whether to include source citations
        similarity_threshold: Minimum similarity score threshold

    Returns:
        Dict containing response and metadata
    """
    try:
        retriever = AsyncMongoRetriever(
            topic_id=topic_id,
            similarity_top_k=similarity_top_k,
            similarity_threshold=similarity_threshold,
        )

        response_synthesizer = get_response_synthesizer(
            response_mode="tree_summarize", use_async=True
        )

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=similarity_threshold)
            ],
        )

        response = await query_engine.aquery(query)

        result = {
            "response": response.response,
            "query": query,
            "topic_id": topic_id,
            "sources_count": len(response.source_nodes) if response.source_nodes else 0,
        }

        if include_sources and response.source_nodes:
            citations = format_citations(response.source_nodes)
            result["response"] += citations
            result["sources"] = [
                {
                    "doc_id": node.node.metadata.get("doc_id"),
                    "page_no": node.node.metadata.get("page_no"),
                    "para_no": node.node.metadata.get("para_no"),
                    "score": node.score,
                    "text_preview": (
                        node.node.text[:200] + "..."
                        if len(node.node.text) > 200
                        else node.node.text
                    ),
                }
                for node in response.source_nodes
            ]

        return result

    except Exception as e:
        logger.error(f"Error in chat query: {str(e)}")
        return {
            "response": f"I apologize, but I encountered an error while processing your question: {str(e)}",
            "query": query,
            "topic_id": topic_id,
            "sources_count": 0,
            "error": str(e),
        }


async def get_similar_chunks(
    query: str,
    topic_id: Optional[str] = None,
    limit: int = 10,
    similarity_threshold: float = 0.7,
) -> list[dict[str, Any]]:
    """
    Get similar chunks without generating a response

    Args:
        query: Search query
        topic_id: Optional topic ID to filter results
        limit: Maximum number of chunks to return
        similarity_threshold: Minimum similarity score threshold

    Returns:
        List of similar chunks with metadata
    """
    try:
        source_nodes = await retrieve_similar_chunks(
            query=query,
            topic_id=topic_id,
            similarity_top_k=limit,
            similarity_threshold=similarity_threshold,
        )

        return [
            {
                "doc_id": node.node.metadata.get("doc_id"),
                "page_no": node.node.metadata.get("page_no"),
                "para_no": node.node.metadata.get("para_no"),
                "text": node.node.text,
                "score": node.score,
                "topic_id": node.node.metadata.get("topic_id"),
            }
            for node in source_nodes
        ]

    except Exception as e:
        logger.error(f"Error getting similar chunks: {str(e)}")
        return []
