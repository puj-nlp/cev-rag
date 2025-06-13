from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Modelo para los mensajes del chat."""
    content: str
    is_bot: bool = False
    timestamp: Optional[str] = None


class ChatSession(BaseModel):
    """Modelo para las sesiones de chat."""
    id: str
    title: str
    messages: List[Message] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuestionRequest(BaseModel):
    """Modelo para las solicitudes de preguntas."""
    question: str
    chat_id: str


class ChatRequest(BaseModel):
    """Modelo para las solicitudes de creación de chat."""
    title: str = "Nueva conversación"


class ErrorResponse(BaseModel):
    """Modelo para las respuestas de error."""
    detail: str
