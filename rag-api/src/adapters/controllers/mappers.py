"""Mappers for converting between DTOs and domain entities."""

from typing import List
from uuid import UUID

from ...domain.entities import ChatSession, Message, Question
from .dto import ChatSessionDTO, MessageDTO, QuestionRequestDTO


class ChatSessionMapper:
    """Mapper for ChatSession entities and DTOs."""
    
    @staticmethod
    def to_dto(entity: ChatSession) -> ChatSessionDTO:
        """Convert ChatSession entity to DTO."""
        return ChatSessionDTO(
            id=str(entity.id),
            title=entity.title,
            messages=[MessageMapper.to_dto(msg) for msg in entity.messages],
            created_at=entity.created_at.isoformat(),
            updated_at=entity.updated_at.isoformat()
        )
    
    @staticmethod
    def from_dto(dto: ChatSessionDTO) -> ChatSession:
        """Convert ChatSession DTO to entity."""
        from datetime import datetime
        
        return ChatSession(
            id=UUID(dto.id),
            title=dto.title,
            messages=[MessageMapper.from_dto(msg) for msg in dto.messages],
            created_at=datetime.fromisoformat(dto.created_at) if dto.created_at else datetime.now(),
            updated_at=datetime.fromisoformat(dto.updated_at) if dto.updated_at else datetime.now()
        )


class MessageMapper:
    """Mapper for Message entities and DTOs."""
    
    @staticmethod
    def to_dto(entity: Message) -> MessageDTO:
        """Convert Message entity to DTO."""
        return MessageDTO(
            content=entity.content,
            is_bot=entity.is_bot,
            timestamp=entity.timestamp.isoformat() if entity.timestamp else None,
            references=entity.references
        )
    
    @staticmethod
    def from_dto(dto: MessageDTO) -> Message:
        """Convert Message DTO to entity."""
        from datetime import datetime
        
        return Message(
            content=dto.content,
            is_bot=dto.is_bot,
            timestamp=datetime.fromisoformat(dto.timestamp) if dto.timestamp else None,
            references=dto.references
        )


class QuestionMapper:
    """Mapper for Question entities."""
    
    @staticmethod
    def from_request(chat_id: UUID, request: QuestionRequestDTO) -> Question:
        """Convert question request to Question entity."""
        return Question(
            text=request.question,
            chat_id=chat_id
        )
