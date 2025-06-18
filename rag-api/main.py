import json
import uuid
import datetime
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pymilvus import Collection, db

import config
from models import ChatSession, Message, QuestionRequest, ChatRequest, ErrorResponse
from rag_service import get_embedding, get_abstract_collection, get_documents_from_query, generate_answer
from chat_with_tools import generate_answer_with_tools

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

# Verify Milvus collections at startup
def verify_milvus_collections():
    from pymilvus import utility, Collection, connections, db
    import time
    
    # Try connecting multiple times to give the Milvus service time to start
    max_attempts = 5
    for attempt in range(max_attempts):
        # Al principio de cada intento, limpiar la configuración de colección
        # para asegurarnos de que se realiza el diagnóstico completo
        config.ABSTRACT_COLLECTION = "source_abstract"
        
        # Try to select the correct database
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Database {config.MILVUS_DATABASE} selected for verification")
        except Exception as e:
            print(f"Note: Could not select database {config.MILVUS_DATABASE}: {e}")
            print("This is normal in older versions of Milvus or in Milvus Standalone")
        try:
            print(f"Verifying Milvus connection (attempt {attempt+1}/{max_attempts})...")
            
            # Verify the Milvus connection
            try:
                conn_status = connections.get_connection_addr("default")
                print(f"Milvus connection status: {conn_status}")
            except Exception as e:
                print(f"Error checking connection status: {e}")
                # Intentar reconectar si hay algún problema
                connections.connect(alias="default", host=config.MILVUS_HOST, port=config.MILVUS_PORT)
            
            # Listar todas las bases de datos disponibles
            try:
                all_databases = utility.list_database()
                print(f"Bases de datos disponibles en Milvus: {all_databases}")
                
                if config.MILVUS_DATABASE not in all_databases:
                    print(f"WARNING! Database {config.MILVUS_DATABASE} not found in: {all_databases}")
                else:
                    print(f"Database {config.MILVUS_DATABASE} found")
            except Exception as e:
                print(f"Error al listar bases de datos: {e}")
                print("The installed PyMilvus or Milvus version may not support multiple databases")
            
            # Listar todas las colecciones disponibles
            try:
                all_collections = utility.list_collections()
                print(f"Colecciones disponibles en Milvus: {all_collections}")
                
                # Buscar la colección por todos los nombres posibles
                target_found = False
                for collection_name in config.ALTERNATIVE_COLLECTION_NAMES:
                    if collection_name in all_collections:
                        print(f"Collection found with name: {collection_name}!")
                        config.ABSTRACT_COLLECTION = collection_name
                        target_found = True
                        break
                
                if not target_found:
                    print(f"WARNING: Collection not found in any name variant: {config.ALTERNATIVE_COLLECTION_NAMES}")
            except Exception as e:
                print(f"Error al listar colecciones: {e}")
            
            # Try to verify and access the collection with each possible name format
            collection_candidates = config.ALTERNATIVE_COLLECTION_NAMES + [f"{config.MILVUS_DATABASE}.{config.ABSTRACT_COLLECTION}"]
            for collection_name in collection_candidates:
                try:
                    has_collection = utility.has_collection(collection_name)
                    print(f"Collection {collection_name} exists: {has_collection}")
                    
                    if has_collection:
                        try:
                            print(f"Attempting to access collection: {collection_name}")
                            abstract_collection = Collection(name=collection_name)
                            schema = abstract_collection.schema
                            embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
                            if embedding_field:
                                print(f"Dimensión de embedding en {collection_name}: {embedding_field.dim}")
                                if embedding_field.dim != config.EMBEDDING_DIMENSION:
                                    print(f"WARNING: Configured dimension ({config.EMBEDDING_DIMENSION}) does not match the collection ({embedding_field.dim})")
                                    # Actualizar la dimensión configurada para que coincida con la colección
                                    config.EMBEDDING_DIMENSION = embedding_field.dim
                                    print(f"Actualizada la dimensión configurada a: {config.EMBEDDING_DIMENSION}")
                                
                                # Count entities to verify there is data
                                entity_count = abstract_collection.num_entities
                                print(f"Número de entidades en {collection_name}: {entity_count}")
                                
                                # Si encontramos la colección y tiene datos, actualizar el nombre en la configuración
                                if entity_count > 0:
                                    config.ABSTRACT_COLLECTION = collection_name
                                    print(f"Usando colección {collection_name} con {entity_count} entidades")
                                    break
                        except Exception as e:
                            print(f"Error verifying {collection_name}: {e}")
                except Exception as e:
                    print(f"Error verifying existence of {collection_name}: {e}")
            
            # Si llegamos aquí, hemos podido conectar correctamente
            break
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Error verifying Milvus connection: {e}")
                print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Could not verify Milvus connection after {max_attempts} attempts.")

