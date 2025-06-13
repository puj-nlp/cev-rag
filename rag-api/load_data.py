#!/usr/bin/env python3
"""
Script para cargar datos en la colección source_abstract de Milvus.
Este script carga datos desde un archivo JSON procesado a la colección de Milvus.
"""

import os
import json
import numpy as np
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from dotenv import load_dotenv
import config

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

# Configuración
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "source_abstract")
DEFAULT_PROCESSED_DATA_PATH = "data/processed_data.json"

def connect_to_milvus():
    """Establece conexión con Milvus."""
    print(f"Conectando a Milvus en {MILVUS_HOST}:{MILVUS_PORT}...")
    
    try:
        connections.connect(
            alias="default", 
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        print("Conexión establecida correctamente")
        return True
    except Exception as e:
        print(f"Error al conectar: {e}")
        return False

def create_collection(collection_name):
    """Crea la colección si no existe."""
    # Verificar si la colección ya existe
    if utility.has_collection(collection_name):
        print(f"La colección {collection_name} ya existe")
        return Collection(collection_name)
    
    print(f"Creando nueva colección: {collection_name}")
    
    # Definir el esquema para la colección
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
    
    schema = CollectionSchema(fields, description=f"Colección {collection_name}")
    
    # Crear la colección
    collection = Collection(name=collection_name, schema=schema)
    print(f"Colección {collection_name} creada exitosamente")
    
    # Crear un índice para el campo de embedding
    print("Creando índice para vectores de embedding...")
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Índice creado exitosamente")
    
    return collection

def load_data(file_path, collection_name):
    """Carga datos desde un archivo JSON a la colección de Milvus."""
    print(f"Cargando datos desde {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
        return False
    
    print(f"Se cargaron {len(data)} registros del archivo JSON")
    
    # Crear o acceder a la colección
    collection = create_collection(collection_name)
    
    # Preparar los datos para inserción
    entities = []
    batch_size = 1000
    total_inserted = 0
    
    for i, item in enumerate(data):
        # Preparar los campos para inserción
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
        
        # Insertar en lotes para mejor rendimiento
        if len(entities) >= batch_size or i == len(data) - 1:
            try:
                insert_result = collection.insert(entities)
                inserted_count = len(insert_result.primary_keys)
                total_inserted += inserted_count
                print(f"Insertados {inserted_count} documentos (Total: {total_inserted}/{len(data)})")
                entities = []
            except Exception as e:
                print(f"Error al insertar lote: {e}")
    
    # Asegurar que los datos estén persistidos
    print("Realizando flush para garantizar persistencia...")
    collection.flush()
    
    # Verificar número total de entidades
    entity_count = collection.num_entities
    print(f"Verificación final: la colección contiene {entity_count} entidades")
    
    return True

def main():
    """Función principal."""
    # Conectar a Milvus
    if not connect_to_milvus():
        print("No se pudo conectar a Milvus. Abortando.")
        return
    
    # Buscar archivo de datos
    data_file = DEFAULT_PROCESSED_DATA_PATH
    if not os.path.exists(data_file):
        # Intentar buscar en el directorio actual o uno nivel arriba
        if os.path.exists("processed_data.json"):
            data_file = "processed_data.json"
        elif os.path.exists("../processed_data.json"):
            data_file = "../processed_data.json"
        else:
            print(f"No se encontró el archivo de datos en la ruta {DEFAULT_PROCESSED_DATA_PATH}")
            data_file = input("Ingresa la ruta al archivo processed_data.json: ")
            if not os.path.exists(data_file):
                print(f"No se encontró el archivo: {data_file}")
                return
    
    # Cargar los datos
    if load_data(data_file, COLLECTION_NAME):
        print("Datos cargados exitosamente a Milvus")
    else:
        print("Ocurrió un error al cargar los datos")

if __name__ == "__main__":
    main()
