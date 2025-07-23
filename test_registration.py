#!/usr/bin/env python3
"""
Test user registration to identify SSL issues
"""

import nuclear_ssl_bypass  # Import first

import os
import asyncio
from supabase_client import SupabaseClient
from models import UserCreate

async def test_user_registration():
    """Test user registration functionality"""
    
    print("🧪 Testing user registration...")
    
    try:
        # Initialize Supabase client
        client = SupabaseClient()
        print("✅ Supabase client initialized")
        
        # Test user data
        test_user = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        
        print(f"📧 Testing registration for: {test_user.email}")
        
        # Attempt registration
        result = await client.sign_up(test_user)
        
        if result["success"]:
            print("✅ User registration test PASSED!")
            print("🎉 No SSL errors detected!")
        else:
            print(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ SSL Error detected: {e}")
        print("\n🔧 Additional fixes may be needed...")
        
        # Check if it's specifically an SSL error
        if "SSL" in str(e) or "certificate" in str(e).lower():
            print("🚨 This is indeed an SSL certificate error")
            print("💡 Recommended actions:")
            print("1. Restart Windows")
            print("2. Run as Administrator")
            print("3. Update Windows certificates")
            print("4. Try a different network")
        
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_user_registration())
