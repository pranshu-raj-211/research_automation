from pydantic import BaseModel
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


class ChatExchange(BaseModel):
    query: str
    response: str
    source_list: list[str]  # Links to Doc/Text


class Chat(BaseModel):
    chat_id: str
    topic_id: str
    documents: list[str]  # Links to Doc.id
    documents_selected: list[bool]
    schema_version: str
    exchanges: list[ChatExchange]


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
