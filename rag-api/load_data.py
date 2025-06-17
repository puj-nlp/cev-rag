#!/usr/bin/env python3
"""
Script to load data into the source_abstract collection in Milvus.
This script loads data from a processed JSON file into the Milvus collection.
"""

import os
import json
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from dotenv import load_dotenv
import config

# Load environment variables if .env file exists
load_dotenv()

# Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "source_abstract")
DEFAULT_PROCESSED_DATA_PATH = "data/processed_data.json"

def connect_to_milvus():
    """Establishes connection with Milvus."""
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

def create_collection(collection_name):
    """Creates the collection if it doesn't exist."""
    # Check if collection already exists
    if utility.has_collection(collection_name):
        print(f"Collection {collection_name} already exists")
        return Collection(collection_name)
    
    print(f"Creating new collection: {collection_name}")
    
    # Define schema for the collection
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIMENSION),
        FieldSchema(name="source_id", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="link", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="page", dtype=DataType.INT64),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="dynamic_field", dtype=DataType.JSON),
    ]
    
    schema = CollectionSchema(fields, description=f"Collection {collection_name}")
    
    # Create the collection
    collection = Collection(name=collection_name, schema=schema)
    print(f"Collection {collection_name} created successfully")
    
    # Create an index for the embedding field
    print("Creating index for embedding vectors...")
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created successfully")
    
    return collection

def load_data(file_path, collection_name):
    """Loads data from a JSON file into the Milvus collection."""
    print(f"Loading data from {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return False
    
    print(f"Loaded {len(data)} records from JSON file")
    
    # Create or access the collection
    collection = create_collection(collection_name)
    
    # Preparar los datos para inserción
    entities = []
    batch_size = 1000
    total_inserted = 0
    
    for i, item in enumerate(data):
        # Prepare fields for insertion
        entity = {
            "embedding": item.get("embedding", [0.0] * config.EMBEDDING_DIMENSION),
            "source_id": str(item.get("source_id", "")),
            "link": str(item.get("link", "")),
            "page": int(item.get("page", 0)),
            "text": str(item.get("text", "")),
            "title": str(item.get("title", "")),
            "type": str(item.get("type", "")),
            "dynamic_field": item.get("metadata", {})
        }
        
        entities.append(entity)
        
        # Insert in batches for better performance
        if len(entities) >= batch_size or i == len(data) - 1:
            try:
                insert_result = collection.insert(entities)
                inserted_count = len(insert_result.primary_keys)
                total_inserted += inserted_count
                print(f"Inserted {inserted_count} documents (Total: {total_inserted}/{len(data)})")
                entities = []
            except Exception as e:
                print(f"Error inserting batch: {e}")
    
    # Ensure data is persisted
    print("Performing flush to ensure persistence...")
    collection.flush()
    
    # Verify total number of entities
    entity_count = collection.num_entities
    print(f"Final verification: collection contains {entity_count} entities")
    
    return True

def main():
    """Main function."""
    # Connect to Milvus
    if not connect_to_milvus():
        print("Could not connect to Milvus. Aborting.")
        return
    
    # Look for data file
    data_file = DEFAULT_PROCESSED_DATA_PATH
    if not os.path.exists(data_file):
        # Try to find in current directory or one level up
        if os.path.exists("processed_data.json"):
            data_file = "processed_data.json"
        elif os.path.exists("../processed_data.json"):
            data_file = "../processed_data.json"
        else:
            print(f"Data file not found at path {DEFAULT_PROCESSED_DATA_PATH}")
            data_file = input("Enter the path to processed_data.json: ")
            if not os.path.exists(data_file):
                print(f"File not found: {data_file}")
                return
    
    # Load the data
    if load_data(data_file, COLLECTION_NAME):
        print("Data loaded successfully to Milvus")
    else:
        print("An error occurred while loading data")

if __name__ == "__main__":
    main()
