"""Configuration settings for the application."""

import os
from pathlib import Path
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from the project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"
load_dotenv(env_file)


@dataclass
class APIConfig:
    """API configuration settings."""
    title: str = "Window to Truth API"
    description: str = "API for queries about the Colombian conflict using RAG with Truth Commission data"
    version: str = "1.0.0"


@dataclass
class OpenAIConfig:
    """OpenAI configuration settings."""
    api_key: str
    embedding_model: str = "text-embedding-3-large"  # Use 3-large for 3072 dimensions
    completion_model: str = "gpt-4o-mini"
    embedding_dimension: int = 3072  # Match your Milvus collection


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    storage_type: str  # "sqlite" or "memory"
    sqlite_path: str
    enable_migration: bool = True


@dataclass
class MilvusConfig:
    """Milvus configuration settings."""
    host: str
    port: str
    database: str
    collection_name: str
    alternative_collection_names: List[str]


@dataclass
class AppConfig:
    """Application configuration settings."""
    top_k: int = 5


class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self):
        self._api_config = APIConfig()
        self._database_config = self._load_database_config()
        self._milvus_config = self._load_milvus_config()
        self._openai_config = self._load_openai_config()
        self._app_config = AppConfig()
        self._auto_discover_dimensions()
    
    def _auto_discover_dimensions(self):
        """Auto-discover embedding dimensions from Milvus if not explicitly set."""
        # Only auto-discover if using default dimensions and not explicitly set in env
        if not os.getenv("EMBEDDING_DIMENSION") and not os.getenv("EMBEDDING_MODEL"):
            try:
                from .dimension_discovery import DimensionDiscoveryService
                
                discovery_service = DimensionDiscoveryService(
                    host=self._milvus_config.host,
                    port=self._milvus_config.port,
                    database=self._milvus_config.database,
                    collection_names=self._milvus_config.alternative_collection_names
                )
                
                discovered_dimension = discovery_service.discover_dimension()
                recommended_model = discovery_service.get_recommended_model(discovered_dimension)
                
                print(f"Auto-discovered: dimension={discovered_dimension}, model={recommended_model}")
                
                # Update the OpenAI config with discovered values
                self._openai_config.embedding_dimension = discovered_dimension
                self._openai_config.embedding_model = recommended_model
                
            except Exception as e:
                print(f"Auto-discovery failed, using defaults: {e}")
    
    def _load_openai_config(self) -> OpenAIConfig:
        """Load OpenAI configuration from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        return OpenAIConfig(
            api_key=api_key,
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
            completion_model=os.getenv("COMPLETION_MODEL", "gpt-4o-mini"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        )
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            storage_type=os.getenv("STORAGE_TYPE", "sqlite"),
            sqlite_path=os.getenv("SQLITE_PATH", "data/chat_sessions.db"),
            enable_migration=os.getenv("ENABLE_MIGRATION", "true").lower() == "true"
        )
    
    def _load_milvus_config(self) -> MilvusConfig:
        """Load Milvus configuration from environment."""
        host = os.getenv("MILVUS_HOST", "milvus")
        port = os.getenv("MILVUS_PORT", "19530")
        database = "colombia_data_qaps"
        collection_name = "source_abstract"
        
        alternative_names = [
            "source_abstract",
            "colombia_data_qaps.source_abstract",
            f"{database}.{collection_name}",
            f"default_{collection_name}"
        ]
        
        return MilvusConfig(
            host=host,
            port=port,
            database=database,
            collection_name=collection_name,
            alternative_collection_names=alternative_names
        )
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._database_config
    
    @property
    def api(self) -> APIConfig:
        """Get API configuration."""
        return self._api_config
    
    @property
    def openai(self) -> OpenAIConfig:
        """Get OpenAI configuration."""
        return self._openai_config
    
    @property
    def milvus(self) -> MilvusConfig:
        """Get Milvus configuration."""
        return self._milvus_config
    
    @property
    def app(self) -> AppConfig:
        """Get application configuration."""
        return self._app_config


# Global configuration instance
config_service = ConfigService()
