"""DTOs (Data Transfer Objects) for API communication."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID


class MessageDTO(BaseModel):
    """DTO for chat messages."""
    content: str
    is_bot: bool = False
    timestamp: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None


class ChatSessionDTO(BaseModel):
    """DTO for chat sessions."""
    id: str
    title: str
    messages: List[MessageDTO] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuestionRequestDTO(BaseModel):
    """DTO for question requests."""
    question: str


class ChatRequestDTO(BaseModel):
    """DTO for chat creation requests."""
    title: str = "New conversation"


class ErrorResponseDTO(BaseModel):
    """DTO for error responses."""
    detail: str
