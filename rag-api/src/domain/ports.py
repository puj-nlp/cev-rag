"""Domain ports (interfaces) for the RAG API."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from .entities import ChatSession, Message, Document, Question, ChatResponse, RAGContext


class ChatSessionRepository(ABC):
    """Port for chat session persistence."""
    
    @abstractmethod
    async def save(self, chat_session: ChatSession) -> ChatSession:
        """Save a chat session."""
        pass
    
    @abstractmethod
    async def find_by_id(self, chat_id: UUID) -> Optional[ChatSession]:
        """Find a chat session by ID."""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[ChatSession]:
        """Find all chat sessions."""
        pass
    
    @abstractmethod
    async def find_by_session_id(self, session_id: str) -> List[ChatSession]:
        """Find all chat sessions for a specific session ID."""
        pass
    
    @abstractmethod
    async def delete(self, chat_id: UUID) -> bool:
        """Delete a chat session."""
        pass


class VectorDatabase(ABC):
    """Port for vector database operations."""
    
    @abstractmethod
    async def search_similar_documents(self, embedding: List[float], limit: int = 5) -> List[Document]:
        """Search for similar documents using vector similarity."""
        pass
    
    @abstractmethod
    async def verify_connection(self) -> bool:
        """Verify database connection."""
        pass


class EmbeddingService(ABC):
    """Port for embedding generation."""
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text."""
        pass


class LLMService(ABC):
    """Port for Large Language Model operations."""
    
    @abstractmethod
    async def generate_answer(
        self, 
        question: str, 
        context: str, 
        chat_history: List[Dict[str, Any]]
    ) -> str:
        """Generate an answer using the LLM."""
        pass
    
    @abstractmethod
    async def generate_answer_with_tools(
        self, 
        question: str, 
        chat_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate an answer using LLM with tool calling capabilities."""
        pass


class RAGContextBuilder(ABC):
    """Port for building RAG context from documents."""
    
    @abstractmethod
    async def build_context(self, documents: List[Document], question: str) -> RAGContext:
        """Build RAG context from retrieved documents."""
        pass


class TimestampService(ABC):
    """Port for timestamp operations."""
    
    @abstractmethod
    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        pass
