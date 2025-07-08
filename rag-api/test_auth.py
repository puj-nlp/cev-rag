#!/usr/bin/env python3
"""
Test script for API authentication.

This script tests the API endpoints with and without authentication
to verify that the API key protection is working correctly.
"""

import requests
import json
import sys
import os
from typing import Optional


class APITester:
    """Test API authentication functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
    
    def test_health_check(self) -> bool:
        """Test health check endpoint (should not require auth)."""
        print("🏥 Testing health check endpoint...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("  ✅ Health check successful (no auth required)")
                return True
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Health check error: {e}")
            return False
    
    def test_protected_endpoint(self) -> bool:
        """Test a protected endpoint."""
        print("🔒 Testing protected endpoint (list chats)...")
        try:
            response = self.session.get(f"{self.base_url}/chats")
            if response.status_code == 200:
                print("  ✅ Protected endpoint accessible with API key")
                return True
            elif response.status_code == 401:
                print("  ❌ Unauthorized - check your API key")
                print(f"  Response: {response.json()}")
                return False
            else:
                print(f"  ❌ Unexpected status code: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"  ❌ Protected endpoint error: {e}")
            return False
    
    def test_without_auth(self) -> bool:
        """Test protected endpoint without authentication."""
        print("🚫 Testing protected endpoint without authentication...")
        try:
            response = requests.get(f"{self.base_url}/chats")
            if response.status_code == 401:
                print("  ✅ Correctly rejected request without API key")
                return True
            elif response.status_code == 200:
                print("  ⚠️  WARNING: Protected endpoint accessible without auth!")
                print("  This might mean authentication is disabled.")
                return False
            else:
                print(f"  ❌ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            return False
    
    def test_invalid_api_key(self) -> bool:
        """Test with invalid API key."""
        print("🔑 Testing with invalid API key...")
        try:
            headers = {'Authorization': 'Bearer invalid_key_123'}
            response = requests.get(f"{self.base_url}/chats", headers=headers)
            if response.status_code == 401:
                print("  ✅ Correctly rejected invalid API key")
                return True
            elif response.status_code == 200:
                print("  ⚠️  WARNING: Invalid API key was accepted!")
                return False
            else:
                print(f"  ❌ Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all authentication tests."""
        print("🧪 Running API authentication tests...\n")
        
        tests = [
            self.test_health_check(),
            self.test_without_auth(),
            self.test_invalid_api_key(),
        ]
        
        if self.api_key:
            tests.append(self.test_protected_endpoint())
        else:
            print("🔑 No API key provided - skipping authenticated tests")
        
        print("\n" + "="*50)
        passed = sum(tests)
        total = len(tests)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed!")
            return False


def main():
    """Main function to run the tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test API authentication')
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key to test with (can also use API_KEY environment variable)'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000/api',
        help='Base URL of the API (default: http://localhost:8000/api)'
    )
    
    args = parser.parse_args()
    
    # Get API key from command line or environment
    api_key = args.api_key or os.getenv('API_KEY')
    
    if not api_key:
        print("⚠️  No API key provided. Only testing unauthenticated endpoints.")
        print("   Use --api-key or set API_KEY environment variable for full testing.")
        print()
    
    tester = APITester(args.url, api_key)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
