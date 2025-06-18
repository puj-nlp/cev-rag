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

# Function to diagnose the Milvus collection structure
def diagnose_milvus_collection():
    try:
        print("\n--- MILVUS DIAGNOSTICS ---")
        
        # List all collections
        from pymilvus import utility
        collections = utility.list_collections()
        print(f"Available collections: {collections}")
        
        # Try to access the main collection
        try:
            collection_name = config.ABSTRACT_COLLECTION
            print(f"\nVerifying collection: {collection_name}")
            
            collection = Collection(name=collection_name)
            
            # Get schema information
            schema = collection.schema
            print(f"Collection schema: {schema}")
            
            # List fields
            fields = [field.name for field in schema.fields]
            print(f"Available fields: {fields}")
            
            # Verify data quantity
            entity_count = collection.num_entities
            print(f"Number of entities: {entity_count}")
            
            # If there is data, try to get some samples
            if entity_count > 0:
                print("\nTrying to obtain data samples:")
                
                # Load the collection
                collection.load()
                
                # Perform a random search
                import random
                random_vec = [random.random() for _ in range(config.EMBEDDING_DIMENSION)]
                
                # Use all fields except embedding
                output_fields = [f for f in fields if f != "embedding"]
                print(f"Fields to query: {output_fields}")
                
                # Perform a search
                results = collection.search(
                    data=[random_vec],
                    anns_field="embedding",
                    param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                    limit=3,
                    output_fields=output_fields
                )
                
                # Show results
                print(f"Results found: {len(results[0])}")
                for i, hit in enumerate(results[0]):
                    print(f"\nDocument {i+1}:")
                    doc_dict = hit.entity.to_dict()
                    print(f"Fields available in result: {list(doc_dict.keys())}")
                    
                    # Show some values
                    for key, value in doc_dict.items():
                        # Limit length for long fields
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  - {key}: {value[:100]}...")
                        else:
                            print(f"  - {key}: {value}")
            
        except Exception as e:
            print(f"Error verifying collection {collection_name}: {e}")
            import traceback
            print(traceback.format_exc())
    
    except Exception as e:
        print(f"Error in general diagnosis: {e}")
        import traceback
        print(traceback.format_exc())

