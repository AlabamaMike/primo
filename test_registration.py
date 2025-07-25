#!/usr/bin/env python3
"""
Test SQLite database functionality
"""

import asyncio
from database import SQLiteDatabase
from models import UserCreate

async def test_sqlite_database():
    """Test SQLite database functionality"""
    
    print("🧪 Testing SQLite database...")
    
    try:
        # Initialize database
        db = SQLiteDatabase()
        print("✅ SQLite database initialized")
        
        # Test connection
        if db.test_connection():
            print("✅ Database connection successful")
        
        # Test user data
        test_user = UserCreate(
            email="test@example.com",
            password="testpassword123"
        )
        
        print(f"📧 Testing registration for: {test_user.email}")
        
        # Attempt registration
        result = await db.sign_up(test_user)
        
        if result["success"]:
            print("✅ User registration test PASSED!")
            print("🎉 SQLite database is working perfectly!")
            
            # Try to login with the same user
            print("🔐 Testing login...")
            from models import UserLogin
            login_data = UserLogin(email=test_user.email, password=test_user.password)
            login_result = await db.sign_in(login_data)
            
            if login_result["success"]:
                print("✅ Login test PASSED!")
                print("� Database is ready for the application!")
            else:
                print(f"❌ Login failed: {login_result.get('error')}")
                
        else:
            print(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
            if "already exists" in result.get('error', ''):
                print("ℹ️  This is expected if you've run this test before")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_sqlite_database())
