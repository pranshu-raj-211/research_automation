from app.config import settings, logger
from ollama import embeddings

async def get_embedding(text: str) -> list[float]:
    """Generate embeddings using a locally running Ollama model."""
    model = settings.OLLAMA_EMBEDDING_MODEL
    try:
        result = embeddings(model=model, prompt=text)
        return result['embedding']
    except Exception as e:
        logger.exception(f"Ollama embedding failed: {e}")
        return []