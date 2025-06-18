"""Milvus implementation of VectorDatabase port."""

from typing import List, Optional
from pymilvus import connections, Collection, utility, db

from ...domain.entities import Document
from ...domain.ports import VectorDatabase


class MilvusVectorDatabase(VectorDatabase):
    """Milvus implementation of vector database."""
    
    def __init__(
        self, 
        host: str, 
        port: str, 
        database: str, 
        collection_name: str,
        alternative_names: List[str]
    ):
        self._host = host
        self._port = port
        self._database = database
        self._collection_name = collection_name
        self._alternative_names = alternative_names
        self._collection: Optional[Collection] = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection to Milvus."""
        try:
            connections.connect(
                alias="default",
                host=self._host,
                port=self._port
            )
            print(f"Successfully connected to Milvus at {self._host}:{self._port}")
            
            # Try to select the database
            try:
                db.using_database(self._database)
                print(f"Database {self._database} selected")
            except Exception as e:
                print(f"Note: Could not select database {self._database}: {e}")
                print("This is normal in older versions of Milvus")
            
            self._collection = self._get_collection()
            
        except Exception as e:
            print(f"Error connecting to Milvus: {e}")
            raise
    
    def _get_collection(self) -> Collection:
        """Get the collection instance."""
        # List available collections
        collections = utility.list_collections()
        print(f"Available collections: {collections}")
        
        # Try different collection name formats
        candidates = [self._collection_name] + self._alternative_names
        
        for candidate in candidates:
            if candidate in collections:
                print(f"Found collection: {candidate}")
                collection = Collection(name=candidate)
                
                # Get schema information to verify embedding dimension
                schema = collection.schema
                embedding_field = next((field for field in schema.fields if field.name == "embedding"), None)
                
                if embedding_field:
                    expected_dim = embedding_field.dim
                    print(f"Collection {candidate} expects embedding dimension: {expected_dim}")
                    
                    # Store the expected dimension for later use
                    self._expected_dimension = expected_dim
                
                # Verify the collection has data
                entity_count = collection.num_entities
                print(f"Collection {candidate} has {entity_count} entities")
                
                if entity_count > 0:
                    return collection
        
        raise ValueError(f"No valid collection found among: {candidates}")
    
    @property
    def expected_dimension(self) -> int:
        """Get the expected embedding dimension for this collection."""
        return getattr(self, '_expected_dimension', 1536)
    
    async def search_similar_documents(self, embedding: List[float], limit: int = 5) -> List[Document]:
        """Search for similar documents using vector similarity."""
        if not self._collection:
            raise ValueError("Collection not initialized")
        
        # Validate embedding dimension
        expected_dim = self.expected_dimension
        actual_dim = len(embedding)
        
        if actual_dim != expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: collection expects {expected_dim} dimensions "
                f"but received {actual_dim} dimensions. Please check your embedding model configuration."
            )
        
        try:
            # Load collection if not already loaded
            self._collection.load()
            
            # Get schema to determine output fields
            schema = self._collection.schema
            output_fields = [field.name for field in schema.fields if field.name != "embedding"]
            
            print(f"Searching with embedding dimension: {len(embedding)}")
            
            # Perform the search
            search_results = self._collection.search(
                data=[embedding],
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=limit,
                output_fields=output_fields
            )
            
            documents = []
            for hit in search_results[0]:
                doc_dict = hit.entity.to_dict()
                
                # Extract content and metadata
                content = self._extract_content(doc_dict)
                metadata = self._extract_metadata(doc_dict)
                
                document = Document(
                    content=content,
                    metadata=metadata,
                    score=hit.score,
                    original_fields=doc_dict
                )
                documents.append(document)
            
            print(f"Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise
    
    def _extract_content(self, doc_dict: dict) -> str:
        """Extract content from document dictionary."""
        # Try different content field names
        content_fields = ["content", "text", "abstract", "body"]
        
        for field in content_fields:
            if field in doc_dict and doc_dict[field]:
                return str(doc_dict[field])
        
        # If no content field found, try to use title
        if "title" in doc_dict and doc_dict["title"]:
            return f"Document titled: {doc_dict['title']}"
        
        return "No content available"
    
    def _extract_metadata(self, doc_dict: dict) -> dict:
        """Extract metadata from document dictionary."""
        metadata = {}
        
        # Standard metadata fields
        metadata_fields = ["title", "source_id", "page", "link", "author", "date"]
        
        for field in metadata_fields:
            if field in doc_dict:
                metadata[field] = doc_dict[field]
        
        return metadata
    
    async def verify_connection(self) -> bool:
        """Verify database connection."""
        try:
            conn_status = connections.get_connection_addr("default")
            print(f"Milvus connection status: {conn_status}")
            return True
        except Exception as e:
            print(f"Error verifying connection: {e}")
            return False
