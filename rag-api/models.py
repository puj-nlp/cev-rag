from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Model for chat messages."""
    content: str
    is_bot: bool = False
    timestamp: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None


class ChatSession(BaseModel):
    """Model for chat sessions."""
    id: str
    title: str
    messages: List[Message] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuestionRequest(BaseModel):
    """Model for question requests."""
    question: str
    chat_id: str


class ChatRequest(BaseModel):
    """Model for chat creation requests."""
    title: str = "New conversation"


class ErrorResponse(BaseModel):
    """Model for error responses."""
    detail: str
