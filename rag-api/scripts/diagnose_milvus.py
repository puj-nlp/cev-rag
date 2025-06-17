#!/usr/bin/env python3
"""
Diagnostic script for Milvus.
This script provides detailed information about databases and collections
available on the Milvus server.
"""

import os
import sys
import json
from pymilvus import connections, utility, Collection
from dotenv import load_dotenv

# Load environment variables if .env file exists
load_dotenv()

# Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_DATABASE = os.getenv("MILVUS_DATABASE", "colombia_data_qaps")
TARGET_COLLECTION = os.getenv("TARGET_COLLECTION", "source_abstract")

# Possible collection name variants
COLLECTION_VARIANTS = [
    TARGET_COLLECTION,
    f"{MILVUS_DATABASE}.{TARGET_COLLECTION}",
    f"default_{TARGET_COLLECTION}"
]

def print_separator(title=None):
    """Prints a separator line with optional title."""
    width = 80
    if title:
        print(f"\n{'=' * 10} {title} {'=' * (width - len(title) - 12)}")
    else:
        print('\n' + '=' * width)

def connect_to_milvus():
    """Establishes connection with Milvus."""
    print_separator("MILVUS CONNECTION")
    print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    
    try:
        connections.connect(
            alias="default", 
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        print("Connection established successfully")
        return True
    except Exception as e:
        print(f"Error connecting: {e}")
        return False

def check_databases():
    """Checks available databases."""
    print_separator("DATABASES")
    
    try:
        databases = utility.list_database()
        print(f"Available databases: {databases}")
        
        for db_name in databases:
            print(f"- {db_name}")
        
        if MILVUS_DATABASE in databases:
            print(f"\nTarget database '{MILVUS_DATABASE}' found ✓")
            # Try to select the database
            try:
                from pymilvus import db
                db.using_database(MILVUS_DATABASE)
                print(f"✓ Database '{MILVUS_DATABASE}' selected successfully")
            except Exception as e:
                print(f"⚠️ Error selecting database '{MILVUS_DATABASE}': {e}")
        else:
            print(f"\n⚠️ Target database '{MILVUS_DATABASE}' NOT found ⚠️")
        
        return databases
    except AttributeError:
        print("Current PyMilvus version does not support list_database()")
        print("This is normal in older versions or in Milvus Standalone")
        # Try to select the database anyway
        try:
            from pymilvus import db
            db.using_database(MILVUS_DATABASE)
            print(f"Attempting to select database '{MILVUS_DATABASE}' anyway...")
        except Exception as e:
            print(f"Note: Database selection not supported: {e}")
        return []
    except Exception as e:
        print(f"Error listing databases: {e}")
        return []

def check_collections():
    """Checks available collections."""
    print_separator("COLLECTIONS")
    
    # Initial list of collections before selecting database
    try:
        collections = utility.list_collections()
        print(f"Available collections before selecting database ({len(collections)}):")
        
        for idx, coll in enumerate(collections, 1):
            print(f"{idx}. {coll}")
            
        # Try to select specific database
        try:
            from pymilvus import db
            db.using_database(MILVUS_DATABASE)
            print(f"\nDatabase '{MILVUS_DATABASE}' selected to check collections")
            
            # List collections after selecting the database
            collections_after = utility.list_collections()
            print(f"Available collections AFTER selecting database ({len(collections_after)}):")
            
            for idx, coll in enumerate(collections_after, 1):
                print(f"{idx}. {coll}")
                
            # Use this list for verification
            collections = collections_after
        except Exception as e:
            print(f"Note: Could not select database to check collections: {e}")
        
        # Check if any variant of the target collection exists
        target_found = False
        for variant in COLLECTION_VARIANTS:
            if variant in collections:
                print(f"\nTarget collection found as: '{variant}' ✓")
                target_found = True
                break
                
        if not target_found:
            print(f"\n⚠️ No variant of the target collection was found ⚠️")
            print(f"Variants searched: {COLLECTION_VARIANTS}")
            
        return collections
    except Exception as e:
        print(f"Error listing collections: {e}")
        return []

def check_collection_details(collection_name):
    """Checks the details of a specific collection."""
    print_separator(f"COLLECTION DETAILS: {collection_name}")
    
    try:
        exists = utility.has_collection(collection_name)
        print(f"Does the collection exist? {exists}")
        
        if not exists:
            return False
            
        # Try to load the collection
        try:
            collection = Collection(collection_name)
            schema = collection.schema
            print(f"Collection name: {collection.name}")
            print(f"Description: {collection.description}")
            
            # Show fields
            print("\nFields:")
            for field in schema.fields:
                print(f"- {field.name}: {field.dtype}")
                if field.name == "embedding":
                    print(f"  Dimension: {field.dim}")
                    
            # Count entities
            try:
                count = collection.num_entities
                print(f"\nNumber of entities: {count}")
            except Exception as e:
                print(f"Error counting entities: {e}")
                
            return True
        except Exception as e:
            print(f"Error loading the collection: {e}")
            return False
    except Exception as e:
        print(f"Error checking collection existence: {e}")
        return False

def try_search_in_collection(collection_name, limit=5):
    """Attempts to perform a simple search in the collection."""
    print_separator(f"SEARCH TEST IN: {collection_name}")
    
    try:
        collection = Collection(collection_name)
        
        # Check if the collection is loaded
        try:
            collection.load()
            print("Collection loaded successfully")
        except Exception as e:
            print(f"Error loading the collection (it may already be loaded): {e}")
        
        # Get vector dimension
        schema = collection.schema
        embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
        
        if not embedding_field:
            print("No 'embedding' field found in the collection")
            return False
            
        dim = embedding_field.dim
        print(f"Vector dimension: {dim}")
        
        # Test vector (all zeros)
        test_vector = [0.0] * dim
        
        # Search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Determine output fields
        field_names = [field.name for field in schema.fields]
        output_fields = [f for f in field_names if f not in ["embedding"]]
        print(f"Output fields: {output_fields}")
        
        # Execute search
        print("Executing search...")
        results = collection.search(
            data=[test_vector],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=output_fields
        )
        
        # Show results
        print(f"\nResults found: {len(results[0])}")
        for i, hit in enumerate(results[0]):
            print(f"\nResult #{i+1}:")
            entity = hit.entity.to_dict()
            
            # Format main fields
            if "text" in entity:
                print(f"- text: {entity['text'][:100]}..." if len(entity['text']) > 100 else entity['text'])
            
            if "title" in entity:
                print(f"- title: {entity['title']}")
                
            if "source_id" in entity:
                print(f"- source_id: {entity['source_id']}")
                
            # Show score
            print(f"- score: {hit.score}")
            
        return True
    except Exception as e:
        print(f"Error in search: {e}")
        return False

def main():
    """Main function."""
    print("MILVUS DIAGNOSTICS")
    print(f"Host: {MILVUS_HOST}")
    print(f"Port: {MILVUS_PORT}")
    print(f"Target database: {MILVUS_DATABASE}")
    print(f"Target collection: {TARGET_COLLECTION}")
    
    # Connect to Milvus
    if not connect_to_milvus():
        print("\n⚠️ Could not connect to Milvus. Aborting diagnostics.")
        return
    
    # Check databases
    databases = check_databases()
    
    # Check collections
    collections = check_collections()
    
    # Check details of each collection variant
    for variant in COLLECTION_VARIANTS:
        if variant in collections:
            check_collection_details(variant)
            try_search_in_collection(variant)
    
    print_separator("DIAGNOSTICS COMPLETE")
    print("If you need help interpreting these results, consult:")
    print("https://milvus.io/docs/troubleshooting.md")

if __name__ == "__main__":
    main()
