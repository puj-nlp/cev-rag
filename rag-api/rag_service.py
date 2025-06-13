import json
from typing import List, Dict, Any
from openai import OpenAI
from pymilvus import connections, Collection, utility, db
import config

# Inicializar el cliente de OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Conectar a Milvus
connections.connect(
    alias="default", 
    host=config.MILVUS_HOST,
    port=config.MILVUS_PORT
)

print("Conectado a Milvus exitosamente")

# Verificar disponibilidad de bases de datos e intentar seleccionar la base de datos correcta
try:
    # Intentar listar las bases de datos disponibles
    databases = utility.list_database()
    print(f"Bases de datos disponibles: {databases}")
    
    if config.MILVUS_DATABASE in databases:
        print(f"Base de datos {config.MILVUS_DATABASE} encontrada")
        # Intentar seleccionar la base de datos específica
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Base de datos {config.MILVUS_DATABASE} seleccionada correctamente")
        except Exception as e:
            print(f"Error al seleccionar la base de datos {config.MILVUS_DATABASE}: {e}")
    else:
        print(f"¡ADVERTENCIA! Base de datos {config.MILVUS_DATABASE} no encontrada")
except Exception as e:
    print(f"Error al listar bases de datos: {e}")
    print("La versión de PyMilvus o Milvus instalada puede no soportar múltiples bases de datos")

def get_embedding(text: str, model: str = config.EMBEDDING_MODEL) -> List[float]:
    """
    Obtiene el embedding de un texto usando OpenAI.
    
    Args:
        text: Texto para el cual se generará el embedding
        model: Modelo de embedding a utilizar
        
    Returns:
        List[float]: Vector de embedding
    """
    # Asegurarse de que el texto no es None o vacío
    if not text:
        text = "Consulta vacía"
    
    # Limpiar el texto
    text = text.replace("\n", " ").strip()
    
    try:
        print(f"Generando embedding con modelo: {model}")
        # Usar el formato correcto para la API de OpenAI v1.0+
        response = client.embeddings.create(
            input=text,  # String simple, no lista
            model=model
        )
        embedding = response.data[0].embedding
        print(f"Embedding generado con dimensión: {len(embedding)}")
        return embedding
    except Exception as e:
        print(f"Error al generar embedding: {e}")
        print(f"Usando fallback con dimensión: {config.EMBEDDING_DIMENSION}")
        # Retornar un vector de ceros como fallback
        # Usar la dimensión configurada en config.py
        return [0.0] * config.EMBEDDING_DIMENSION

