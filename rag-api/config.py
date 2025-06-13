import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones de la API
API_TITLE = "Ventana a la Verdad API"
API_DESCRIPTION = "API para consultas sobre el conflicto colombiano usando RAG (Retrieval-Augmented Generation) con datos de la Comisión de la Verdad"
API_VERSION = "1.0.0"

# Configuraciones de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # Modelo de embeddings que genera vectores de 1536 dimensiones
COMPLETION_MODEL = "gpt-3.5-turbo-0125"     # Versión específica y estable
EMBEDDING_DIMENSION = 1536                  # Dimensión del vector de embedding utilizado en Milvus

# Configuraciones de Milvus
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_DATABASE = "colombia_data_qaps"  # Nombre de la base de datos
ABSTRACT_COLLECTION = "source_abstract"  # Nombre de la colección a utilizar

# Lista de nombres alternativos para intentar si falla la conexión principal
ALTERNATIVE_COLLECTION_NAMES = [
    "source_abstract",                           # Nombre simple
    "colombia_data_qaps.source_abstract",        # Con prefijo de base de datos explícito
    MILVUS_DATABASE + "." + ABSTRACT_COLLECTION, # Construcción dinámica
    "default_" + ABSTRACT_COLLECTION             # Algunas versiones usan prefijo default_
]

# Otros parámetros
TOP_K = 5  # Número de documentos a recuperar
