# primo

A Python-based task management web application using FastAPI, Supabase, Tailwind CSS, and HTMX.

## Features

- 🔐 User authentication with Supabase Auth (email/password)
- 📝 Personal task management with CRUD operations
- 📱 Mobile-friendly responsive design with Tailwind CSS
- ⚡ Real-time updates with HTMX
- 🏷️ Task priorities (Low, Medium, High, Urgent)
- 📊 Task statuses (To Do, In Progress, Completed)
- 📅 Due date tracking
- 🔒 Secure row-level security with Supabase

## Setup

### 1. Install dependencies
Dependencies are already installed in the virtual environment:
```bash
pip install fastapi uvicorn supabase python-dotenv jinja2 python-multipart certifi
```

### 2. Configure Supabase

#### Database Setup
1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Run the SQL script from `database_setup.sql` to create the tasks table and policies

#### Environment Configuration
Your `.env` file is already configured with:
```
SUPABASE_URL=https://vdcqtridfcqizmenquaa.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Run the application

```bash
python main.py
```

Or use the VS Code task "Run Python Script"

The application will be available at: http://localhost:8000

## Project Structure

```
primo/
├── main.py                          # Application entry point
├── app.py                           # FastAPI application
├── models.py                        # Pydantic models
├── supabase_client.py              # Supabase client wrapper
├── database_setup.sql              # Database schema and policies
├── templates/                      # Jinja2 templates
│   ├── base.html                   # Base template
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── dashboard.html              # Main dashboard
│   └── partials/                   # HTMX partial templates
│       ├── task_list.html          # Task list component
│       └── task_edit_form.html     # Task edit form
├── static/                         # Static files (CSS, JS)
├── .env                           # Environment variables
├── .env.example                   # Environment template
└── .vscode/tasks.json             # VS Code tasks
```

## Database Schema

The `tasks` table includes:
- `id` - Primary key
- `title` - Task title (required)
- `description` - Optional task description
- `due_date` - Optional due date
- `priority` - Low, Medium, High, Urgent
- `status` - To Do, In Progress, Completed
- `user_id` - Reference to authenticated user
- `created_at` - Timestamp
- `updated_at` - Auto-updated timestamp

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
- `POST /logout` - Logout

## Usage

1. **Register**: Create a new account at `/register`
2. **Login**: Sign in at `/login`
3. **Add Tasks**: Use the form on the dashboard to create new tasks
4. **Manage Tasks**: Edit or delete tasks using the buttons in the task list
5. **Track Progress**: Update task status and priority as needed

## Technologies

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Frontend**: HTML, Tailwind CSS, HTMX
- **Templates**: Jinja2