def connect_to_milvus_database():
    """
    Verifica la conexión a Milvus.
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        # Verificar que la conexión está activa
        connections.get_connection_addr("default")
        print("Conexión a Milvus verificada")
        return True
    except Exception as e:
        print(f"Error al verificar conexión a Milvus: {e}")
        return False

def get_abstract_collection() -> Collection:
    """
    Obtiene la colección source_abstract.
    
    Returns:
        Collection: Colección de Milvus
    """
    try:
        # Intentar seleccionar la base de datos correcta primero
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Base de datos {config.MILVUS_DATABASE} seleccionada para buscar colección")
        except Exception as e:
            print(f"Nota: No se pudo seleccionar la base de datos {config.MILVUS_DATABASE}: {e}")
            print("Esto es normal en versiones antiguas de Milvus o en Milvus Standalone")
        
        # Lista todas las colecciones disponibles para diagnóstico
        from pymilvus import utility
        collections = utility.list_collections()
        print(f"Colecciones disponibles después de seleccionar base de datos: {collections}")
        
        # Buscar formato de colección más probable
        collection_candidates = [
            config.ABSTRACT_COLLECTION,                               # source_abstract
            f"{config.MILVUS_DATABASE}.{config.ABSTRACT_COLLECTION}", # colombia_data_qaps.source_abstract
        ]
        
        # Si la colección aparece en la lista, usar ese nombre exacto
        collection_found = False
        for collection in collections:
            if collection in collection_candidates or collection == config.ABSTRACT_COLLECTION:
                print(f"Colección encontrada exactamente como: {collection}")
                collection_candidates.insert(0, collection)  # Poner esta al principio
                collection_found = True
        
        if not collection_found:
            print(f"⚠️ ADVERTENCIA: No se encontró la colección en la lista de colecciones disponibles")
        
        # Intentar todos los formatos de colección posibles
        for collection_name in collection_candidates:
            try:
                print(f"Intentando acceder a la colección: {collection_name}")
                collection = Collection(name=collection_name)
                print(f"Colección accedida exitosamente: {collection_name}")
                
                # Verificar si la colección tiene datos
                entity_count = collection.num_entities
                print(f"Número de entidades en {collection_name}: {entity_count}")
                
                if entity_count == 0:
                    print(f"⚠️ ADVERTENCIA: La colección {collection_name} está vacía ⚠️")
                    print("La colección existe pero no contiene datos. Verifique que se hayan cargado los datos correctamente.")
                    # A pesar de estar vacía, devolvemos la colección para que el error sea más específico después
                
                # Verificar si la colección está cargada o cargarla
                try:
                    collection.load()
                    print(f"Colección {collection_name} cargada exitosamente")
                except Exception as load_err:
                    print(f"Aviso al cargar la colección {collection_name}: {load_err}")
                
                return collection
            except Exception as e:
                print(f"Error al acceder a la colección {collection_name}: {e}")
                continue
        
        # Si llegamos aquí, intentemos una vez más con un enfoque diferente
        try:
            # Si tenemos la base de datos correcta, intenta forzar la conexión completa
            connection_string = f"{config.MILVUS_DATABASE}/{config.ABSTRACT_COLLECTION}"
            print(f"Intentando último enfoque con: {connection_string}")
            collection = Collection(name=connection_string)
            print(f"Colección accedida exitosamente con conexión completa: {connection_string}")
            return collection
        except Exception as e:
            print(f"Error en el último intento: {e}")
            
        # Si llegamos aquí, ninguno de los intentos anteriores tuvo éxito
        raise Exception(f"No se pudo acceder a ninguna colección. Formatos intentados: {collection_candidates}")
    except Exception as e:
        print(f"Error general al obtener colección: {e}")
        raise

def get_documents_from_query(query_vec: List[float], collection: Collection, top_k: int = config.TOP_K) -> List[Dict]:
    """
    Busca documentos relevantes en una colección de Milvus.
    
    Args:
        query_vec: Vector de embedding de la consulta
        collection: Colección de Milvus donde buscar
        top_k: Número de documentos a recuperar
        
    Returns:
        List[Dict]: Lista de documentos relevantes
    """
    # Verificar primero si la colección tiene datos
    entity_count = collection.num_entities
    if entity_count == 0:
        raise Exception(f"La colección {collection.name} está vacía. No hay documentos para buscar. Asegúrese de que se hayan cargado correctamente los datos en la colección.")

    search_params = {
        "metric_type": "COSINE",
        "params": {"nprobe": 10}
    }
    
    # Asegurarse de que la colección esté cargada
    try:
        collection.load()
        print(f"Colección {collection.name} cargada exitosamente")
    except Exception as e:
        print(f"Aviso al cargar la colección: {e}")
    
    # Detectar qué campos están disponibles en la colección
    collection_info = collection.schema
    field_names = [field.name for field in collection_info.fields]
    output_fields = []
    
    # Detectar la dimensión del vector en la colección
    embedding_field = next((field for field in collection_info.fields if field.name == "embedding"), None)
    collection_vector_dim = embedding_field.dim if embedding_field else None
    
    # Verificar si las dimensiones coinciden
    if collection_vector_dim is not None and len(query_vec) != collection_vector_dim:
        print(f"¡ADVERTENCIA! Dimensión del vector de consulta ({len(query_vec)}) no coincide con la colección ({collection_vector_dim})")
        # Ajustar dinámicamente el tamaño del vector si es necesario
        if len(query_vec) > collection_vector_dim:
            # Truncar
            query_vec = query_vec[:collection_vector_dim]
            print(f"Vector truncado a {collection_vector_dim} dimensiones")
        else:
            # Expandir con ceros
            query_vec = query_vec + [0.0] * (collection_vector_dim - len(query_vec))
            print(f"Vector expandido a {collection_vector_dim} dimensiones")
    
    # Configurar campos de salida basados en el esquema de la colección
    if "text" in field_names:
        output_fields.extend(["text", "title", "type", "link", "source_id", "page"])
    elif "content" in field_names:
        output_fields.extend(["content", "metadata"])
    else:
        # Añadir todos los campos excepto embedding e id
        output_fields = [f for f in field_names if f not in ["embedding", "id"]]
    
    results = collection.search(
        data=[query_vec],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=output_fields
    )
    
    documents = []
    for hit in results[0]:
        doc_dict = hit.entity.to_dict()
        
        # Estructura de documento según el esquema detectado
        if "text" in doc_dict:
            # Esquema nuevo con text, title, type, etc. (source_abstract)
            content = doc_dict.get('text', '')
            metadata = {
                "source_id": doc_dict.get('source_id', ''),
                "link": doc_dict.get('link', ''),
                "page": doc_dict.get('page', 0),
                "title": doc_dict.get('title', ''),
                "type": doc_dict.get('type', '')
            }
            
            # Agregar datos dinámicos si existen
            if "dynamic_field" in doc_dict and doc_dict["dynamic_field"]:
                try:
                    # El campo dynamic_field ya es JSON en Milvus, no necesita parsing
                    dynamic_data = doc_dict["dynamic_field"]
                    metadata.update(dynamic_data)
                except Exception as e:
                    print(f"Error al procesar dynamic_field: {e}")
        else:
            # Esquema antiguo con content y metadata
            content = doc_dict.get('content', '')
            metadata_str = doc_dict.get('metadata', '{}')
            try:
                metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
            except Exception as e:
                print(f"Error al procesar metadata: {e}")
                metadata = {}
        
        documents.append({
            "content": content,
            "metadata": metadata,
            "score": hit.score
        })
    
    return documents

def generate_answer(question: str, context: str, chat_history: List[Dict]) -> str:
    """
    Genera una respuesta utilizando OpenAI con el contexto recuperado.
    
    Args:
        question: Pregunta del usuario
        context: Contexto relevante para responder
        chat_history: Historial de la conversación
        
    Returns:
        str: Respuesta generada
    """
    messages = [
        {"role": "system", "content": "Eres un asistente experto en el conflicto colombiano y la Comisión de la Verdad. Responde preguntas basándote en la información proporcionada. Si la información proporcionada no es suficiente para responder la pregunta con certeza, indica que no tienes suficiente información y sugiere qué información adicional podría ser útil. Trata los temas con sensibilidad y respeto, reconociendo que involucran experiencias humanas difíciles relacionadas con el conflicto."}
    ]
    
    # Añadir historial de chat
    for message in chat_history:
        role = "assistant" if message["is_bot"] else "user"
        messages.append({"role": role, "content": message["content"]})
    
    # Añadir contexto y pregunta actual
    messages.append({"role": "user", "content": f"Contexto: {context}\n\nPregunta: {question}"})
    
    response = client.chat.completions.create(
        model=config.COMPLETION_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content
