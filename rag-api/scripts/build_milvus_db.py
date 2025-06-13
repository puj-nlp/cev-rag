import os
import json
import datetime
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, utility, Collection
from openai import OpenAI
import numpy as np

# Importar configuración
import sys
sys.path.append("..")
import config

# Configurar OpenAI
try:
    with open("../secrets.json", "r") as f:
        secrets = json.load(f)
        api_key = secrets.get("openai_api_key", config.OPENAI_API_KEY)
except Exception as e:
    print(f"No se pudo cargar secrets.json: {e}")
    api_key = config.OPENAI_API_KEY
    
client = OpenAI(api_key=api_key)

# Configurar rutas
DATA_DIR = "./data"
ABSTRACT_DATA_PATH = os.path.join(DATA_DIR, "processed_data.json")

def get_embedding(text, model=config.EMBEDDING_MODEL):
    """Obtiene el embedding de un texto usando OpenAI."""
    # Asegurarse de que el texto no es None o vacío
    if not text:
        text = "Contenido vacío"
    
    # Limpiar el texto
    text = text.replace("\n", " ").strip()
    
    # Usar el formato correcto para la API de OpenAI v1.0+
    try:
        response = client.embeddings.create(
            input=text,  # String simple, no lista
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error al generar embedding: {e}")
        # Retornar un vector de ceros como fallback
        # Usar la dimensión configurada en config.py
        return [0.0] * config.EMBEDDING_DIMENSION

def connect_to_milvus():
    """Conecta a Milvus."""
    try:
        connections.connect(
            alias="default", 
            host=config.MILVUS_HOST,
            port=config.MILVUS_PORT
        )
        # En versiones nuevas de pymilvus, verificamos la conexión de otra manera
        # is_connected ya no está disponible
        connections.get_connection_addr("default")
        print("Conectado a Milvus exitosamente")
        print(f"Se usará la colección: {config.ABSTRACT_COLLECTION}")
    except Exception as e:
        print(f"Error al conectar a Milvus: {e}")
        raise

def check_existing_collection_dimension(collection_name):
    """
    Verifica si una colección ya existe y obtiene su dimensión de embedding.
    
    Args:
        collection_name: Nombre de la colección a verificar
        
    Returns:
        int or None: La dimensión del vector de embedding si la colección existe, None en caso contrario
    """
    if not utility.has_collection(collection_name):
        return None
    
    try:
        collection = Collection(collection_name)
        schema = collection.schema
        for field in schema.fields:
            if field.name == "embedding" and hasattr(field, "dim"):
                print(f"Colección {collection_name} ya existe con dimensión de embedding: {field.dim}")
                return field.dim
    except Exception as e:
        print(f"Error al verificar dimensión de colección existente: {e}")
    
    return None

def create_collection(collection_name, dimension=config.EMBEDDING_DIMENSION):
    """Crea una colección en Milvus con el esquema específico."""
    # Verificar si la colección ya existe y obtener su dimensión
    existing_dimension = check_existing_collection_dimension(collection_name)
    
    # Si la colección ya existe, usar su dimensión en lugar de eliminarla
    if existing_dimension:
        print(f"Usando colección existente {collection_name} con dimensión {existing_dimension}")
        return Collection(collection_name)
    
    # Si la colección no existe o se decidió eliminarla, crear una nueva
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
        print(f"Se eliminó la colección existente: {collection_name}")
    
    print(f"Creando nueva colección {collection_name} con dimensión {dimension}")
    
    # Definir el esquema apropiado según la colección
    if collection_name == config.ABSTRACT_COLLECTION:
        # Esquema de source_abstract según la estructura definida en Milvus
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
        print(f"Creando colección {collection_name} con esquema específico para datos de la Comisión de la Verdad")
    else:
        # Esquema genérico para otras colecciones
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
        ]
        print(f"Creando colección {collection_name} con esquema genérico")
    
    schema = CollectionSchema(fields, f"Colección {collection_name}")
    collection = Collection(name=collection_name, schema=schema)
    print(f"Colección creada: {collection_name}")
    
    return collection

def load_data(filepath):
    """Carga datos desde un archivo JSON."""
    if not os.path.exists(filepath):
        print(f"El archivo {filepath} no existe")
        return []
    
    with open(filepath, "r") as f:
        data = json.load(f)
    
    print(f"Se cargaron {len(data)} documentos de {filepath}")
    return data

