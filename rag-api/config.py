import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configurations
API_TITLE = "Window to Truth API"
API_DESCRIPTION = "API for queries about the Colombian conflict using RAG (Retrieval-Augmented Generation) with data from the Truth Commission"
API_VERSION = "1.0.0"

# OpenAI configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # Embedding model that generates 1536-dimensional vectors
COMPLETION_MODEL = "gpt-3.5-turbo-0125"     # Specific and stable version
EMBEDDING_DIMENSION = 1536                  # Dimension of the embedding vector used in Milvus

# Milvus configurations
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_DATABASE = "colombia_data_qaps"  # Database name
ABSTRACT_COLLECTION = "source_abstract"  # Collection name to use

# List of alternative collection names to try if main connection fails
ALTERNATIVE_COLLECTION_NAMES = [
    "source_abstract",                           # Simple name
    "colombia_data_qaps.source_abstract",        # With explicit database prefix
    MILVUS_DATABASE + "." + ABSTRACT_COLLECTION, # Dynamic construction
    "default_" + ABSTRACT_COLLECTION             # Some versions use default_ prefix
]

# Other parameters
TOP_K = 5  # Number of documents to retrieve
