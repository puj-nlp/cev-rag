import json
from typing import List, Dict, Any
from openai import OpenAI
from pymilvus import connections, Collection, utility, db
import config

# Initialize OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Connect to Milvus
connections.connect(
    alias="default", 
    host=config.MILVUS_HOST,
    port=config.MILVUS_PORT
)

print("Successfully connected to Milvus")

# Función para diagnosticar la estructura de la colección Milvus
def diagnose_milvus_collection():
    try:
        print("\n--- DIAGNÓSTICO DE MILVUS ---")
        
        # Listar todas las colecciones
        from pymilvus import utility
        collections = utility.list_collections()
        print(f"Colecciones disponibles: {collections}")
        
        # Tratar de acceder a la colección principal
        try:
            collection_name = config.ABSTRACT_COLLECTION
            print(f"\nVerificando colección: {collection_name}")
            
            collection = Collection(name=collection_name)
            
            # Obtener información del schema
            schema = collection.schema
            print(f"Schema de la colección: {schema}")
            
            # Listar campos
            fields = [field.name for field in schema.fields]
            print(f"Campos disponibles: {fields}")
            
            # Verificar cantidad de datos
            entity_count = collection.num_entities
            print(f"Número de entidades: {entity_count}")
            
            # Si hay datos, intentar obtener algunas muestras
            if entity_count > 0:
                print("\nIntentando obtener muestras de datos:")
                
                # Cargar la colección
                collection.load()
                
                # Realizar una búsqueda aleatoria
                import random
                random_vec = [random.random() for _ in range(config.EMBEDDING_DIMENSION)]
                
                # Usar todos los campos excepto embedding
                output_fields = [f for f in fields if f != "embedding"]
                print(f"Campos a consultar: {output_fields}")
                
                # Hacer una búsqueda
                results = collection.search(
                    data=[random_vec],
                    anns_field="embedding",
                    param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                    limit=3,
                    output_fields=output_fields
                )
                
                # Mostrar resultados
                print(f"Resultados encontrados: {len(results[0])}")
                for i, hit in enumerate(results[0]):
                    print(f"\nDocumento {i+1}:")
                    doc_dict = hit.entity.to_dict()
                    print(f"Campos disponibles en el resultado: {list(doc_dict.keys())}")
                    
                    # Mostrar algunos valores
                    for key, value in doc_dict.items():
                        # Limitar la longitud para campos largos
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  - {key}: {value[:100]}...")
                        else:
                            print(f"  - {key}: {value}")
            
        except Exception as e:
            print(f"Error verificando colección {collection_name}: {e}")
            import traceback
            print(traceback.format_exc())
    
    except Exception as e:
        print(f"Error en diagnóstico general: {e}")
        import traceback
        print(traceback.format_exc())

# Ejecutar diagnóstico al inicio
diagnose_milvus_collection()

# Verify database availability and try to select the correct database
try:
    # Try to list available databases
    databases = utility.list_database()
    print(f"Available databases: {databases}")
    
    if config.MILVUS_DATABASE in databases:
        print(f"Database {config.MILVUS_DATABASE} found")
        # Try to select the specific database
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Database {config.MILVUS_DATABASE} selected successfully")
        except Exception as e:
            print(f"Error selecting database {config.MILVUS_DATABASE}: {e}")
    else:
        print(f"WARNING! Database {config.MILVUS_DATABASE} not found")
except Exception as e:
    print(f"Error listing databases: {e}")
    print("The installed PyMilvus or Milvus version may not support multiple databases")

