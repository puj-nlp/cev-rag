"""FastAPI controllers for the RAG API."""

from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from ...application.use_cases import ChatSessionUseCase, QuestionAnsweringUseCase
from .dto import ChatSessionDTO, MessageDTO, QuestionRequestDTO, ChatRequestDTO, ErrorResponseDTO
from .mappers import ChatSessionMapper, MessageMapper, QuestionMapper


class ChatController:
    """Controller for chat session operations."""
    
    def __init__(self, chat_use_case: ChatSessionUseCase):
        self._chat_use_case = chat_use_case
        self.router = APIRouter(prefix="/chats", tags=["chats"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the routes for this controller."""
        self.router.add_api_route(
            "",
            self.list_chats,
            methods=["GET"],
            response_model=List[ChatSessionDTO]
        )
        self.router.add_api_route(
            "",
            self.create_chat,
            methods=["POST"],
            response_model=ChatSessionDTO
        )
        self.router.add_api_route(
            "/{chat_id}",
            self.get_chat,
            methods=["GET"],
            response_model=ChatSessionDTO
        )
        self.router.add_api_route(
            "/{chat_id}",
            self.delete_chat,
            methods=["DELETE"]
        )
    
    async def list_chats(self) -> List[ChatSessionDTO]:
        """List all chat sessions."""
        chat_sessions = await self._chat_use_case.list_chat_sessions()
        return [ChatSessionMapper.to_dto(chat) for chat in chat_sessions]
    
    async def create_chat(self, chat_request: ChatRequestDTO) -> ChatSessionDTO:
        """Create a new chat session."""
        chat_session = await self._chat_use_case.create_chat_session(chat_request.title)
        return ChatSessionMapper.to_dto(chat_session)
    
    async def get_chat(self, chat_id: str) -> ChatSessionDTO:
        """Get a specific chat session."""
        try:
            chat_uuid = UUID(chat_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")
        
        chat_session = await self._chat_use_case.get_chat_session(chat_uuid)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return ChatSessionMapper.to_dto(chat_session)
    
    async def delete_chat(self, chat_id: str):
        """Delete a chat session."""
        try:
            chat_uuid = UUID(chat_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")
        
        success = await self._chat_use_case.delete_chat_session(chat_uuid)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}


class QuestionController:
    """Controller for question answering operations."""
    
    def __init__(self, qa_use_case: QuestionAnsweringUseCase):
        self._qa_use_case = qa_use_case
        self.router = APIRouter(prefix="/chats", tags=["questions"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the routes for this controller."""
        self.router.add_api_route(
            "/{chat_id}/messages",
            self.add_message,
            methods=["POST"],
            response_model=MessageDTO
        )
    
    async def add_message(
        self,
        chat_id: str,
        question_request: QuestionRequestDTO,
        use_tools: bool = Query(True, description="Whether to use the tool calling approach")
    ) -> MessageDTO:
        """Process a question and add the response to the chat."""
        try:
            chat_uuid = UUID(chat_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid chat ID format")
        
        try:
            # Convert request to domain entity
            question = QuestionMapper.from_request(chat_uuid, question_request)
            
            # Process the question
            response_message = await self._qa_use_case.process_question(
                question, use_tools=use_tools
            )
            
            # Convert response to DTO
            return MessageMapper.to_dto(response_message)
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            error_message = "Could not process the question. Please try again."
            
            # Customize error message based on error type
            error_str = str(e).lower()
            if "empty" in error_str or "está vacía" in error_str:
                error_message = "The database contains no documents. Please ensure data has been correctly loaded."
            elif "connection" in error_str or "connect" in error_str:
                error_message = "Could not connect to the database. Please verify the connection."
            elif "dimension" in error_str or "dimensión" in error_str:
                error_message = "There is a problem with the vector dimensions. Please verify the configuration."
            
            raise HTTPException(status_code=500, detail=error_message)


class HealthController:
    """Controller for health check operations."""
    
    def __init__(self):
        self.router = APIRouter(tags=["health"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup the routes for this controller."""
        self.router.add_api_route(
            "/",
            self.health_check,
            methods=["GET"]
        )
    
    async def health_check(self):
        """Health check endpoint."""
        return {"status": "online", "message": "RAG API is running"}
