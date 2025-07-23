from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    priority: TaskPriority
    status: TaskStatus
    user_id: str
    created_at: datetime
    updated_at: datetime

class User(BaseModel):
    id: str
    email: str
    created_at: datetime
