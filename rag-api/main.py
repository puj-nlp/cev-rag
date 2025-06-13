import json
import uuid
import datetime
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymilvus import Collection, db

import config
from models import ChatSession, Message, QuestionRequest, ChatRequest, ErrorResponse
from rag_service import get_embedding, get_abstract_collection, get_documents_from_query, generate_answer

app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION
)

# Configurar CORS para permitir solicitudes del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Verificar las colecciones de Milvus al inicio
def verify_milvus_collections():
    from pymilvus import utility, Collection, connections, db
    import time
    
    # Intentar conectar varias veces para dar tiempo al servicio Milvus para iniciar
    max_attempts = 5
    for attempt in range(max_attempts):
        # Al principio de cada intento, limpiar la configuración de colección
        # para asegurarnos de que se realiza el diagnóstico completo
        config.ABSTRACT_COLLECTION = "source_abstract"
        
        # Intentar seleccionar la base de datos correcta
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Base de datos {config.MILVUS_DATABASE} seleccionada para verificación")
        except Exception as e:
            print(f"Nota: No se pudo seleccionar la base de datos {config.MILVUS_DATABASE}: {e}")
            print("Esto es normal en versiones antiguas de Milvus o en Milvus Standalone")
        try:
            print(f"Verificando conexión a Milvus (intento {attempt+1}/{max_attempts})...")
            
            # Verificar la conexión a Milvus
            try:
                conn_status = connections.get_connection_addr("default")
                print(f"Estado de conexión Milvus: {conn_status}")
            except Exception as e:
                print(f"Error al verificar estado de conexión: {e}")
                # Intentar reconectar si hay algún problema
                connections.connect(alias="default", host=config.MILVUS_HOST, port=config.MILVUS_PORT)
            
            # Listar todas las bases de datos disponibles
            try:
                all_databases = utility.list_database()
                print(f"Bases de datos disponibles en Milvus: {all_databases}")
                
                if config.MILVUS_DATABASE not in all_databases:
                    print(f"¡ADVERTENCIA! Base de datos {config.MILVUS_DATABASE} no encontrada en: {all_databases}")
                else:
                    print(f"Base de datos {config.MILVUS_DATABASE} encontrada")
            except Exception as e:
                print(f"Error al listar bases de datos: {e}")
                print("La versión de PyMilvus o Milvus instalada puede no soportar múltiples bases de datos")
            
            # Listar todas las colecciones disponibles
            try:
                all_collections = utility.list_collections()
                print(f"Colecciones disponibles en Milvus: {all_collections}")
                
                # Buscar la colección por todos los nombres posibles
                target_found = False
                for collection_name in config.ALTERNATIVE_COLLECTION_NAMES:
                    if collection_name in all_collections:
                        print(f"¡Colección encontrada con nombre: {collection_name}!")
                        config.ABSTRACT_COLLECTION = collection_name
                        target_found = True
                        break
                
                if not target_found:
                    print(f"ADVERTENCIA: No se encontró la colección en ninguna variante de nombre: {config.ALTERNATIVE_COLLECTION_NAMES}")
            except Exception as e:
                print(f"Error al listar colecciones: {e}")
            
            # Intentar verificar y acceder a la colección con cada formato de nombre posible
            collection_candidates = config.ALTERNATIVE_COLLECTION_NAMES + [f"{config.MILVUS_DATABASE}.{config.ABSTRACT_COLLECTION}"]
            for collection_name in collection_candidates:
                try:
                    has_collection = utility.has_collection(collection_name)
                    print(f"Colección {collection_name} existe: {has_collection}")
                    
                    if has_collection:
                        try:
                            print(f"Intentando acceder a la colección: {collection_name}")
                            abstract_collection = Collection(name=collection_name)
                            schema = abstract_collection.schema
                            embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
                            if embedding_field:
                                print(f"Dimensión de embedding en {collection_name}: {embedding_field.dim}")
                                if embedding_field.dim != config.EMBEDDING_DIMENSION:
                                    print(f"ADVERTENCIA: La dimensión configurada ({config.EMBEDDING_DIMENSION}) no coincide con la colección ({embedding_field.dim})")
                                    # Actualizar la dimensión configurada para que coincida con la colección
                                    config.EMBEDDING_DIMENSION = embedding_field.dim
                                    print(f"Actualizada la dimensión configurada a: {config.EMBEDDING_DIMENSION}")
                                
                                # Contar entidades para verificar que hay datos
                                entity_count = abstract_collection.num_entities
                                print(f"Número de entidades en {collection_name}: {entity_count}")
                                
                                # Si encontramos la colección y tiene datos, actualizar el nombre en la configuración
                                if entity_count > 0:
                                    config.ABSTRACT_COLLECTION = collection_name
                                    print(f"Usando colección {collection_name} con {entity_count} entidades")
                                    break
                        except Exception as e:
                            print(f"Error al verificar {collection_name}: {e}")
                except Exception as e:
                    print(f"Error al verificar existencia de {collection_name}: {e}")
            
            # Si llegamos aquí, hemos podido conectar correctamente
            break
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Error al verificar conexión a Milvus: {e}")
                print(f"Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print(f"No se pudo verificar la conexión a Milvus después de {max_attempts} intentos.")

# Ejecutar la verificación en segundo plano para no bloquear el inicio de la API
import threading
threading.Thread(target=verify_milvus_collections, daemon=True).start()

# Almacenamiento en memoria para chats (en producción usaríamos una base de datos)
chats: Dict[str, ChatSession] = {}


def get_current_timestamp() -> str:
    """Obtiene la marca de tiempo actual en formato ISO."""
    return datetime.datetime.now().isoformat()


@app.get("/")
async def root():
    """Endpoint de verificación de estado de la API."""
    return {"status": "online", "message": "Wildlife RAG API is running"}


@app.get("/chats", response_model=List[ChatSession])
async def list_chats():
    """Lista todas las sesiones de chat."""
    return list(chats.values())


@app.post("/chats", response_model=ChatSession)
async def create_chat(chat_request: ChatRequest):
    """Crea una nueva sesión de chat."""
    chat_id = str(uuid.uuid4())
    timestamp = get_current_timestamp()
    
    new_chat = ChatSession(
        id=chat_id,
        title=chat_request.title,
        messages=[],
        created_at=timestamp,
        updated_at=timestamp
    )
    
    chats[chat_id] = new_chat
    return new_chat


@app.get("/chats/{chat_id}", response_model=ChatSession)
async def get_chat(chat_id: str):
    """Obtiene una sesión de chat específica."""
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    return chats[chat_id]


@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Elimina una sesión de chat."""
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    deleted_chat = chats.pop(chat_id)
    return {"message": f"Chat '{deleted_chat.title}' eliminado"}


@app.post("/chats/{chat_id}/messages", response_model=Message)
async def add_message(chat_id: str, question_request: QuestionRequest):
    """
    Procesa una pregunta del usuario y genera una respuesta usando RAG.
    """
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    
    question = question_request.question
    chat_session = chats[chat_id]
    
    # Registrar la pregunta del usuario
    user_message = Message(
        content=question,
        is_bot=False,
        timestamp=get_current_timestamp()
    )
    chat_session.messages.append(user_message)
    
    try:
        # Obtener el embedding de la pregunta
        query_vec = get_embedding(question)
        
        # Inicializar listas de resultados
        abstract_results = []
        colombia_results = []
        
        # Primero intentamos seleccionar la base de datos correcta
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Base de datos {config.MILVUS_DATABASE} seleccionada para búsqueda")
        except Exception as e:
            print(f"Nota: No se pudo seleccionar la base de datos {config.MILVUS_DATABASE}: {e}")
            print("Intentaremos acceder a la colección de todos modos")
        
        # Buscar en la colección source_abstract (principal)
        try:
            print(f"Intentando buscar en colección principal {config.ABSTRACT_COLLECTION}...")
            abstract_collection = get_abstract_collection()
            
            # Verificar la dimensión del embedding en la colección
            schema = abstract_collection.schema
            embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
            if embedding_field:
                print(f"Dimensión del embedding en {config.ABSTRACT_COLLECTION}: {embedding_field.dim}")
                print(f"Dimensión del vector de consulta: {len(query_vec)}")
                
                # Si la dimensión configurada no coincide con la colección, actualizar la configuración
                if embedding_field.dim != config.EMBEDDING_DIMENSION:
                    print(f"Ajustando la dimensión configurada de {config.EMBEDDING_DIMENSION} a {embedding_field.dim}")
                    config.EMBEDDING_DIMENSION = embedding_field.dim
                    
                    # Si también la dimensión del vector de consulta es diferente, regenerar el embedding
                    if len(query_vec) != embedding_field.dim:
                        print("Regenerando embedding con la dimensión correcta...")
                        query_vec = get_embedding(question)
            
            # Buscar documentos similares
            abstract_results = get_documents_from_query(query_vec, abstract_collection)
            print(f"Búsqueda exitosa en colección {config.ABSTRACT_COLLECTION}, se encontraron {len(abstract_results)} resultados")
        except Exception as e:
            print(f"Error al buscar en colección {config.ABSTRACT_COLLECTION}: {e}")
            abstract_results = []
            
            # Intentar con nombres alternativos de colección
            for collection_name in config.ALTERNATIVE_COLLECTION_NAMES:
                if collection_name == config.ABSTRACT_COLLECTION:
                    continue  # Ya lo intentamos
                    
                try:
                    print(f"Intentando con nombre alternativo: {collection_name}")
                    alt_collection = Collection(name=collection_name)
                    alt_results = get_documents_from_query(query_vec, alt_collection)
                    print(f"Búsqueda exitosa en colección alternativa {collection_name}, se encontraron {len(alt_results)} resultados")
                    abstract_results = alt_results
                    break
                except Exception as e2:
                    print(f"Error con colección alternativa {collection_name}: {e2}")
        
        # Solo buscamos en una colección ahora, no hay respaldo
        # Asegurarse de que tenemos al menos algunos resultados
        if not abstract_results:
            raise Exception("No se encontraron documentos relevantes en la colección. Por favor revise la configuración de dimensiones de embeddings y la disponibilidad de la colección.")
            
        # Combinar resultados
        all_results = abstract_results + colombia_results
        
        # Ordenar por score (de mayor a menor)
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Limitar a los top resultados para no sobrecargar el contexto
        top_results = all_results[:config.TOP_K]
        
        # Construir el contexto para OpenAI
        context = "\n\n".join([doc["content"] for doc in top_results])
        
        # Obtener historial de chat para proporcionar contexto de la conversación
        chat_history = [
            {"content": msg.content, "is_bot": msg.is_bot}
            for msg in chat_session.messages[-10:]  # Limitamos a las últimas 10 mensajes
        ]
        
        # Generar respuesta
        answer = generate_answer(question, context, chat_history)
        
        # Guardar la respuesta
        bot_message = Message(
            content=answer,
            is_bot=True,
            timestamp=get_current_timestamp()
        )
        
        chat_session.messages.append(bot_message)
        chat_session.updated_at = get_current_timestamp()
        
        return bot_message
        
    except Exception as e:
        # En caso de error, registrar el error y devolver un mensaje específico
        error_message = f"Error al procesar la pregunta: {str(e)}"
        print(error_message)  # Log del error
        
        # Personalizar el mensaje de error según el tipo de problema
        user_message = "No se pudo procesar la pregunta. Por favor, inténtalo de nuevo."
        
        # Si el error está relacionado con una colección vacía
        if "está vacía" in str(e):
            user_message = "La base de datos no contiene documentos. Por favor, asegúrate de que los datos se hayan cargado correctamente en la colección."
        # Si el error está relacionado con la conexión a Milvus
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            user_message = "No se pudo conectar a la base de datos. Por favor, verifica la conexión con el servidor Milvus."
        # Si el error está relacionado con la dimensión del vector
        elif "dimension" in str(e).lower() or "dimensión" in str(e).lower():
            user_message = "Hay un problema con la dimensión de los vectores. Por favor, verifica la configuración del modelo de embeddings."
        
        raise HTTPException(
            status_code=500,
            detail=user_message
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
