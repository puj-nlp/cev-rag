#!/usr/bin/env python3
"""
Script de diagnóstico para Milvus.
Este script proporciona información detallada sobre las bases de datos y colecciones
disponibles en el servidor Milvus.
"""

import os
import sys
import json
from pymilvus import connections, utility, Collection
from dotenv import load_dotenv

# Cargar variables de entorno si existe un archivo .env
load_dotenv()

# Configuración
MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_DATABASE = os.getenv("MILVUS_DATABASE", "colombia_data_qaps")
TARGET_COLLECTION = os.getenv("TARGET_COLLECTION", "source_abstract")

# Posibles variantes de nombre de colección
COLLECTION_VARIANTS = [
    TARGET_COLLECTION,
    f"{MILVUS_DATABASE}.{TARGET_COLLECTION}",
    f"default_{TARGET_COLLECTION}"
]

def print_separator(title=None):
    """Imprime una línea separadora con título opcional."""
    width = 80
    if title:
        print(f"\n{'=' * 10} {title} {'=' * (width - len(title) - 12)}")
    else:
        print('\n' + '=' * width)

def connect_to_milvus():
    """Establece conexión con Milvus."""
    print_separator("CONEXIÓN A MILVUS")
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

def check_databases():
    """Verifica las bases de datos disponibles."""
    print_separator("BASES DE DATOS")
    
    try:
        databases = utility.list_database()
        print(f"Bases de datos disponibles: {databases}")
        
        for db_name in databases:
            print(f"- {db_name}")
        
        if MILVUS_DATABASE in databases:
            print(f"\nBase de datos objetivo '{MILVUS_DATABASE}' encontrada ✓")
            # Intentar seleccionar la base de datos
            try:
                from pymilvus import db
                db.using_database(MILVUS_DATABASE)
                print(f"✓ Base de datos '{MILVUS_DATABASE}' seleccionada correctamente")
            except Exception as e:
                print(f"⚠️ Error al seleccionar la base de datos '{MILVUS_DATABASE}': {e}")
        else:
            print(f"\n⚠️ Base de datos objetivo '{MILVUS_DATABASE}' NO encontrada ⚠️")
        
        return databases
    except AttributeError:
        print("La versión actual de PyMilvus no soporta list_database()")
        print("Esto es normal en versiones antiguas o en Milvus Standalone")
        # Intentar seleccionar la base de datos de todos modos
        try:
            from pymilvus import db
            db.using_database(MILVUS_DATABASE)
            print(f"Intentando seleccionar base de datos '{MILVUS_DATABASE}' de todos modos...")
        except Exception as e:
            print(f"Nota: Selección de base de datos no soportada: {e}")
        return []
    except Exception as e:
        print(f"Error al listar bases de datos: {e}")
        return []

def check_collections():
    """Verifica las colecciones disponibles."""
    print_separator("COLECCIONES")
    
    # Lista inicial de colecciones antes de seleccionar base de datos
    try:
        collections = utility.list_collections()
        print(f"Colecciones disponibles antes de seleccionar base de datos ({len(collections)}):")
        
        for idx, coll in enumerate(collections, 1):
            print(f"{idx}. {coll}")
            
        # Intentar seleccionar base de datos específica
        try:
            from pymilvus import db
            db.using_database(MILVUS_DATABASE)
            print(f"\nBase de datos '{MILVUS_DATABASE}' seleccionada para verificar colecciones")
            
            # Listar colecciones después de seleccionar la base de datos
            collections_after = utility.list_collections()
            print(f"Colecciones disponibles DESPUÉS de seleccionar base de datos ({len(collections_after)}):")
            
            for idx, coll in enumerate(collections_after, 1):
                print(f"{idx}. {coll}")
                
            # Usar esta lista para verificación
            collections = collections_after
        except Exception as e:
            print(f"Nota: No se pudo seleccionar la base de datos para verificar colecciones: {e}")
        
        # Verificar si alguna variante de la colección objetivo existe
        target_found = False
        for variant in COLLECTION_VARIANTS:
            if variant in collections:
                print(f"\nColección objetivo encontrada como: '{variant}' ✓")
                target_found = True
                break
                
        if not target_found:
            print(f"\n⚠️ Ninguna variante de la colección objetivo fue encontrada ⚠️")
            print(f"Variantes buscadas: {COLLECTION_VARIANTS}")
            
        return collections
    except Exception as e:
        print(f"Error al listar colecciones: {e}")
        return []

