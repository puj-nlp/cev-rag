"""Domain entities for the RAG API."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


@dataclass
class Message:
    """Domain entity representing a chat message."""
    content: str
    is_bot: bool = False
    timestamp: Optional[datetime] = None
    references: Optional[List[Dict[str, Any]]] = None


@dataclass
class ChatSession:
    """Domain entity representing a chat session."""
    id: UUID
    title: str
    session_id: Optional[str]
    messages: List[Message]
    created_at: datetime
    updated_at: datetime


@dataclass
class Document:
    """Domain entity representing a document from the vector database."""
    content: str
    metadata: Dict[str, Any]
    score: float
    original_fields: Optional[Dict[str, Any]] = None


@dataclass
class Question:
    """Domain entity representing a user question."""
    text: str
    chat_id: UUID


@dataclass
class Reference:
    """Domain entity representing a bibliographic reference."""
    number: int
    title: str
    source_id: str
    page: str
    year: str
    publisher: str
    isbn: str
    url: Optional[str] = None


@dataclass
class RAGContext:
    """Domain entity representing the context for RAG generation."""
    documents: List[Document]
    context_text: str
    references: List[Reference]


@dataclass
class ChatResponse:
    """Domain entity representing a response from the RAG system."""
    content: str
    references: List[Reference]
    contexts_used: Optional[List[Dict[str, Any]]] = None
