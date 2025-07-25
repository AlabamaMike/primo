import sqlite3
import hashlib
import secrets
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path
from models import Task, TaskCreate, TaskUpdate, UserCreate, UserLogin

class SQLiteDatabase:
    def __init__(self, db_path: str = "primo.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date DATE,
                    priority TEXT NOT NULL DEFAULT 'medium',
                    status TEXT NOT NULL DEFAULT 'todo',
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
            ''')
            
            conn.commit()
        
        print("✅ SQLite database initialized successfully")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + password_hash.hex()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        salt = password_hash[:32]  # First 32 chars are salt
        stored_hash = password_hash[32:]  # Rest is the hash
        password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash_check.hex() == stored_hash
    
    def _generate_user_id(self) -> str:
        """Generate a unique user ID"""
        return secrets.token_urlsafe(16)
    
    # User Authentication Methods
    async def sign_up(self, user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user"""
        try:
            user_id = self._generate_user_id()
            password_hash = self._hash_password(user_data.password)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)',
                    (user_id, user_data.email, password_hash)
                )
                conn.commit()
            
            return {
                "success": True,
                "data": {
                    "user": {
                        "id": user_id,
                        "email": user_data.email,
                        "created_at": datetime.now()
                    }
                }
            }
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Email already exists"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def sign_in(self, user_data: UserLogin) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM users WHERE email = ?',
                    (user_data.email,)
                )
                user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid email or password"}
            
            if not self._verify_password(user_data.password, user['password_hash']):
                return {"success": False, "error": "Invalid email or password"}
            
            return {
                "success": True,
                "data": {
                    "user": {
                        "id": user['id'],
                        "email": user['email'],
                        "created_at": user['created_at']
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT id, email, created_at FROM users WHERE id = ?',
                    (user_id,)
                )
                user = cursor.fetchone()
                
                if user:
                    return dict(user)
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    # Task Management Methods
    async def create_task(self, task_data: TaskCreate, user_id: str) -> Dict[str, Any]:
        """Create a new task"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    '''INSERT INTO tasks (title, description, due_date, priority, status, user_id) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        task_data.title,
                        task_data.description,
                        task_data.due_date.isoformat() if task_data.due_date else None,
                        task_data.priority.value,
                        task_data.status.value,
                        user_id
                    )
                )
                task_id = cursor.lastrowid
                conn.commit()
                
                # Return the created task
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM tasks WHERE id = ?',
                    (task_id,)
                )
                task = cursor.fetchone()
                
                return {"success": True, "data": dict(task)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC',
                    (user_id,)
                )
                tasks = cursor.fetchall()
                
                # Convert to list of dictionaries and parse dates
                task_list = []
                for task in tasks:
                    task_dict = dict(task)
                    # Parse due_date if it exists
                    if task_dict['due_date']:
                        task_dict['due_date'] = datetime.fromisoformat(task_dict['due_date']).date()
                    # Parse timestamps
                    task_dict['created_at'] = datetime.fromisoformat(task_dict['created_at'])
                    task_dict['updated_at'] = datetime.fromisoformat(task_dict['updated_at'])
                    task_list.append(task_dict)
                
                return task_list
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    async def get_task(self, task_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                    (task_id, user_id)
                )
                task = cursor.fetchone()
                
                if task:
                    task_dict = dict(task)
                    if task_dict['due_date']:
                        task_dict['due_date'] = datetime.fromisoformat(task_dict['due_date']).date()
                    task_dict['created_at'] = datetime.fromisoformat(task_dict['created_at'])
                    task_dict['updated_at'] = datetime.fromisoformat(task_dict['updated_at'])
                    return task_dict
                return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    async def update_task(self, task_id: int, task_data: TaskUpdate, user_id: str) -> Dict[str, Any]:
        """Update a task"""
        try:
            # Build update query dynamically based on provided fields
            update_fields = []
            values = []
            
            if task_data.title is not None:
                update_fields.append("title = ?")
                values.append(task_data.title)
            
            if task_data.description is not None:
                update_fields.append("description = ?")
                values.append(task_data.description)
            
            if task_data.due_date is not None:
                update_fields.append("due_date = ?")
                values.append(task_data.due_date.isoformat() if task_data.due_date else None)
            
            if task_data.priority is not None:
                update_fields.append("priority = ?")
                values.append(task_data.priority.value)
            
            if task_data.status is not None:
                update_fields.append("status = ?")
                values.append(task_data.status.value)
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            values.extend([task_id, user_id])
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?",
                    values
                )
                conn.commit()
                
                # Return the updated task
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                    (task_id, user_id)
                )
                task = cursor.fetchone()
                
                if task:
                    return {"success": True, "data": dict(task)}
                else:
                    return {"success": False, "error": "Task not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def delete_task(self, task_id: int, user_id: str) -> Dict[str, Any]:
        """Delete a task"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'DELETE FROM tasks WHERE id = ? AND user_id = ?',
                    (task_id, user_id)
                )
                conn.commit()
                
                if cursor.rowcount > 0:
                    return {"success": True, "data": {"deleted": task_id}}
                else:
                    return {"success": False, "error": "Task not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_connection(self):
        """Test the database connection"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT 1')
                result = cursor.fetchone()
                print("✅ Successfully connected to SQLite database!")
                return True
        except Exception as e:
            print(f"❌ Failed to connect to SQLite database: {e}")
            return False
