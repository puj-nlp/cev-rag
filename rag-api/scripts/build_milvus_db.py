import os
import json
import datetime
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, utility, Collection
from openai import OpenAI
import numpy as np

# Import configuration
import sys
sys.path.append("..")
import config

# Configure OpenAI
try:
    with open("../secrets.json", "r") as f:
        secrets = json.load(f)
        api_key = secrets.get("openai_api_key", config.OPENAI_API_KEY)
except Exception as e:
    print(f"Could not load secrets.json: {e}")
    api_key = config.OPENAI_API_KEY
    
client = OpenAI(api_key=api_key)

# Configure paths
DATA_DIR = "./data"
ABSTRACT_DATA_PATH = os.path.join(DATA_DIR, "processed_data.json")

def get_embedding(text, model=config.EMBEDDING_MODEL):
    """Gets the embedding of a text using OpenAI."""
    # Make sure the text is not None or empty
    if not text:
        text = "Empty content"
    
    # Clean the text
    text = text.replace("\n", " ").strip()
    
    # Use the correct format for OpenAI API v1.0+
    try:
        response = client.embeddings.create(
            input=text,  # Simple string, not a list
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return a zero vector as fallback
        # Use the dimension configured in config.py
        return [0.0] * config.EMBEDDING_DIMENSION

def connect_to_milvus():
    """Connects to Milvus."""
    try:
        connections.connect(
            alias="default", 
            host=config.MILVUS_HOST,
            port=config.MILVUS_PORT
        )
        # In newer versions of pymilvus, we verify connection differently
        # is_connected is no longer available
        connections.get_connection_addr("default")
        print("Successfully connected to Milvus")
        print(f"Using collection: {config.ABSTRACT_COLLECTION}")
    except Exception as e:
        print(f"Error connecting to Milvus: {e}")
        raise

def check_existing_collection_dimension(collection_name):
    """
    Checks if a collection already exists and gets its embedding dimension.
    
    Args:
        collection_name: Name of the collection to check
        
    Returns:
        int or None: The embedding vector dimension if the collection exists, None otherwise
    """
    if not utility.has_collection(collection_name):
        return None
    
    try:
        collection = Collection(collection_name)
        schema = collection.schema
        for field in schema.fields:
            if field.name == "embedding" and hasattr(field, "dim"):
                print(f"Collection {collection_name} already exists with embedding dimension: {field.dim}")
                return field.dim
    except Exception as e:
        print(f"Error checking existing collection dimension: {e}")
    
    return None

def create_collection(collection_name, dimension=config.EMBEDDING_DIMENSION):
    """Creates a collection in Milvus with the specific schema."""
    # Check if the collection already exists and get its dimension
    existing_dimension = check_existing_collection_dimension(collection_name)
    
    # If the collection already exists, use its dimension instead of deleting it
    if existing_dimension:
        print(f"Using existing collection {collection_name} with dimension {existing_dimension}")
        return Collection(collection_name)
    
    # If the collection doesn't exist or was decided to be deleted, create a new one
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"Existing collection was deleted: {collection_name}")
    
    print(f"Creating new collection {collection_name} with dimension {dimension}")
    
    # Define appropriate schema based on the collection
    if collection_name == config.ABSTRACT_COLLECTION:
        # source_abstract schema according to the structure defined in Milvus
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="source_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="link", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="page", dtype=DataType.INT64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="dynamic_field", dtype=DataType.JSON)
        ]
        print(f"Creating collection {collection_name} with specific schema for Truth Commission data")
    else:
        # Generic schema for other collections
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
        ]
        print(f"Creating collection {collection_name} with generic schema")
    
    schema = CollectionSchema(fields, f"Collection {collection_name}")
    collection = Collection(name=collection_name, schema=schema)
    print(f"Collection created: {collection_name}")
    
    return collection

def load_data(filepath):
    """Loads data from a JSON file."""
    if not os.path.exists(filepath):
        print(f"File {filepath} does not exist")
        return []
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} documents from {filepath}")
    return data

