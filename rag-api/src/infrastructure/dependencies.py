"""Dependency injection container for the application."""

from functools import lru_cache

from ..domain.ports import (
    ChatSessionRepository,
    VectorDatabase,
    EmbeddingService,
    LLMService,
    RAGContextBuilder,
    TimestampService
)
from ..application.use_cases import ChatSessionUseCase, QuestionAnsweringUseCase
from ..adapters.repositories.memory_chat_repository import InMemoryChatSessionRepository
from ..adapters.repositories.milvus_vector_db import MilvusVectorDatabase
from ..adapters.external.openai_services import OpenAIEmbeddingService, OpenAILLMService
from .services import DefaultRAGContextBuilder, DefaultTimestampService
from .config import config_service


# Repository instances
@lru_cache()
def get_chat_repository() -> ChatSessionRepository:
    """Get chat session repository instance."""
    return InMemoryChatSessionRepository()


@lru_cache()
def get_vector_database() -> VectorDatabase:
    """Get vector database instance."""
    milvus_config = config_service.milvus
    return MilvusVectorDatabase(
        host=milvus_config.host,
        port=milvus_config.port,
        database=milvus_config.database,
        collection_name=milvus_config.collection_name,
        alternative_names=milvus_config.alternative_collection_names
    )


# Service instances
@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get embedding service instance."""
    openai_config = config_service.openai
    return OpenAIEmbeddingService(
        api_key=openai_config.api_key,
        model=openai_config.embedding_model,
        expected_dimension=openai_config.embedding_dimension
    )


@lru_cache()
def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    openai_config = config_service.openai
    return OpenAILLMService(
        api_key=openai_config.api_key,
        model=openai_config.completion_model
    )


@lru_cache()
def get_context_builder() -> RAGContextBuilder:
    """Get RAG context builder instance."""
    return DefaultRAGContextBuilder()


@lru_cache()
def get_timestamp_service() -> TimestampService:
    """Get timestamp service instance."""
    return DefaultTimestampService()


# Use case instances
@lru_cache()
def get_chat_use_case() -> ChatSessionUseCase:
    """Get chat session use case instance."""
    return ChatSessionUseCase(
        chat_repository=get_chat_repository(),
        timestamp_service=get_timestamp_service()
    )


@lru_cache()
def get_question_answering_use_case() -> QuestionAnsweringUseCase:
    """Get question answering use case instance."""
    return QuestionAnsweringUseCase(
        chat_repository=get_chat_repository(),
        vector_db=get_vector_database(),
        embedding_service=get_embedding_service(),
        llm_service=get_llm_service(),
        context_builder=get_context_builder(),
        timestamp_service=get_timestamp_service()
    )
