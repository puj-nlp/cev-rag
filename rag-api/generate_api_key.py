#!/usr/bin/env python3
"""
API Key Generator

This script generates secure API keys for the RAG API.
Usage: python generate_api_key.py [--count N] [--length L]
"""

import secrets
import string
import argparse
import sys


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        length: Length of the API key (default: 32)
        
    Returns:
        A secure random API key string
    """
    # Use URL-safe characters (letters, digits, -, _)
    alphabet = string.ascii_letters + string.digits + '-_'
    api_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return api_key


def main():
    """Main function to handle command line arguments and generate API keys."""
    parser = argparse.ArgumentParser(description='Generate secure API keys for the RAG API')
    parser.add_argument(
        '--count', 
        type=int, 
        default=1, 
        help='Number of API keys to generate (default: 1)'
    )
    parser.add_argument(
        '--length', 
        type=int, 
        default=32, 
        help='Length of each API key (default: 32)'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default='',
        help='Prefix for the API keys (e.g., "prod_", "dev_")'
    )
    
    args = parser.parse_args()
    
    if args.count <= 0:
        print("Error: Count must be positive", file=sys.stderr)
        sys.exit(1)
        
    if args.length < 16:
        print("Error: Length must be at least 16 characters for security", file=sys.stderr)
        sys.exit(1)
    
    print(f"Generating {args.count} API key(s) with length {args.length}:")
    print("=" * 50)
    
    api_keys = []
    for i in range(args.count):
        api_key = args.prefix + generate_api_key(args.length)
        api_keys.append(api_key)
        print(f"API Key {i+1}: {api_key}")
    
    print("=" * 50)
    print("\nFor .env file format:")
    print(f"API_KEYS={','.join(api_keys)}")
    
    print("\nFor curl testing:")
    print(f"curl -H \"Authorization: Bearer {api_keys[0]}\" http://localhost:8000/api/")
    
    print("\nFor HTTP client testing:")
    print("Headers:")
    print(f"  Authorization: Bearer {api_keys[0]}")
    
    print("\n⚠️  SECURITY NOTES:")
    print("- Store these keys securely")
    print("- Do not commit them to version control")
    print("- Use environment variables or secure secret management")
    print("- Rotate keys regularly")


if __name__ == "__main__":
    main()