def process_and_insert_data(collection, data, start_id=0):
    """Procesa los datos y los inserta en la colección según su esquema."""
    # Determinar tamaño de lote para procesar e insertar por partes
    batch_size = 100  # Ajustar según sea necesario
    batch_count = (len(data) + batch_size - 1) // batch_size
    
    print("Generando embeddings... (puede tardar varios minutos)")
    
    # Contador para todos los documentos procesados
    processed_count = 0
    
    # Determinar el esquema de la colección
    collection_schema = collection.schema
    field_names = [field.name for field in collection_schema.fields]
    is_source_abstract = "text" in field_names and "source_id" in field_names
    
    for batch_idx in range(batch_count):
        batch_start = batch_idx * batch_size
        batch_end = min((batch_idx + 1) * batch_size, len(data))
        batch_items = list(data.values())[batch_start:batch_end] if isinstance(data, dict) else data[batch_start:batch_end]
        
        # Inicializar listas para este lote según el esquema
        batch_data = {"id": []}  # ID siempre está presente
        
        # Inicializar listas según el esquema
        for field in field_names:
            if field != "id":  # ID ya está inicializado
                batch_data[field] = []
        
        print(f"Procesando lote {batch_idx+1}/{batch_count} (documentos {batch_start+1}-{batch_end})")
        
        for i, item in enumerate(batch_items):
            if i % 10 == 0:
                print(f"Procesando documento {batch_start+i+1}/{len(data)}")
            
            # Generar el embedding primero para verificar si podemos continuar
            text_content = ""
            if "Text" in item:
                text_content = item["Text"]
            elif "text" in item:
                text_content = item["text"]
            elif "content" in item:
                text_content = item["content"]
            
            if not text_content:
                print(f"Saltando documento #{batch_start+i+1} - sin contenido")
                continue
                
            try:
                embedding = get_embedding(text_content)
                
                # Agregar ID a la lista de datos
                batch_data["id"].append(start_id + processed_count)
                batch_data["embedding"].append(embedding)
                
                # Procesar datos según el esquema de la colección
                if is_source_abstract:
                    # Esquema para source_abstract
                    batch_data["text"].append(text_content)
                    batch_data["title"].append(item.get("Title", "") or item.get("title", ""))
                    batch_data["source_id"].append(item.get("ID", "") or item.get("source_id", ""))
                    batch_data["type"].append(item.get("Type", "") or item.get("type", ""))
                    batch_data["link"].append(item.get("Link", "") or item.get("link", ""))
                    batch_data["page"].append(int(item.get("Page", 0) or item.get("page", 0) or 0))
                    
                    # Campos dinámicos como JSON
                    dynamic_data = {}
                    for k, v in item.items():
                        if k not in ["Text", "Title", "ID", "Type", "Link", "Page", "text", "title", "source_id", "type", "link", "page"]:
                            dynamic_data[k] = v
                    batch_data["dynamic_field"].append(dynamic_data)
                else:
                    # Esquema para otras colecciones (contenido y metadata)
                    content = text_content
                    batch_data["content"].append(content)
                    
                    # Construir metadata como JSON
                    metadata = {}
                    for k, v in item.items():
                        if k not in ["content", "text"]:
                            metadata[k] = v
                    batch_data["metadata"].append(json.dumps(metadata))
                
                processed_count += 1
            except Exception as e:
                print(f"Error procesando documento #{batch_start+i+1}: {e}")
        
        # Si tenemos datos en este lote, insertarlos
        if batch_data["id"]:
            try:
                collection.insert(batch_data)
                print(f"Lote {batch_idx+1}/{batch_count} insertado: {len(batch_data['id'])} documentos")
            except Exception as e:
                print(f"Error al insertar lote {batch_idx+1}: {e}")
    
    return processed_count  # Devolver el número total de documentos procesados

def create_index_and_load(collection):
    """Crea un índice y carga la colección en memoria."""
    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 8, "efConstruction": 200}
    }
    
    collection.create_index("embedding", index_params)
    print("Índice creado")
    
    collection.load()
    print(f"Colección cargada con {collection.num_entities} entidades")

def main():
    # Conectar a Milvus
    connect_to_milvus()
    
    # Flag para saber si se creó alguna colección
    created_collection = False
    
    # Verificar si hay alguna ruta alternativa de datos
    # Por si el archivo está en la raíz del proyecto o si hay datos transformados
    if not os.path.exists(ABSTRACT_DATA_PATH):
        alt_paths = [
            "./processed_data.json",
            "../processed_data.json",
            os.path.join(DATA_DIR, "abstracts_data.json"),
            os.path.join(DATA_DIR, "transformed_processed_data.json"),  # Buscar datos transformados
        ]
        for path in alt_paths:
            if os.path.exists(path):
                print(f"Usando ruta alternativa para datos: {path}")
                abstract_data_path = path
                break
    else:
        abstract_data_path = ABSTRACT_DATA_PATH
    
    # Cargar datos de processed_data.json
    abstract_data = load_data(abstract_data_path)
    if abstract_data:
        # Crear la colección
        abstract_collection = create_collection(config.ABSTRACT_COLLECTION)
        
        # Procesar e insertar datos
        docs_processed = process_and_insert_data(abstract_collection, abstract_data)
        print(f"Total de documentos procesados: {docs_processed}")
        
        # Crear índice y cargar la colección
        create_index_and_load(abstract_collection)
        created_collection = True
    
    # Si no se encontró ningún dato para importar, crear una colección vacía como fallback
    if not created_collection:
        print("No se encontraron datos para importar. Creando colección vacía como fallback...")
        fallback_collection = create_collection(config.ABSTRACT_COLLECTION)
        
        # Crear un documento de ejemplo para asegurar que la colección funcione
        sample_data = [{
            "content": "Este es un documento de ejemplo para la colección de la Comisión de la Verdad sobre el conflicto colombiano.",
            "source": "sample_document"
        }]
        process_and_insert_data(fallback_collection, sample_data)
        create_index_and_load(fallback_collection)
        print("Colección fallback creada y cargada con un documento de ejemplo.")
    
    # Desconectar
    connections.disconnect("default")
    print("Desconectado de Milvus")
    
    # Crear archivo de registro
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
    
    print("Proceso completado y registro guardado.")

if __name__ == "__main__":
    main()
