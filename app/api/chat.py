from fastapi import HTTPException, APIRouter
from typing import Any
from app.services.chat_service import rag_chat_service
from app.config import logger
from app.schemas import ChatRequest, ChatResponse, SimilarChunksRequest


router = APIRouter(prefix="/search")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Chat with documents using RAG.

    This endpoint processes a user's question and returns an AI-generated response
    based on relevant document chunks, along with source citations.
    """
    try:
        result = await rag_chat_service.chat(
            query=request.query,
            topic_id=request.topic_id,
            similarity_top_k=request.similarity_top_k,
            include_sources=request.include_sources,
        )
        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/get-chunks", response_model=list[dict[str, Any]])
async def search_similar_chunks(request: SimilarChunksRequest):
    """
    Search for similar document chunks without generating a response

    This endpoint returns raw document chunks that are similar to the query,
    useful for exploring relevant content before asking specific questions.
    """
    try:
        chunks = await rag_chat_service.get_similar_chunks(
            query=request.query, topic_id=request.topic_id, limit=request.limit
        )
        return chunks

    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        return HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the chat service"""
    try:
        test_query = "test"
        await rag_chat_service.get_similar_chunks(test_query, limit=1)

        return {
            "status": "healthy",
            "service": "chat",
            "models": {"llm": "Connected", "embedding": "Connected"},
            "database": "Connected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
