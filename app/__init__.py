from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from app.config import settings
from llama_index.core import Settings


def get_llm():
    """Get or create LLM instance"""
    global _llm
    if _llm is None:
        _llm = Ollama(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.0,
            request_timeout=120.0,
        )
    return _llm


def get_embedding_model():
    """Get or create embedding model instance"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OllamaEmbedding(
            model_name=settings.OLLAMA_EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
    return _embedding_model


def initialize_rag_settings():
    """Initialize global LlamaIndex settings"""
    Settings.llm = get_llm()
    Settings.embed_model = get_embedding_model()