from fastapi import FastAPI, Request, Form, HTTPException, Depends, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import SQLiteDatabase
from models import TaskCreate, TaskUpdate, UserCreate, UserLogin, TaskStatus, TaskPriority
from typing import Optional, Annotated
from datetime import date, datetime, timedelta
import secrets
import csv
import io
from collections import defaultdict

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

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, user=Depends(get_current_user)):
    """Reports dashboard"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all tasks for analysis
    tasks = await db.get_tasks(user["id"])
    
    # Task Status Report
    status_counts = defaultdict(int)
    priority_counts = defaultdict(int)
    overdue_count = 0
    today = date.today()
    
    # Task Aging Analysis
    aging_buckets = {
        "0-7 days": 0,
        "8-30 days": 0,
        "31-90 days": 0,
        "90+ days": 0
    }
    
    for task in tasks:
        # Count by status
        status_display = task.get('status', '').replace('_', ' ').title()
        status_counts[status_display] += 1
        
        # Count by priority
        priority_display = task.get('priority', '').title()
        priority_counts[priority_display] += 1
        
        # Check for overdue tasks
        due_date_str = task.get('due_date')
        if due_date_str and task.get('status') != 'completed':
            try:
                if isinstance(due_date_str, str):
                    due_date = datetime.fromisoformat(due_date_str).date()
                elif isinstance(due_date_str, date):
                    due_date = due_date_str
                else:
                    continue
                
                if due_date < today:
                    overdue_count += 1
            except (ValueError, AttributeError, TypeError):
                pass
        
        # Calculate task age
        created_at_data = task.get('created_at', '')
        if created_at_data:
            try:
                if isinstance(created_at_data, str):
                    created_at = datetime.fromisoformat(created_at_data.replace('Z', '+00:00'))
                elif isinstance(created_at_data, datetime):
                    created_at = created_at_data
                else:
                    continue
                    
                age_days = (datetime.now() - created_at).days
                
                if age_days <= 7:
                    aging_buckets["0-7 days"] += 1
                elif age_days <= 30:
                    aging_buckets["8-30 days"] += 1
                elif age_days <= 90:
                    aging_buckets["31-90 days"] += 1
                else:
                    aging_buckets["90+ days"] += 1
            except (ValueError, AttributeError, TypeError):
                pass
    
    # Completion rate calculation
    total_tasks = len(tasks)
    completed_tasks = status_counts.get('Completed', 0)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user,
        "total_tasks": total_tasks,
        "status_counts": dict(status_counts),
        "priority_counts": dict(priority_counts),
        "overdue_count": overdue_count,
        "completion_rate": round(completion_rate, 1),
        "aging_buckets": aging_buckets,
        "tasks": tasks,
        "TaskStatus": TaskStatus,
        "TaskPriority": TaskPriority
    })

@app.get("/reports/export", response_class=HTMLResponse)
async def export_reports(request: Request, user=Depends(get_current_user)):
    """Export reports as CSV"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get all tasks for analysis
    tasks = await db.get_tasks(user["id"])
    
    # Create CSV content for detailed report
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write report headers
    writer.writerow(['Report Type', 'Metric', 'Value'])
    writer.writerow([])  # Empty row
    
    # Task Status Report
    writer.writerow(['Task Status Report', '', ''])
    status_counts = defaultdict(int)
    for task in tasks:
        status_display = task.get('status', '').replace('_', ' ').title()
        status_counts[status_display] += 1
    
    for status, count in status_counts.items():
        writer.writerow(['Status', status, count])
    
    writer.writerow([])  # Empty row
    
    # Priority Distribution
    writer.writerow(['Priority Distribution', '', ''])
    priority_counts = defaultdict(int)
    for task in tasks:
        priority_display = task.get('priority', '').title()
        priority_counts[priority_display] += 1
    
    for priority, count in priority_counts.items():
        writer.writerow(['Priority', priority, count])
    
    writer.writerow([])  # Empty row
    
    # Task Aging Report
    writer.writerow(['Task Aging Report', '', ''])
    aging_buckets = {
        "0-7 days": 0,
        "8-30 days": 0,
        "31-90 days": 0,
        "90+ days": 0
    }
    
    today = datetime.now()
    for task in tasks:
        created_at_data = task.get('created_at', '')
        if created_at_data:
            try:
                if isinstance(created_at_data, str):
                    created_at = datetime.fromisoformat(created_at_data.replace('Z', '+00:00'))
                elif isinstance(created_at_data, datetime):
                    created_at = created_at_data
                else:
                    continue
                    
                age_days = (today - created_at).days
                
                if age_days <= 7:
                    aging_buckets["0-7 days"] += 1
                elif age_days <= 30:
                    aging_buckets["8-30 days"] += 1
                elif age_days <= 90:
                    aging_buckets["31-90 days"] += 1
                else:
                    aging_buckets["90+ days"] += 1
            except (ValueError, AttributeError, TypeError):
                pass
    
    for age_range, count in aging_buckets.items():
        writer.writerow(['Age Range', age_range, count])
    
    writer.writerow([])  # Empty row
    
    # Overdue Tasks
    writer.writerow(['Overdue Analysis', '', ''])
    overdue_count = 0
    today_date = date.today()
    
    for task in tasks:
        due_date_str = task.get('due_date')
        if due_date_str and task.get('status') != 'completed':
            try:
                if isinstance(due_date_str, str):
                    due_date = datetime.fromisoformat(due_date_str).date()
                elif isinstance(due_date_str, date):
                    due_date = due_date_str
                else:
                    continue
                    
                if due_date < today_date:
                    overdue_count += 1
            except (ValueError, AttributeError, TypeError):
                pass
    
    writer.writerow(['Overdue Tasks', 'Count', overdue_count])
    
    # Completion Rate
    total_tasks = len(tasks)
    completed_tasks = status_counts.get('Completed', 0)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    writer.writerow(['Completion Rate', 'Percentage', f"{completion_rate:.1f}%"])
    
    # Create response
    csv_content = output.getvalue()
    output.close()
    
    # Create filename with current date
    filename = f"task_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
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
