"""In-memory implementation of ChatSessionRepository."""

from typing import Dict, List, Optional
from uuid import UUID

from ...domain.entities import ChatSession
from ...domain.ports import ChatSessionRepository


class InMemoryChatSessionRepository(ChatSessionRepository):
    """In-memory implementation of chat session repository."""
    
    def __init__(self):
        self._chats: Dict[UUID, ChatSession] = {}
    
    async def save(self, chat_session: ChatSession) -> ChatSession:
        """Save a chat session."""
        self._chats[chat_session.id] = chat_session
        return chat_session
    
    async def find_by_id(self, chat_id: UUID) -> Optional[ChatSession]:
        """Find a chat session by ID."""
        return self._chats.get(chat_id)
    
    async def find_all(self) -> List[ChatSession]:
        """Find all chat sessions."""
        return list(self._chats.values())
    
    async def find_by_session_id(self, session_id: str) -> List[ChatSession]:
        """Find all chat sessions for a specific session ID."""
        return [
            chat for chat in self._chats.values() 
            if chat.session_id == session_id
        ]
    
    async def delete(self, chat_id: UUID) -> bool:
        """Delete a chat session."""
        if chat_id in self._chats:
            del self._chats[chat_id]
            return True
        return False
