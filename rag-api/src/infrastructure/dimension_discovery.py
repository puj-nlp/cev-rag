"""Service for discovering and adjusting embedding dimensions based on Milvus collection."""

from typing import Optional
from pymilvus import Collection, utility, connections, db


class DimensionDiscoveryService:
    """Service to discover the correct embedding dimension from Milvus collection."""
    
    def __init__(self, host: str, port: str, database: str, collection_names: list):
        self.host = host
        self.port = port
        self.database = database
        self.collection_names = collection_names
        self._discovered_dimension: Optional[int] = None
    
    def discover_dimension(self) -> int:
        """Discover the embedding dimension from the Milvus collection."""
        if self._discovered_dimension is not None:
            return self._discovered_dimension
        
        try:
            # Connect to Milvus
            connections.connect(alias="discovery", host=self.host, port=self.port)
            
            # Try to select database
            try:
                db.using_database(self.database)
                print(f"Using database: {self.database}")
            except Exception as e:
                print(f"Could not select database {self.database}: {e}")
            
            # List available collections
            collections = utility.list_collections()
            print(f"Available collections: {collections}")
            
            # Try to find a collection and get its dimension
            for collection_name in self.collection_names:
                if collection_name in collections:
                    try:
                        collection = Collection(name=collection_name)
                        schema = collection.schema
                        
                        # Find embedding field
                        embedding_field = next(
                            (field for field in schema.fields if field.name == "embedding"), 
                            None
                        )
                        
                        if embedding_field:
                            dimension = embedding_field.dim
                            print(f"Discovered embedding dimension from collection {collection_name}: {dimension}")
                            self._discovered_dimension = dimension
                            return dimension
                    
                    except Exception as e:
                        print(f"Error accessing collection {collection_name}: {e}")
                        continue
            
            # Default fallback
            print("Could not discover dimension from collections, using default: 3072")
            self._discovered_dimension = 3072
            return self._discovered_dimension
        
        except Exception as e:
            print(f"Error during dimension discovery: {e}")
            # Return default dimension
            return 3072
        
        finally:
            # Clean up connection
            try:
                connections.disconnect(alias="discovery")
            except:
                pass
    
    def get_recommended_model(self, dimension: int) -> str:
        """Get recommended OpenAI model based on dimension."""
        if dimension == 1536:
            return "text-embedding-3-small"
        elif dimension == 3072:
            return "text-embedding-3-large"
        elif dimension == 256:
            return "text-embedding-3-small"  # Can specify 256 dimensions
        elif dimension == 512:
            return "text-embedding-3-small"  # Can specify 512 dimensions
        else:
            # For other dimensions, try text-embedding-3-large (supports 256-3072)
            if 256 <= dimension <= 3072:
                return "text-embedding-3-large"
            else:
                print(f"Warning: Unusual dimension {dimension}, using text-embedding-3-large")
                return "text-embedding-3-large"
