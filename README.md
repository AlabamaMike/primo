# pr## Features

- 🔐 User authentication with secure password hashing
- 📝 Personal task management with CRUD operations
- 📱 Mobile-friendly responsive design with Tailwind CSS
- ⚡ Real-time updates with HTMX
- 🏷️ Task priorities (Low, Medium, High, Urgent)
- 📊 Task statuses (To Do, In Progress, Completed)
- 📅 Due date tracking
- 💾 Simple SQLite database storage
- 🔒 Session-based authentication
- 📄 CSV export functionality for task data
- 📈 Comprehensive reporting dashboard with task analytics
- ⏰ Task aging analysis and overdue trackingthon-based task management web application using FastAPI, SQLite, Tailwind CSS, and HTMX.

## Features

- 🔐 User authentication with secure password hashing
- 📝 Personal task management with CRUD operations
- 📱 Mobile-friendly responsive design with Tailwind CSS
- ⚡ Real-time updates with HTMX
- 🏷️ Task priorities (Low, Medium, High, Urgent)
- 📊 Task statuses (To Do, In Progress, Completed)
- 📅 Due date tracking
- � Simple SQLite database storage
- 🔒 Session-based authentication

## Setup

### 1. Install dependencies
Dependencies are already installed in the virtual environment:
```bash
pip install fastapi uvicorn jinja2 python-multipart sqlalchemy
```

### 2. Run the application

```bash
python main.py
```

Or use the VS Code task "Run Python Script"

The application will be available at: http://localhost:8000

The SQLite database (`primo.db`) will be automatically created on first run.

## Project Structure

```
primo/
├── main.py                          # Application entry point
├── app.py                           # FastAPI application
├── database.py                      # SQLite database client
├── models.py                        # Pydantic models
├── primo.db                         # SQLite database (auto-created)
├── templates/                       # Jinja2 templates
│   ├── base.html                    # Base template
│   ├── login.html                   # Login page
│   ├── register.html                # Registration page
│   ├── dashboard.html               # Main dashboard
│   └── partials/                    # HTMX partial templates
│       ├── task_list.html           # Task list component
│       └── task_edit_form.html      # Task edit form
├── static/                          # Static files (CSS, JS)
└── .vscode/tasks.json               # VS Code tasks
```

## Database Schema

### Users Table
- `id` - Unique user identifier
- `email` - User email (unique)
- `password_hash` - Securely hashed password
- `created_at` - Registration timestamp

### Tasks Table
- `id` - Primary key (auto-increment)
- `title` - Task title (required)
- `description` - Optional task description
- `due_date` - Optional due date
- `priority` - Low, Medium, High, Urgent
- `status` - To Do, In Progress, Completed
- `user_id` - Reference to user
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## API Endpoints

- `GET /` - Home (redirects to login or dashboard)
- `GET /login` - Login page
- `POST /login` - Handle login
- `GET /register` - Registration page
- `POST /register` - Handle registration
- `GET /dashboard` - Main dashboard
- `GET /tasks` - Get tasks (HTMX)
- `POST /tasks` - Create task
- `GET /tasks/{id}/edit` - Edit form (HTMX)
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `GET /export/csv` - Export tasks as CSV file
- `GET /reports` - Task reports dashboard
- `GET /reports/export` - Export reports as CSV file
- `POST /logout` - Logout

## Usage

1. **Register**: Create a new account at `/register`
2. **Login**: Sign in at `/login`
3. **Add Tasks**: Use the form on the dashboard to create new tasks
4. **Manage Tasks**: Edit or delete tasks using the buttons in the task list
5. **Track Progress**: Update task status and priority as needed
6. **Export Data**: Click the "Export CSV" button to download your tasks as a CSV file
7. **View Reports**: Access the Reports page for comprehensive task analytics including:
   - Task status distribution
   - Priority analysis
   - Task aging reports
   - Overdue task tracking
   - Completion rate metrics

## Technologies

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Authentication**: Session-based with secure password hashing
- **Frontend**: HTML, Tailwind CSS, HTMX
- **Templates**: Jinja2

## Security Features

- Password hashing using PBKDF2 with SHA-256
- Session-based authentication
- CSRF protection
- SQL injection prevention with parameterized queries