# Ejecutar la verificación en segundo plano para no bloquear el inicio de la API
import threading
threading.Thread(target=verify_milvus_collections, daemon=True).start()

# In-memory storage for chats (in production, we would use a database)
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
async def add_message(
    chat_id: str, 
    question_request: QuestionRequest, 
    use_tools: bool = Query(True, description="Whether to use the tool calling approach to get more specific context")
):
    """
    Processes a user's question and generates a response using RAG.
    Optionally uses the tool calling approach for more specific questions.
    """
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    question = question_request.question
    chat_session = chats[chat_id]
    
    # Register the user's question
    user_message = Message(
        content=question,
        is_bot=False,
        timestamp=get_current_timestamp()
    )
    chat_session.messages.append(user_message)
    
    try:
        # If tool calling is requested, use the advanced approach
        if use_tools:
            print(f"Using Tool Calling approach for the question: {question}")
            
            # Get chat history to provide conversation context
            chat_history = [
                {"content": msg.content, "is_bot": msg.is_bot}
                for msg in chat_session.messages[-10:]  # Limit to the last 10 messages
            ]
            
            # Generate response using the tool calling approach
            tool_response = generate_answer_with_tools(question, chat_history)
            
            # Extract references from the contexts used in tool calling
            references = []
            contexts_used = tool_response.get("contexts", [])
            
            print(f"\n--- PREPARING REFERENCES FROM TOOL CONTEXTS ---")
            print(f"Number of contexts found: {len(contexts_used)}")
            
            # Try to use documents collected during tool execution first
            all_documents = []
            for context in contexts_used:
                documents = context.get("documents", [])
                all_documents.extend(documents)
            
            # If we have documents from the tool execution, use those
            if all_documents:
                print(f"Using {len(all_documents)} documents from tool execution")
                # Sort by score and take the top 3
                all_documents.sort(key=lambda x: x.get("score", 0), reverse=True)
                top_documents = all_documents[:3]
            else:
                # Fallback: Get documents using direct search
                print("No documents found in tool contexts, performing fallback search")
                query_vec = get_embedding(question)
                try:
                    # First, try to select the correct database
                    try:
                        db.using_database(config.MILVUS_DATABASE)
                        print(f"Database {config.MILVUS_DATABASE} selected for reference extraction")
                    except Exception as e:
                        print(f"Note: Could not select database {config.MILVUS_DATABASE}: {e}")
                    
                    abstract_collection = get_abstract_collection()
                    fallback_results = get_documents_from_query(query_vec, abstract_collection)
                    top_documents = []
                    
                    for doc in fallback_results[:3]:
                        metadata = doc.get("metadata", {})
                        original = doc.get("original_fields", {})
                        
                        top_documents.append({
                            "title": metadata.get("title") or original.get("title") or "Untitled document",
                            "page": metadata.get("page") or original.get("page") or "",
                            "source_id": metadata.get("source_id") or original.get("source_id") or "",
                            "metadata": metadata,
                            "original_fields": original,
                            "score": doc.get("score", 0)
                        })
                        
                except Exception as e:
                    print(f"Error in fallback search for references: {e}")
                    top_documents = []
            
            # Process documents to create references
            for i, doc in enumerate(top_documents):
                title = doc.get("title", "Untitled document")
                source_id = doc.get("source_id", "")
                page = doc.get("page", "")
                
                # Normalize document names for academic format
                if not source_id.startswith("Tomo") and "vol" not in source_id.lower():
                    # Try to infer if it's a volume based on the title
                    if "tomo" in title.lower() or "vol" in title.lower():
                        source_id = title  # Use title if it seems to contain volume information
                
                # Convert page to string if it's a number
                if isinstance(page, (int, float)):
                    page = str(int(page))  # Convert to int then string to remove decimals
                
                print(f"Tool Reference {i+1}: Title={title}, Source={source_id}, Page={page}")
                
                # Add this reference to the list with academic format
                references.append({
                    "number": i+1,
                    "title": title,
                    "source_id": source_id,
                    "page": page,
                    "year": "2022",  # Fixed year for Truth Commission documents
                    "publisher": "Colombia. Comisión de la Verdad",
                    "isbn": "978-958-53874-3-0"  # Standard ISBN for Commission docs
                })
            
            print(f"Generated {len(references)} references for tool-based response")
            
            # Create response message
            bot_message = Message(
                content=tool_response["content"],
                is_bot=True,
                timestamp=get_current_timestamp(),
                references=references
            )
            
            chat_session.messages.append(bot_message)
            chat_session.updated_at = get_current_timestamp()
            
            return bot_message
        
        # If not using tool calling, proceed with the standard approach
        # Get the question embedding
        query_vec = get_embedding(question)
        
        # Initialize results lists
        abstract_results = []
        colombia_results = []
        
        # First, we try to select the correct database
        try:
            db.using_database(config.MILVUS_DATABASE)
            print(f"Database {config.MILVUS_DATABASE} selected for search")
        except Exception as e:
            print(f"Note: Could not select database {config.MILVUS_DATABASE}: {e}")
            print("We will try to access the collection anyway")
        
        # Buscar en la colección source_abstract (principal)
        try:
            print(f"Attempting to search in main collection {config.ABSTRACT_COLLECTION}...")
            abstract_collection = get_abstract_collection()
            
            # Verify the embedding dimension in the collection
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
            
            # Search for similar documents
            abstract_results = get_documents_from_query(query_vec, abstract_collection)
            print(f"Successful search in collection {config.ABSTRACT_COLLECTION}, found {len(abstract_results)} results")
            
            # Show result details for diagnosis
            print("\n--- RESULT DETAILS ---")
            for i, doc in enumerate(abstract_results[:3]):  # Solo mostrar los primeros 3 para no sobrecargar los logs
                print(f"Document {i+1}:")
                
                # Verify content
                content = doc.get('content', '')
                if content:
                    print(f"  - Content ({type(content).__name__}, len={len(content)}): {content[:100]}...")
                else:
                    print(f"  - Content: EMPTY")
                
                # Verify metadata
                metadata = doc.get('metadata', {})
                print(f"  - Metadata ({type(metadata).__name__}, keys={list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}):")
                if isinstance(metadata, dict) and metadata:
                    for key, value in metadata.items():
                        print(f"      - {key}: {value}")
                else:
                    print(f"      EMPTY or NOT A DICTIONARY: {metadata}")
                
                # Verify score
                print(f"  - Score: {doc.get('score', 0)}")
                
                # Verify all available fields in the document
                print(f"  - Todos los campos disponibles: {list(doc.keys())}")
        except Exception as e:
            print(f"Error al buscar en colección {config.ABSTRACT_COLLECTION}: {e}")
            import traceback
            print(traceback.format_exc())
            abstract_results = []
            
            # Intentar con nombres alternativos de colección
            for collection_name in config.ALTERNATIVE_COLLECTION_NAMES:
                if collection_name == config.ABSTRACT_COLLECTION:
                    continue  # Ya lo intentamos
                    
                try:
                    print(f"Trying with alternative name: {collection_name}")
                    alt_collection = Collection(name=collection_name)
                    alt_results = get_documents_from_query(query_vec, alt_collection)
                    print(f"Successful search in alternative collection {collection_name}, found {len(alt_results)} results")
                    abstract_results = alt_results
                    break
                except Exception as e2:
                    print(f"Error con colección alternativa {collection_name}: {e2}")
        
        # Solo buscamos en una colección ahora, no hay respaldo
        # Make sure we have at least some results
        if not abstract_results:
            raise Exception("No relevant documents found in the collection. Please review the embedding dimensions configuration and collection availability.")
            
        # Combine results
        all_results = abstract_results + colombia_results
        
        # Ordenar por score (de mayor a menor)
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit to top results to not overload the context
        top_results = all_results[:config.TOP_K]
        
        # Build context for OpenAI
        context_pieces = []
        print("\n--- CONTEXT BUILDING ---")
        for i, doc in enumerate(top_results):
            # Primero, intentamos usar el campo content que debería haber sido extraído correctamente
            content = doc.get("content", "")
            source = "content"
            
            # Directly check original fields if available
            if not content and "original_fields" in doc:
                if "text" in doc["original_fields"] and doc["original_fields"]["text"]:
                    content = doc["original_fields"]["text"]
                    source = "original_fields.text"
                
                # If there's still no content, try with the title
                if not content and "title" in doc["original_fields"] and doc["original_fields"]["title"]:
                    content = f"Document titled: {doc['original_fields']['title']}"
                    source = "original_fields.title"
            
            # Add important metadata to the context
            metadata = doc.get("metadata", {})
            meta_string = ""
            if metadata.get("title"):
                meta_string += f"Title: {metadata['title']}\n"
            if metadata.get("source_id"):
                meta_string += f"Fuente: {metadata['source_id']}\n"
            if metadata.get("page"):
                meta_string += f"Página: {metadata['page']}\n"
            
            # Combine metadata and content
            full_content = ""
            if meta_string:
                full_content = f"{meta_string}\n{content}"
            else:
                full_content = content
            
            # Registrar lo que encontramos
            if full_content:
                print(f"Document {i+1}: Adding {len(full_content)} characters to context (source: {source})")
                context_pieces.append(full_content)
            else:
                print(f"Document {i+1}: No content found to add to context")
        
        # Join all context pieces
        context = "\n\n---\n\n".join(context_pieces)
        print(f"Total context: {len(context)} characters")
        
        # If there's no context, create a basic one to avoid errors
        if not context.strip():
            print("WARNING: No useful context found in documents. Using generic message.")
            context = "No relevant information was found for this question in the database."
        
        # Get chat history to provide conversation context
        chat_history = [
            {"content": msg.content, "is_bot": msg.is_bot}
            for msg in chat_session.messages[-10:]  # Limit to the last 10 messages
        ]
        
        # Prepare references to be included in the response in academic format
        references = []
        print("\n--- PREPARING ACADEMIC REFERENCES ---")
        for i, doc in enumerate(top_results[:3]):  # Use up to 3 documents as references
            metadata = doc.get("metadata", {})
            original = doc.get("original_fields", {})
            
            # Get the title and bibliographic data
            title = metadata.get("title") or original.get("title") or "Untitled document"
            
            # Try to extract volume information from the title or source_id
            source_id = metadata.get("source_id") or original.get("source_id") or ""
            # Normalize document names for academic format
            if not source_id.startswith("Tomo") and "vol" not in source_id.lower():
                # Try to infer if it's a volume based on the title
                if "tomo" in title.lower() or "vol" in title.lower():
                    source_id = title  # Use title if it seems to contain volume information
            
            # Get page number
            page = metadata.get("page") or original.get("page") or ""
            # Convert page to string if it's a number
            if isinstance(page, (int, float)):
                page = str(int(page))  # Convertir a entero y luego a string para eliminar decimales
            
            print(f"Reference {i+1}: Title={title}, Source={source_id}, Page={page}")
            
            # Add this reference to the list with academic format
            references.append({
                "number": i+1,
                "title": title,
                "source_id": source_id,
                "page": page,
                "year": "2022",  # Fixed year for Truth Commission documents
                "publisher": "Colombia. Comisión de la Verdad",
                "isbn": "978-958-53874-3-0"  # ISBN estándar para docs de la Comisión
            })
        
        # Generate response including the context and references
        print(f"Generating response with {len(context)} characters of context and {len(references)} references")
        answer = generate_answer(question, context, chat_history)
        
        # Adjust the response to ensure it includes the references in academic format
        if references:
            # Si ya existe la sección de Referencias, la reemplazamos; si no, la añadimos
            if "Referencias" in answer:
                # Encontrar dónde comienza la sección de Referencias
                ref_index = answer.find("Referencias")
                # Truncate the response to remove any content after "References"
                answer = answer[:ref_index]
            
            # Crear la sección de Referencias en formato académico completo
            refs_text = "\n\nReferencias\n\n"
            for ref in references:
                # Formato de referencia académica completa
                title = ref['title'] or "Untitled document"
                source_id = ref['source_id'] or ""
                page = ref['page'] or ""
                
                # Construir la referencia en formato académico
                ref_line = f"{ref['number']}. {title}. (2022). Colombia. Comisión de la Verdad. ISBN 978-958-53874-3-0"
                
                # Add source/volume information if available
                if source_id:
                    ref_line += f". (Fuente: {source_id}"
                    if page:
                        ref_line += f", Página: {page}"
                    ref_line += ")"
                elif page:
                    ref_line += f", p. {page}"
                
                refs_text += ref_line + "\n"
            
            # Add references to the end of the response
            answer = answer.strip() + "\n\n" + refs_text
        
        # Save the response with references
        bot_message = Message(
            content=answer,
            is_bot=True,
            timestamp=get_current_timestamp(),
            references=references
        )
        
        chat_session.messages.append(bot_message)
        chat_session.updated_at = get_current_timestamp()
        
        return bot_message
        
    except Exception as e:
        # En caso de error, registrar el error y devolver un mensaje específico
        error_message = f"Error processing the question: {str(e)}"
        print(error_message)  # Log del error
        
        # Personalizar el mensaje de error según el tipo de problema
        user_message = "Could not process the question. Please try again."
        
        # If the error is related to an empty collection
        if "está vacía" in str(e) or "is empty" in str(e):
            user_message = "The database contains no documents. Please ensure data has been correctly loaded into the collection."
        # If the error is related to Milvus connection
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            user_message = "Could not connect to the database. Please verify the connection to the Milvus server."
        # If the error is related to vector dimensions
        elif "dimension" in str(e).lower() or "dimensión" in str(e).lower():
            user_message = "There is a problem with the vector dimensions. Please verify the embeddings model configuration."
        
        raise HTTPException(
            status_code=500,
            detail=user_message
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
