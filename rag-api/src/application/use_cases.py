"""Use cases for the RAG API application."""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..domain.entities import ChatSession, Message, Question, ChatResponse
from ..domain.ports import (
    ChatSessionRepository, 
    VectorDatabase, 
    EmbeddingService, 
    LLMService, 
    RAGContextBuilder,
    TimestampService
)


class ChatSessionUseCase:
    """Use case for managing chat sessions."""
    
    def __init__(
        self, 
        chat_repository: ChatSessionRepository,
        timestamp_service: TimestampService
    ):
        self._chat_repository = chat_repository
        self._timestamp_service = timestamp_service
    
    async def create_chat_session(self, title: str) -> ChatSession:
        """Create a new chat session."""
        chat_id = uuid4()
        current_time = datetime.fromisoformat(self._timestamp_service.get_current_timestamp())
        
        chat_session = ChatSession(
            id=chat_id,
            title=title,
            messages=[],
            created_at=current_time,
            updated_at=current_time
        )
        
        return await self._chat_repository.save(chat_session)
    
    async def get_chat_session(self, chat_id: UUID) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        return await self._chat_repository.find_by_id(chat_id)
    
    async def list_chat_sessions(self) -> List[ChatSession]:
        """List all chat sessions."""
        return await self._chat_repository.find_all()
    
    async def delete_chat_session(self, chat_id: UUID) -> bool:
        """Delete a chat session."""
        return await self._chat_repository.delete(chat_id)


class QuestionAnsweringUseCase:
    """Use case for processing questions and generating answers."""
    
    def __init__(
        self,
        chat_repository: ChatSessionRepository,
        vector_db: VectorDatabase,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
        context_builder: RAGContextBuilder,
        timestamp_service: TimestampService
    ):
        self._chat_repository = chat_repository
        self._vector_db = vector_db
        self._embedding_service = embedding_service
        self._llm_service = llm_service
        self._context_builder = context_builder
        self._timestamp_service = timestamp_service
    
    async def process_question(
        self, 
        question: Question, 
        use_tools: bool = True,
        top_k: int = 5
    ) -> Message:
        """Process a question and generate an answer."""
        # Get the chat session
        chat_session = await self._chat_repository.find_by_id(question.chat_id)
        if not chat_session:
            raise ValueError(f"Chat session {question.chat_id} not found")
        
        # Add user message to chat
        current_time = datetime.fromisoformat(self._timestamp_service.get_current_timestamp())
        user_message = Message(
            content=question.text,
            is_bot=False,
            timestamp=current_time
        )
        chat_session.messages.append(user_message)
        
        try:
            # Prepare chat history
            chat_history = [
                {"content": msg.content, "is_bot": msg.is_bot}
                for msg in chat_session.messages[-10:]  # Last 10 messages
            ]
            
            if use_tools:
                # Use tool-based approach
                tool_response = await self._llm_service.generate_answer_with_tools(
                    question.text, chat_history
                )
                
                # Create response message
                bot_message = Message(
                    content=tool_response["content"],
                    is_bot=True,
                    timestamp=current_time,
                    references=tool_response.get("references", [])
                )
            else:
                # Use traditional RAG approach
                # Generate embedding for the question
                embedding = await self._embedding_service.generate_embedding(question.text)
                
                # Search for similar documents
                documents = await self._vector_db.search_similar_documents(embedding, top_k)
                
                # Build context
                rag_context = await self._context_builder.build_context(documents, question.text)
                
                # Generate answer
                answer = await self._llm_service.generate_answer(
                    question.text, 
                    rag_context.context_text, 
                    chat_history
                )
                
                # Create response message
                bot_message = Message(
                    content=answer,
                    is_bot=True,
                    timestamp=current_time,
                    references=[ref.__dict__ for ref in rag_context.references]
                )
            
            # Add bot message to chat
            chat_session.messages.append(bot_message)
            chat_session.updated_at = current_time
            
            # Save updated chat session
            await self._chat_repository.save(chat_session)
            
            return bot_message
            
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error processing question: {str(e)}"
            print(error_message)
            
            # Create error response
            error_response = Message(
                content="I apologize, but I couldn't process your question. Please try again.",
                is_bot=True,
                timestamp=current_time
            )
            
            chat_session.messages.append(error_response)
            await self._chat_repository.save(chat_session)
            
            raise Exception(error_message)
