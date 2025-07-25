from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import SQLiteDatabase
from models import TaskCreate, TaskUpdate, UserCreate, UserLogin, TaskStatus, TaskPriority
from typing import Optional, Annotated
from datetime import date
import secrets
import csv
import io

app = FastAPI(title="Primo Task Manager", description="A task management app with SQLite backend")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# SQLite database
db = SQLiteDatabase()

# Simple session management
sessions: dict = {}

def create_session(user_id: str) -> str:
    """Create a new session for a user"""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = user_id
    return session_id

def get_current_user(session_id: Optional[str] = Cookie(None)):
    """Get current user from session"""
    if not session_id or session_id not in sessions:
        return None
    
    user_id = sessions[session_id]
    return db.get_user_by_id(user_id)

def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]

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
    result = await db.sign_in(user_data)
    
    if result["success"]:
        # Create session and redirect to dashboard
        session_id = create_session(result["data"]["user"]["id"])
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
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
    result = await db.sign_up(user_data)
    
    if result["success"]:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "success": "Registration successful! You can now login with your credentials."
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
    
    tasks = await db.get_tasks(user["id"])
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
    
    tasks = await db.get_tasks(user["id"])
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
    
    result = await db.create_task(task_data, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await db.get_tasks(user["id"])
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
    
    task = await db.get_task(task_id, user["id"])
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
    
    result = await db.update_task(task_id, task_data, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await db.get_tasks(user["id"])
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
    
    result = await db.delete_task(task_id, user["id"])
    
    if result["success"]:
        # Return updated task list
        tasks = await db.get_tasks(user["id"])
        return templates.TemplateResponse("partials/task_list.html", {
            "request": request, 
            "tasks": tasks,
            "TaskStatus": TaskStatus,
            "TaskPriority": TaskPriority
        })
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete task"))

@app.get("/export/csv")
async def export_tasks_csv(user=Depends(get_current_user)):
    """Export user's tasks as CSV file"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get all tasks for the user
    tasks = await db.get_tasks(user["id"])
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV headers
    writer.writerow([
        'Title', 
        'Description', 
        'Due Date', 
        'Priority', 
        'Status', 
        'Created At', 
        'Updated At'
    ])
    
    # Write task data
    for task in tasks:
        writer.writerow([
            task.get('title', ''),
            task.get('description', ''),
            task.get('due_date', ''),
            task.get('priority', '').title(),
            task.get('status', '').replace('_', ' ').title(),
            task.get('created_at', ''),
            task.get('updated_at', '')
        ])
    
    # Create response
    csv_content = output.getvalue()
    output.close()
    
    # Create filename with current date
    from datetime import datetime
    filename = f"tasks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Return CSV file as download
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/logout")
async def logout(request: Request, session_id: Optional[str] = Cookie(None)):
    """Logout user"""
    if session_id:
        delete_session(session_id)
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="session_id")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
