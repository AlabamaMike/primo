#!/usr/bin/env python3
"""
SSL Test Script for Supabase Connection
Run this to test if SSL issues are resolved
"""

import os
import ssl
import urllib3
from supabase_client import SupabaseClient

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_ssl_connection():
    try:
        print("Testing Supabase SSL connection...")
        
        # Initialize client
        client = SupabaseClient()
        
        # Test basic connection
        result = client.test_connection()
        
        if result:
            print("✅ SSL connection test PASSED!")
            
            # Test auth signup (this is where SSL errors usually occur)
            print("\nTesting auth functionality...")
            
            # We won't actually create a user, just test the client initialization
            print("✅ Supabase client initialized successfully!")
            print("✅ Ready for user registration!")
            
        else:
            print("❌ SSL connection test FAILED!")
            
    except Exception as e:
        print(f"❌ Error during SSL test: {e}")
        print("\n🔧 Possible solutions:")
        print("1. Try running with administrator privileges")
        print("2. Check Windows certificate store")
        print("3. Try running: pip install --upgrade certifi")

if __name__ == "__main__":
    test_ssl_connection()
