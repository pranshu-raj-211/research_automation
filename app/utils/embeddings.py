import httpx
from app.config import settings


async def get_embedding(text: str) -> list[float]:
    """Generate embeddings using a locally running Ollama model."""
    response = await httpx.post(
        settings.OLLAMA_BASE_URL,
        json={"model": settings.OLLAMA_EMBEDDING_MODEL, "prompt": text}
    )

    if response.status_code != 200:
        raise RuntimeError(f"Embedding request failed: {response.text}")

    return response.json()["embedding"]
