# Import nuclear SSL bypass configuration first
import nuclear_ssl_bypass

import os
import ssl
import urllib3
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from models import Task, TaskCreate, TaskUpdate, UserCreate, UserLogin

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        # Create Supabase client
        try:
            self.client: Client = create_client(self.url, self.key)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        return self.client
    
    def test_connection(self):
        """Test the connection to Supabase"""
        try:
            # Simple query to test connection - this will work even if no tables exist
            response = self.client.auth.get_session()
            print("✅ Successfully connected to Supabase!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False
    
    # Auth methods
    async def sign_up(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, user_data: UserLogin) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_out(self) -> Dict[str, Any]:
        """Sign out the current user"""
        try:
            response = self.client.auth.sign_out()
            return {"success": True, "data": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user(self) -> Optional[Dict[str, Any]]:
        """Get current user"""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    # Task methods
    async def create_task(self, task_data: TaskCreate, user_id: str) -> Dict[str, Any]:
        """Create a new task"""
        try:
            task_dict = task_data.dict()
            task_dict["user_id"] = user_id
            
            response = self.client.table("tasks").insert(task_dict).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        try:
            response = self.client.table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    async def get_task(self, task_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        try:
            response = self.client.table("tasks").select("*").eq("id", task_id).eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    async def update_task(self, task_id: int, task_data: TaskUpdate, user_id: str) -> Dict[str, Any]:
        """Update a task"""
        try:
            # Only include non-None values in the update
            update_dict = {k: v for k, v in task_data.dict().items() if v is not None}
            
            response = self.client.table("tasks").update(update_dict).eq("id", task_id).eq("user_id", user_id).execute()
            return {"success": True, "data": response.data[0] if response.data else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_task(self, task_id: int, user_id: str) -> Dict[str, Any]:
        """Delete a task"""
        try:
            response = self.client.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
