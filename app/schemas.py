from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class Text(BaseModel):
    id: str
    doc_id: str
    topic_id: str
    page_no: int
    para_no: int
    text: str
    embedding: list[float]
    schema_version: str


class Doc(BaseModel):
    id: str
    topic_id: str
    user_id: str
    text: list[str]  # Links to Text.id
    authors: list[str] = []
    citations: list[str] = []
    schema_version: str
    status: str  # Added to track ingestion status


class ResultsLogEntry(BaseModel):
    doc_id: str
    result_summary: str
    result_metrics: dict = None  # For future use
    methods_used: list[str]
    subset_of_problem: str


class Topic(BaseModel):
    id: str
    name: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    summary: str
    chat_id: str
    documents: list[str]  # Links to Doc.id
    num_docs: int
    docs_size_total: int
    results_log: list[ResultsLogEntry]
    schema_version: str


class User(BaseModel):
    id: str
    name: str
    mail: str
    password: str
    created_at: datetime
    updated_at: datetime
    topic_ids: list[str]
    session_id: str


class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question")
    topic_id: Optional[str] = Field(None, description="Topic ID to filter results")
    similarity_top_k: int = Field(
        10, ge=1, le=50, description="Number of similar chunks to retrieve"
    )
    include_sources: bool = Field(
        True, description="Whether to include source citations"
    )


class ChatResponse(BaseModel):
    response: str
    query: str
    topic_id: Optional[str]
    sources_count: int
    sources: Optional[list[dict[str, Any]]] = None
    error: Optional[str] = None


class SimilarChunksRequest(BaseModel):
    query: str = Field(..., description="The search query")
    topic_id: Optional[str] = Field(None, description="Topic ID to filter results")
    limit: int = Field(
        10, ge=1, le=50, description="Maximum number of chunks to return"
    )
