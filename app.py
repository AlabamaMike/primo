from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_client import SupabaseClient
from models import TaskCreate, TaskUpdate, UserCreate, UserLogin, TaskStatus, TaskPriority
from typing import Optional, Annotated
from datetime import date
import json

app = FastAPI(title="Primo Task Manager", description="A task management app with Supabase backend")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Supabase client
supabase_client = SupabaseClient()

# Security
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user from token"""
    if not credentials:
        return None
    
    try:
        # Verify token with Supabase
        user = supabase_client.get_user()
        return user
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(get_current_user)):
    """Home page - redirect to login if not authenticated"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle login form submission"""
    user_data = UserLogin(email=email, password=password)
    result = await supabase_client.sign_in(user_data)
    
    if result["success"]:
        # Redirect to dashboard on success
        response = RedirectResponse(url="/dashboard", status_code=302)
        return response
    else:
        # Return login page with error
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": result.get("error", "Login failed")
        })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle registration form submission"""
    user_data = UserCreate(email=email, password=password)
    result = await supabase_client.sign_up(user_data)
    
    if result["success"]:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "success": "Registration successful! Please check your email to verify your account, then login."
        })
    else:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": result.get("error", "Registration failed")
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_current_user)):
    """Main dashboard with tasks"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    tasks = await supabase_client.get_tasks(user["id"])
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "tasks": tasks,
        "TaskStatus": TaskStatus,
        "TaskPriority": TaskPriority
    })

@app.get("/tasks", response_class=HTMLResponse)
async def get_tasks_html(request: Request, user=Depends(get_current_user)):
    """Get tasks as HTML fragment for HTMX"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    tasks = await supabase_client.get_tasks(user["id"])
    return templates.TemplateResponse("partials/task_list.html", {
        "request": request, 
        "tasks": tasks,
        "TaskStatus": TaskStatus,
        "TaskPriority": TaskPriority
    })

@app.post("/tasks")
async def create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    due_date: Optional[str] = Form(None),
    priority: TaskPriority = Form(TaskPriority.MEDIUM),
    user=Depends(get_current_user)
):
    """Create a new task"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            parsed_due_date = None
    
    task_data = TaskCreate(
        title=title,
        description=description if description else None,
        due_date=parsed_due_date,
        priority=priority
    )
    
    result = await supabase_client.create_task(task_data, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await supabase_client.get_tasks(user["id"])
        return templates.TemplateResponse("partials/task_list.html", {
            "request": request, 
            "tasks": tasks,
            "TaskStatus": TaskStatus,
            "TaskPriority": TaskPriority
        })
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create task"))

@app.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_form(request: Request, task_id: int, user=Depends(get_current_user)):
    """Get edit form for a task"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    task = await supabase_client.get_task(task_id, user["id"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return templates.TemplateResponse("partials/task_edit_form.html", {
        "request": request, 
        "task": task,
        "TaskStatus": TaskStatus,
        "TaskPriority": TaskPriority
    })

@app.put("/tasks/{task_id}")
async def update_task(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    due_date: Optional[str] = Form(None),
    priority: TaskPriority = Form(...),
    status: TaskStatus = Form(...),
    user=Depends(get_current_user)
):
    """Update a task"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Parse due_date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = date.fromisoformat(due_date)
        except ValueError:
            parsed_due_date = None
    
    task_data = TaskUpdate(
        title=title,
        description=description if description else None,
        due_date=parsed_due_date,
        priority=priority,
        status=status
    )
    
    result = await supabase_client.update_task(task_id, task_data, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await supabase_client.get_tasks(user["id"])
        return templates.TemplateResponse("partials/task_list.html", {
            "request": request, 
            "tasks": tasks,
            "TaskStatus": TaskStatus,
            "TaskPriority": TaskPriority
        })
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update task"))

@app.delete("/tasks/{task_id}")
async def delete_task(request: Request, task_id: int, user=Depends(get_current_user)):
    """Delete a task"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await supabase_client.delete_task(task_id, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await supabase_client.get_tasks(user["id"])
        return templates.TemplateResponse("partials/task_list.html", {
            "request": request, 
            "tasks": tasks,
            "TaskStatus": TaskStatus,
            "TaskPriority": TaskPriority
        })
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete task"))

@app.post("/logout")
async def logout(user=Depends(get_current_user)):
    """Logout user"""
    if user:
        supabase_client.sign_out()
    return RedirectResponse(url="/login", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
