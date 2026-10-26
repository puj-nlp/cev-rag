"""DTOs (Data Transfer Objects) for API communication."""

import re
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from uuid import UUID

# Control characters except tab, line feed and carriage return
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

MAX_QUESTION_LENGTH = 2000
MAX_TITLE_LENGTH = 200


def _clean_text(value: str) -> str:
    return _CONTROL_CHARS.sub("", value).strip()


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
    session_id: Optional[str] = None
    messages: List[MessageDTO] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuestionRequestDTO(BaseModel):
    """DTO for question requests."""
    question: str = Field(..., max_length=MAX_QUESTION_LENGTH)
    session_id: Optional[str] = Field(None, max_length=64)
    language: Literal["es", "en"] = "es"

    @field_validator("question")
    @classmethod
    def clean_question(cls, value: str) -> str:
        value = _clean_text(value)
        if not value:
            raise ValueError("Question must not be empty")
        return value


class ChatRequestDTO(BaseModel):
    """DTO for chat creation requests."""
    title: str = Field("New conversation", max_length=MAX_TITLE_LENGTH)
    session_id: Optional[str] = Field(None, max_length=64)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return _clean_text(value) or "New conversation"


class SessionRequestDTO(BaseModel):
    """DTO for establishing the frontend session cookie."""
    legacy_session_id: Optional[str] = Field(None, max_length=64)


class ErrorResponseDTO(BaseModel):
    """DTO for error responses."""
    detail: str