# Execute diagnostics at startup
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
    print(f"Detecting fields in the collection. Available fields: {field_names}")
    
    # For the source_abstract collection, we know these are the fields we need
    expected_fields = ["id", "text", "title", "type", "link", "source_id", "page"]
    
    # Filter only the fields that exist in the collection
    output_fields = [field for field in expected_fields if field in field_names and field != "id"]
    
    # If for some reason the expected fields were not found, include all except embedding
    if not output_fields:
        print("WARNING: Expected fields not found. Including all except 'embedding'")
        output_fields = [f for f in field_names if f not in ["embedding"]]
    
    print(f"Final output fields: {output_fields}")
    
    print(f"Executing Milvus search with the following parameters:")
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
    
    # Debug: Let's verify the structure of the results
    print(f"Results type: {type(results)}")
    print(f"Number of results: {len(results)}")
    print(f"Structure of first result set: {type(results[0])}")
    print(f"Number of hits in first set: {len(results[0])}")
    
    print(f"Available fields in collection: {field_names}")
    print(f"Configured output fields: {output_fields}")
    
    documents = []
    for hit in results[0]:
        print(f"Raw hit data: {hit}")
        doc_dict = hit.entity.to_dict()
        print(f"Document dictionary from Milvus: {doc_dict}")
        
        # Based on the known schema of source_abstract
        # The main content field is 'text'
        content = doc_dict.get('text', '')
        
        # If the text field is empty, check if there are other fields with content
        if not content:
            print("WARNING: Empty 'text' field, checking values in all fields")
            # Show all fields and their values
            for field_name, field_value in doc_dict.items():
                if field_name != 'embedding' and field_value:
                    print(f"  - Field '{field_name}' has value: {str(field_value)[:50]}...")
                    
        # Structure the metadata
        metadata = {
            "source_id": doc_dict.get('source_id', ''),
            "link": doc_dict.get('link', ''),
            "page": doc_dict.get('page', 0),
            "title": doc_dict.get('title', ''),
            "type": doc_dict.get('type', '')
        }
        
        # Depurar valores
        print(f"Extracted content: {str(content)[:100]}..." if content else "Content: EMPTY")
        print(f"Extracted metadata: {metadata}")
        
        # If content is still empty after all checks,
        # use the title as a last resort
        if not content and doc_dict.get('title'):
            content = f"Document title: {doc_dict.get('title')}"
            print(f"Using title as content: {content}")
        
        # Ensure we have some content
        if not content:
            content = "Could not extract content from this document."
            print("WARNING: Could not get content from document")
        
        # Add the processed document to the results list
        documents.append({
            "content": content,
            "metadata": metadata,
            "score": hit.score,
            # Also include original fields for debugging
            "original_fields": doc_dict
        })
    
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
        {"role": "system", "content": """You are 'Window to Truth', an academic researcher specialized in the Colombian conflict and the Truth Commission. Generate detailed and rigorous responses based EXCLUSIVELY on the information provided. Follow these specific guidelines:

1. STRICT ACADEMIC FORMAT:
   - Begin with a clear "Introduction" that presents the general topic.
   - Use bold subtitles to organize information by regions, themes, or concepts.
   - When mentioning specific data, ALWAYS include the citation in IEEE format [number] at the end of the sentence.
   - End with a "Conclusion" that synthesizes the main points.

2. CITATIONS AND REFERENCES:
   - SPECIFICALLY cite pages and exact sources from the documents.
   - Use the format [number] for in-text citations.
   - At the end, include a "References" section with the complete format: [number] Document title, page X.

3. CONTENT, ETHICS, AND TONE:
   - Treat topics with academic rigor and ethical sensitivity due to the nature of the conflict.
   - DO NOT reveal names of victims, specific locations of sensitive events, or details that could endanger individuals or communities.
   - Use precise, objective, and formal language; avoid emotionally charged terms.
   - Base your responses EXCLUSIVELY on the provided information; do not make assumptions.
   - Maintain neutrality and avoid bias towards any actor in the conflict.

4. RESPONSIBILITY AND ATTRIBUTION:
   - Focus on systemic factors, institutional roles, and collective responsibility rather than blaming specific individuals.
   - Analyze the broader context and the interaction of various actors in the conflict.

5. INFORMATION MANAGEMENT:
   - If the requested information is not available in the sources, clearly indicate it.
   - If sources present conflicts or ambiguities, acknowledge it and present the different perspectives.

Your answer should be structured, academic, and rich in specific data, similar to a formal report from the Truth Commission."""}
    ]
    
    # Add chat history (include only a limited amount to keep context focused)
    relevant_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
    for message in relevant_history:
        role = "assistant" if message["is_bot"] else "user"
        messages.append({"role": role, "content": message["content"]})
    
    # Structure the prompt to encourage a high-quality academic response
    content_prompt = f"""
Please generate a complete academic response to the following question about the Colombian conflict.
Use ONLY the information provided in the context and appropriately cite the sources.

QUESTION:
{question}

AVAILABLE CONTEXT (cite these sources specifically):
{context}

SPECIAL INSTRUCTIONS:
1. Structure your response with a clear "Introduction", sections with bold subtitles, and a "Conclusion".
2. IMPORTANT: Cite specific sources using the format: (Source: [Title], Page: [number]) after each data point or assertion.
3. Include concrete data, specific names of regions, and exact figures when available.
4. At the end of your response, add the "References" header to indicate where the complete bibliography should go.

Your answer must be rigorous, well-structured, and academically grounded.
"""
    
    messages.append({"role": "user", "content": content_prompt})
    
    response = client.chat.completions.create(
        model=config.COMPLETION_MODEL,
        messages=messages,
        temperature=0.3,  # Lower temperature for more consistent and precise responses
        max_tokens=800    # Increase the token limit to allow for more detailed responses
    )
    
    return response.choices[0].message.content
