"""Authentication and authorization utilities for the API."""

import os
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security scheme for bearer token
security = HTTPBearer(auto_error=False)


class APIKeyManager:
    """Manages API key validation."""
    
    def __init__(self):
        # Get API keys from environment variables
        # You can have multiple API keys separated by commas
        api_keys_str = os.getenv("API_KEYS", "")
        self.valid_api_keys = set(
            key.strip() for key in api_keys_str.split(",") if key.strip()
        )
        
        # If no API keys are configured, disable authentication
        self.auth_enabled = len(self.valid_api_keys) > 0
        
        if not self.auth_enabled:
            print("⚠️  No API keys configured. Authentication is disabled.")
            print("   Set API_KEYS environment variable to enable authentication.")
        else:
            print(f"✅ API authentication enabled with {len(self.valid_api_keys)} valid key(s)")
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate if the provided API key is valid."""
        if not self.auth_enabled:
            return True
        return api_key in self.valid_api_keys


# Global instance
api_key_manager = APIKeyManager()


def get_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Dependency to validate API key from Authorization header.
    
    Expected format: Authorization: Bearer YOUR_API_KEY
    """
    # If authentication is disabled, allow access
    if not api_key_manager.auth_enabled:
        return "no-auth"
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide Authorization header with Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    if not api_key_manager.validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


def require_api_key(
    api_key: str = Depends(get_api_key)
) -> str:
    """
    Dependency that enforces API key authentication.
    Use this as a dependency in your route handlers.
    """
    return api_key