def process_and_insert_data(collection, data, start_id=0):
    """Processes data and inserts it into the collection according to its schema."""
    # Determine batch size to process and insert in parts
    batch_size = 100  # Adjust as needed
    batch_count = (len(data) + batch_size - 1) // batch_size
    
    print("Generating embeddings... (this may take several minutes)")
    
    # Counter for all processed documents
    processed_count = 0
    
    # Determine collection schema
    collection_schema = collection.schema
    field_names = [field.name for field in collection_schema.fields]
    is_source_abstract = "text" in field_names and "source_id" in field_names
    
    for batch_idx in range(batch_count):
        batch_start = batch_idx * batch_size
        batch_end = min((batch_idx + 1) * batch_size, len(data))
        batch_items = list(data.values())[batch_start:batch_end] if isinstance(data, dict) else data[batch_start:batch_end]
        
        # Initialize lists for this batch according to schema
        batch_data = {"id": []}  # ID is always present
        
        # Initialize lists according to schema
        for field in field_names:
            if field != "id":  # ID is already initialized
                batch_data[field] = []
        
        print(f"Processing batch {batch_idx+1}/{batch_count} (documents {batch_start+1}-{batch_end})")
        
        for i, item in enumerate(batch_items):
            if i % 10 == 0:
                print(f"Processing document {batch_start+i+1}/{len(data)}")
            
            # Generate the embedding first to verify if we can continue
            text_content = ""
            if "Text" in item:
                text_content = item["Text"]
            elif "text" in item:
                text_content = item["text"]
            elif "content" in item:
                text_content = item["content"]
            
            if not text_content:
                print(f"Skipping document #{batch_start+i+1} - no content")
                continue
                
            try:
                embedding = get_embedding(text_content)
                
                # Add ID to the data list
                batch_data["id"].append(start_id + processed_count)
                batch_data["embedding"].append(embedding)
                
                # Process data according to collection schema
                if is_source_abstract:
                    # Schema for source_abstract
                    batch_data["text"].append(text_content)
                    batch_data["title"].append(item.get("Title", "") or item.get("title", ""))
                    batch_data["source_id"].append(item.get("ID", "") or item.get("source_id", ""))
                    batch_data["type"].append(item.get("Type", "") or item.get("type", ""))
                    batch_data["link"].append(item.get("Link", "") or item.get("link", ""))
                    batch_data["page"].append(int(item.get("Page", 0) or item.get("page", 0) or 0))
                    
                    # Dynamic fields as JSON
                    dynamic_data = {}
                    for k, v in item.items():
                        if k not in ["Text", "Title", "ID", "Type", "Link", "Page", "text", "title", "source_id", "type", "link", "page"]:
                            dynamic_data[k] = v
                    batch_data["dynamic_field"].append(dynamic_data)
                else:
                    # Schema for other collections (content and metadata)
                    content = text_content
                    batch_data["content"].append(content)
                    
                    # Build metadata as JSON
                    metadata = {}
                    for k, v in item.items():
                        if k not in ["content", "text"]:
                            metadata[k] = v
                    batch_data["metadata"].append(json.dumps(metadata))
                
                processed_count += 1
            except Exception as e:
                print(f"Error processing document #{batch_start+i+1}: {e}")
        
        # If we have data in this batch, insert it
        if batch_data["id"]:
            try:
                collection.insert(batch_data)
                print(f"Batch {batch_idx+1}/{batch_count} inserted: {len(batch_data['id'])} documents")
            except Exception as e:
                print(f"Error inserting batch {batch_idx+1}: {e}")
    
    return processed_count  # Return total number of documents processed

def create_index_and_load(collection):
    """Creates an index and loads the collection into memory."""
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 8, "efConstruction": 200}
    }
    
    collection.create_index("embedding", index_params)
    print("Index created")
    
    collection.load()
    print(f"Collection loaded with {collection.num_entities} entities")

def main():
    # Connect to Milvus
    connect_to_milvus()
    
    # Flag to know if any collection was created
    created_collection = False
    
    # Check if there's any alternative data path
    # In case the file is in the project root or if there is transformed data
    if not os.path.exists(ABSTRACT_DATA_PATH):
        alt_paths = [
            "./processed_data.json",
            "../processed_data.json",
            os.path.join(DATA_DIR, "abstracts_data.json"),
            os.path.join(DATA_DIR, "transformed_processed_data.json"),  # Look for transformed data
        ]
        for path in alt_paths:
            if os.path.exists(path):
                print(f"Using alternative path for data: {path}")
                abstract_data_path = path
                break
    else:
        abstract_data_path = ABSTRACT_DATA_PATH
    
    # Load data from processed_data.json
    abstract_data = load_data(abstract_data_path)
    if abstract_data:
        # Create the collection
        abstract_collection = create_collection(config.ABSTRACT_COLLECTION)
        
        # Process and insert data
        docs_processed = process_and_insert_data(abstract_collection, abstract_data)
        print(f"Total documents processed: {docs_processed}")
        
        # Create index and load the collection
        create_index_and_load(abstract_collection)
        created_collection = True
    
    # If no data was found to import, create an empty collection as fallback
    if not created_collection:
        print("No data found to import. Creating empty collection as fallback...")
        fallback_collection = create_collection(config.ABSTRACT_COLLECTION)
        
        # Create an example document to ensure the collection works
        sample_data = [{
            "content": "This is an example document for the Truth Commission collection about the Colombian conflict.",
            "source": "sample_document"
        }]
        process_and_insert_data(fallback_collection, sample_data)
        create_index_and_load(fallback_collection)
        print("Fallback collection created and loaded with an example document.")
    
    # Disconnect
    connections.disconnect("default")
    print("Disconnected from Milvus")
    
    # Create log file
    log_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "database": config.MILVUS_DATABASE,
        "collection": {
            "name": config.ABSTRACT_COLLECTION,
            "documents": len(abstract_data) if abstract_data else 0
        }
    }
    
    with open(os.path.join(DATA_DIR, "build_log.json"), "w") as f:
        json.dump(log_data, f, indent=2)
    
    print("Process completed and log saved.")

if __name__ == "__main__":
    main()