def get_embedding(text: str, model: str = config.EMBEDDING_MODEL) -> List[float]:
    """
    Gets the embedding of a text using OpenAI.
    
    Args:
        text: Text for which the embedding will be generated
        model: Embedding model to use
        
    Returns:
        List[float]: Embedding vector
    """
    # Make sure the text is not None or empty
    if not text:
        text = "Empty query"
    
    # Clean the text
    text = text.replace("\n", " ").strip()
    
    try:
        print(f"Generating embedding with model: {model}")
        # Use correct format for OpenAI API v1.0+
        response = client.embeddings.create(
            input=text,  # Simple string, not a list
            model=model
        )
        embedding = response.data[0].embedding
        print(f"Embedding generated with dimension: {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        print(f"Using fallback with dimension: {config.EMBEDDING_DIMENSION}")
        # Return a zero vector as fallback
        # Use dimension configured in config.py
        return [0.0] * config.EMBEDDING_DIMENSION

def connect_to_milvus_database():
    """
    Verifies the connection to Milvus.
    
    Returns:
        bool: True if the connection is successful, False otherwise
    """
    try:
        # Verify that the connection is active
        connections.get_connection_addr("default")
        print("Milvus connection verified")
        return True
    except Exception as e:
        print(f"Error verifying Milvus connection: {e}")
        return False

def get_abstract_collection() -> Collection:
    """
    Gets the source_abstract collection.
    
    Returns:
        Collection: Milvus collection
    """
    try:
        # Try to select the correct database first
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Database {config.MILVUS_DATABASE} selected to search for collection")
        except Exception as e:
            print(f"Note: Could not select database {config.MILVUS_DATABASE}: {e}")
            print("This is normal in older versions of Milvus or in Milvus Standalone")
        
        # List all available collections for diagnostic
        from pymilvus import utility
        collections = utility.list_collections()
        print(f"Available collections after selecting database: {collections}")
        
        # Find most likely collection format
        collection_candidates = [
            config.ABSTRACT_COLLECTION,                               # source_abstract
            f"{config.MILVUS_DATABASE}.{config.ABSTRACT_COLLECTION}", # colombia_data_qaps.source_abstract
        ]
        
        # If the collection appears in the list, use that exact name
        collection_found = False
        for collection in collections:
            if collection in collection_candidates or collection == config.ABSTRACT_COLLECTION:
                print(f"Collection found exactly as: {collection}")
                collection_candidates.insert(0, collection)  # Put this at the beginning
                collection_found = True
        
        if not collection_found:
            print(f"⚠️ WARNING: Collection not found in the list of available collections")
        
        # Try all possible collection formats
        for collection_name in collection_candidates:
            try:
                print(f"Attempting to access collection: {collection_name}")
                collection = Collection(name=collection_name)
                print(f"Collection accessed successfully: {collection_name}")
                
                # Check if the collection has data
                entity_count = collection.num_entities
                print(f"Number of entities in {collection_name}: {entity_count}")
                
                if entity_count == 0:
                    print(f"⚠️ WARNING: Collection {collection_name} is empty ⚠️")
                    print("The collection exists but contains no data. Verify that the data has been loaded correctly.")
                    # Despite being empty, we return the collection so that the error is more specific later
                
                # Check if the collection is loaded or load it
                try:
                    collection.load()
                    print(f"Collection {collection_name} loaded successfully")
                except Exception as load_err:
                    print(f"Note when loading collection {collection_name}: {load_err}")
                
                return collection
            except Exception as e:
                print(f"Error accessing collection {collection_name}: {e}")
                continue
        
        # If we get here, let's try one more time with a different approach
        try:
            # If we have the correct database, try to force the complete connection
            connection_string = f"{config.MILVUS_DATABASE}/{config.ABSTRACT_COLLECTION}"
            print(f"Trying last approach with: {connection_string}")
            collection = Collection(name=connection_string)
            print(f"Collection accessed successfully with complete connection: {connection_string}")
            return collection
        except Exception as e:
            print(f"Error in last attempt: {e}")
            
        # If we get here, none of the previous attempts were successful
        raise Exception(f"Could not access any collection. Formats tried: {collection_candidates}")
    except Exception as e:
        print(f"General error getting collection: {e}")
        raise

def get_documents_from_query(query_vec: List[float], collection: Collection, top_k: int = config.TOP_K) -> List[Dict]:
    """
    Searches for relevant documents in a Milvus collection.
    
    Args:
        query_vec: Query embedding vector
        collection: Milvus collection to search in
        top_k: Number of documents to retrieve
        
    Returns:
        List[Dict]: List of relevant documents
    """
    # First check if the collection has data
    entity_count = collection.num_entities
    if entity_count == 0:
        raise Exception(f"The collection {collection.name} is empty. There are no documents to search for. Make sure the data has been loaded correctly into the collection.")

    search_params = {
        "metric_type": "COSINE",
        "params": {"nprobe": 10}
    }
    
    # Make sure the collection is loaded
    try:
        collection.load()
        print(f"Collection {collection.name} loaded successfully")
    except Exception as e:
        print(f"Note when loading collection: {e}")
    
    # Detect which fields are available in the collection
    collection_info = collection.schema
    field_names = [field.name for field in collection_info.fields]
    output_fields = []
    
    # Detect the vector dimension in the collection
    embedding_field = next((field for field in collection_info.fields if field.name == "embedding"), None)
    collection_vector_dim = embedding_field.dim if embedding_field else None
    
    # Check if the dimensions match
    if collection_vector_dim is not None and len(query_vec) != collection_vector_dim:
        print(f"WARNING! Query vector dimension ({len(query_vec)}) does not match the collection ({collection_vector_dim})")
        # Dynamically adjust the vector size if necessary
        if len(query_vec) > collection_vector_dim:
            # Truncate
            query_vec = query_vec[:collection_vector_dim]
            print(f"Vector truncated to {collection_vector_dim} dimensions")
        else:
            # Expand with zeros
            query_vec = query_vec + [0.0] * (collection_vector_dim - len(query_vec))
            print(f"Vector expanded to {collection_vector_dim} dimensions")
    
    # Configure output fields based on the schema we know exists in Milvus
    print(f"Detectando campos en la colección. Campos disponibles: {field_names}")
    
    # Para la colección source_abstract, sabemos que estos son los campos que necesitamos
    expected_fields = ["id", "text", "title", "type", "link", "source_id", "page"]
    
    # Filtrar solo los campos que existen en la colección
    output_fields = [field for field in expected_fields if field in field_names and field != "id"]
    
    # Si por alguna razón no se encontraron los campos esperados, incluir todos excepto embedding
    if not output_fields:
        print("ADVERTENCIA: No se encontraron los campos esperados. Incluyendo todos excepto 'embedding'")
        output_fields = [f for f in field_names if f not in ["embedding"]]
    
    print(f"Campos de salida finales: {output_fields}")
    
    print(f"Ejecutando búsqueda en Milvus con los siguientes parámetros:")
    print(f"  - Collection: {collection.name}")
    print(f"  - Vector dimension: {len(query_vec)}")
    print(f"  - Output fields: {output_fields}")
    print(f"  - Top-k: {top_k}")
    
    results = collection.search(
        data=[query_vec],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=output_fields
    )
    
    # Debug: Verifiquemos la estructura de los resultados
    print(f"Tipo de resultados: {type(results)}")
    print(f"Número de resultados: {len(results)}")
    print(f"Estructura del primer conjunto de resultados: {type(results[0])}")
    print(f"Número de hits en primer conjunto: {len(results[0])}")
    
    print(f"Campos disponibles en la colección: {field_names}")
    print(f"Campos de salida configurados: {output_fields}")
    
    documents = []
    for hit in results[0]:
        print(f"Raw hit data: {hit}")
        doc_dict = hit.entity.to_dict()
        print(f"Document dictionary from Milvus: {doc_dict}")
        
        # Basado en el esquema conocido de source_abstract
        # El campo principal de contenido es 'text'
        content = doc_dict.get('text', '')
        
        # Si el campo text está vacío, verificar si hay otros campos con contenido
        if not content:
            print("ADVERTENCIA: Campo 'text' vacío, comprobando valores en todos los campos")
            # Mostrar todos los campos y sus valores
            for field_name, field_value in doc_dict.items():
                if field_name != 'embedding' and field_value:
                    print(f"  - Campo '{field_name}' tiene valor: {str(field_value)[:50]}...")
                    
        # Estructurar los metadatos
        metadata = {
            "source_id": doc_dict.get('source_id', ''),
            "link": doc_dict.get('link', ''),
            "page": doc_dict.get('page', 0),
            "title": doc_dict.get('title', ''),
            "type": doc_dict.get('type', '')
        }
        
        # Depurar valores
        print(f"Contenido extraído: {str(content)[:100]}..." if content else "Contenido: VACÍO")
        print(f"Metadatos extraídos: {metadata}")
        
        # Si el contenido sigue vacío después de todas las verificaciones,
        # usar el título como último recurso
        if not content and doc_dict.get('title'):
            content = f"Título del documento: {doc_dict.get('title')}"
            print(f"Usando título como contenido: {content}")
        
        # Asegurarse de que tenemos algún contenido
        if not content:
            content = "No se pudo extraer contenido de este documento."
            print("ADVERTENCIA: No se pudo obtener contenido del documento")
        
        # Añadir el documento procesado a la lista de resultados
        documents.append({
            "content": content,
            "metadata": metadata,
            "score": hit.score,
            # Incluir también los campos originales para depuración
            "original_fields": doc_dict
        })
        
        # La adición del documento se hace en el bloque anterior
    
    return documents

def generate_answer(question: str, context: str, chat_history: List[Dict]) -> str:
    """
    Generates an answer using OpenAI with the retrieved context.
    
    Args:
        question: User's question
        context: Relevant context for answering
        chat_history: Conversation history
        
    Returns:
        str: Generated answer with academic formatting and references
    """
    messages = [
        {"role": "system", "content": """Eres un investigador académico especializado en el conflicto colombiano y la Comisión de la Verdad. Genera respuestas detalladas y rigurosas basadas en la información proporcionada. Sigue estas pautas específicas:

1. FORMATO ACADÉMICO ESTRICTO:
   - Comienza con una "Introducción" clara que presente el tema general.
   - Utiliza subtítulos en negrita para organizar la información por regiones, temas o conceptos.
   - Cuando menciones datos específicos, SIEMPRE incluye la cita en formato parentético al final de la oración: (Fuente: [Título del documento], Página: [número]).
   - Termina con una "Conclusión" que sintetice los puntos principales.

2. CITAS Y REFERENCIAS:
   - Cita ESPECÍFICAMENTE páginas y fuentes exactas de los documentos.
   - Usa el formato (Fuente: [Título exacto], Página: [número]) para cada cita.
   - Al final, escribe el encabezado "Referencias" para que se añada la bibliografía completa.

3. CONTENIDO Y TONO:
   - Trata los temas con rigor académico y sensibilidad debido a la naturaleza del conflicto.
   - Utiliza lenguaje preciso, objetivo y formal.
   - Proporciona detalles concretos: cifras, nombres de regiones específicas, y hechos verificables.
   - Si la información proporcionada es insuficiente, indícalo claramente y sugiere qué datos adicionales serían necesarios.

Tu respuesta debe ser estructurada, académica y rica en datos específicos, similar a un informe formal de la Comisión de la Verdad."""}
    ]
    
    # Add chat history (include only a limited amount to keep context focused)
    relevant_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    for message in relevant_history:
        role = "assistant" if message["is_bot"] else "user"
        messages.append({"role": role, "content": message["content"]})
    
    # Structure the prompt to encourage a high-quality academic response
    content_prompt = f"""
Por favor, genera una respuesta académica completa a la siguiente pregunta sobre el conflicto colombiano. 
Utiliza ÚNICAMENTE la información proporcionada en el contexto y cita apropiadamente las fuentes.

PREGUNTA:
{question}

CONTEXTO DISPONIBLE (cita estas fuentes específicamente):
{context}

INSTRUCCIONES ESPECIALES:
1. Estructura tu respuesta con una "Introducción" clara, secciones con subtítulos en negrita, y una "Conclusión".
2. IMPORTANTE: Cita las fuentes específicas usando el formato: (Fuente: [Título], Página: [número]) después de cada dato o afirmación.
3. Incluye datos concretos, nombres específicos de regiones, y cifras exactas cuando estén disponibles.
4. Al final de tu respuesta, añade el encabezado "Referencias" para indicar donde debe ir la bibliografía completa.

Tu respuesta debe ser rigurosa, bien estructurada y académicamente fundamentada.
"""
    
    messages.append({"role": "user", "content": content_prompt})
    
    response = client.chat.completions.create(
        model=config.COMPLETION_MODEL,
        messages=messages,
        temperature=0.3,  # Menor temperatura para respuestas más consistentes y precisas
        max_tokens=800    # Aumentar el límite para permitir respuestas más detalladas
    )
    
    return response.choices[0].message.content