def check_collection_details(collection_name):
    """Verifica los detalles de una colección específica."""
    print_separator(f"DETALLES DE COLECCIÓN: {collection_name}")
    
    try:
        exists = utility.has_collection(collection_name)
        print(f"¿Existe la colección? {exists}")
        
        if not exists:
            return False
            
        # Intentar cargar la colección
        try:
            collection = Collection(collection_name)
            schema = collection.schema
            print(f"Nombre de la colección: {collection.name}")
            print(f"Descripción: {collection.description}")
            
            # Mostrar campos
            print("\nCampos:")
            for field in schema.fields:
                print(f"- {field.name}: {field.dtype}")
                if field.name == "embedding":
                    print(f"  Dimensión: {field.dim}")
                    
            # Contar entidades
            try:
                count = collection.num_entities
                print(f"\nNúmero de entidades: {count}")
            except Exception as e:
                print(f"Error al contar entidades: {e}")
                
            return True
        except Exception as e:
            print(f"Error al cargar la colección: {e}")
            return False
    except Exception as e:
        print(f"Error al verificar existencia de la colección: {e}")
        return False

def try_search_in_collection(collection_name, limit=5):
    """Intenta realizar una búsqueda simple en la colección."""
    print_separator(f"PRUEBA DE BÚSQUEDA EN: {collection_name}")
    
    try:
        collection = Collection(collection_name)
        
        # Verificar si la colección está cargada
        try:
            collection.load()
            print("Colección cargada correctamente")
        except Exception as e:
            print(f"Error al cargar la colección (puede que ya esté cargada): {e}")
        
        # Obtener dimensión del vector
        schema = collection.schema
        embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
        
        if not embedding_field:
            print("No se encontró campo 'embedding' en la colección")
            return False
            
        dim = embedding_field.dim
        print(f"Dimensión del vector: {dim}")
        
        # Vector de prueba (todo ceros)
        test_vector = [0.0] * dim
        
        # Parámetros de búsqueda
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Determinar campos de salida
        field_names = [field.name for field in schema.fields]
        output_fields = [f for f in field_names if f not in ["embedding"]]
        print(f"Campos de salida: {output_fields}")
        
        # Ejecutar búsqueda
        print("Ejecutando búsqueda...")
        results = collection.search(
            data=[test_vector],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=output_fields
        )
        
        # Mostrar resultados
        print(f"\nResultados encontrados: {len(results[0])}")
        for i, hit in enumerate(results[0]):
            print(f"\nResultado #{i+1}:")
            entity = hit.entity.to_dict()
            
            # Formatear campos principales
            if "text" in entity:
                print(f"- text: {entity['text'][:100]}..." if len(entity['text']) > 100 else entity['text'])
            
            if "title" in entity:
                print(f"- title: {entity['title']}")
                
            if "source_id" in entity:
                print(f"- source_id: {entity['source_id']}")
                
            # Mostrar puntuación
            print(f"- score: {hit.score}")
            
        return True
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return False

def main():
    """Función principal."""
    print("DIAGNÓSTICO DE MILVUS")
    print(f"Host: {MILVUS_HOST}")
    print(f"Puerto: {MILVUS_PORT}")
    print(f"Base de datos objetivo: {MILVUS_DATABASE}")
    print(f"Colección objetivo: {TARGET_COLLECTION}")
    
    # Conectar a Milvus
    if not connect_to_milvus():
        print("\n⚠️ No se pudo conectar a Milvus. Abortando diagnóstico.")
        return
    
    # Verificar bases de datos
    databases = check_databases()
    
    # Verificar colecciones
    collections = check_collections()
    
    # Verificar detalles de cada variante de colección
    for variant in COLLECTION_VARIANTS:
        if variant in collections:
            check_collection_details(variant)
            try_search_in_collection(variant)
    
    print_separator("DIAGNÓSTICO COMPLETO")
    print("Si necesitas ayuda para interpretar estos resultados, consulta:")
    print("https://milvus.io/docs/troubleshooting.md")

if __name__ == "__main__":
    main()
