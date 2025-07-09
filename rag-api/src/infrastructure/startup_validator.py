"""Startup validation service for checking system compatibility."""

import asyncio
from typing import Dict, Any

from ..infrastructure.dependencies import get_vector_database, get_embedding_service
from ..infrastructure.config import config_service


class StartupValidator:
    """Service to validate system configuration at startup."""
    
    @staticmethod
    async def validate_system() -> Dict[str, Any]:
        """Validate the entire system configuration."""
        results = {
            "status": "success",
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        # Check Milvus connection
        try:
            vector_db = get_vector_database()
            connection_ok = await vector_db.verify_connection()
            results["checks"]["milvus_connection"] = connection_ok
            
            if not connection_ok:
                results["errors"].append("Could not connect to Milvus database")
                results["status"] = "error"
            
        except Exception as e:
            results["checks"]["milvus_connection"] = False
            results["errors"].append(f"Milvus connection error: {str(e)}")
            results["status"] = "error"
        
        # Check embedding dimension compatibility
        try:
            vector_db = get_vector_database()
            embedding_service = get_embedding_service()
            
            # Get expected dimension from collection
            expected_dim = vector_db.expected_dimension
            
            # Get configured dimension
            configured_dim = config_service.openai.embedding_dimension
            
            results["checks"]["dimension_compatibility"] = expected_dim == configured_dim
            results["checks"]["expected_dimension"] = expected_dim
            results["checks"]["configured_dimension"] = configured_dim
            
            if expected_dim != configured_dim:
                results["warnings"].append(
                    f"Dimension mismatch: collection expects {expected_dim}, "
                    f"but service configured for {configured_dim}"
                )
            
        except Exception as e:
            results["checks"]["dimension_compatibility"] = False
            results["errors"].append(f"Dimension check error: {str(e)}")
            if results["status"] != "error":
                results["status"] = "warning"
        
        # Test embedding generation
        try:
            embedding_service = get_embedding_service()
            test_embedding = await embedding_service.generate_embedding("test")
            results["checks"]["embedding_generation"] = True
            results["checks"]["actual_embedding_dimension"] = len(test_embedding)
            
        except Exception as e:
            results["checks"]["embedding_generation"] = False
            results["errors"].append(f"Embedding generation error: {str(e)}")
            results["status"] = "error"
        
        return results
    
    @staticmethod
    def print_validation_results(results: Dict[str, Any]):
        """Print validation results in a readable format."""
        print("\n=== SYSTEM VALIDATION RESULTS ===")
        print(f"Overall Status: {results['status'].upper()}")
        
        print("\nChecks:")
        for check, result in results["checks"].items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}: {result}")
        
        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"]:
                print(f"  ⚠️  {warning}")
        
        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  ❌ {error}")
        
        print("=================================\n")
