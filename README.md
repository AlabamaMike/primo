# Primo Task Manager

A modern, Python-based task management web application using FastAPI, SQLite, Tailwind CSS, and HTMX with AI-powered assistance.

## Features

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
- ⏰ Task aging analysis and overdue tracking
- 🤖 **AI-Powered Task Assistance** (New!)
  - Smart task name suggestions as you type
  - Automatic task description expansion
  - Complex task breakdown into subtasks
  - Context-aware suggestions based on your task history

## AI Features

The application now includes powerful AI capabilities powered by OpenAI's GPT models:

### Task Name Suggestions
- As you type a task title, get intelligent suggestions based on context
- Suggestions consider your existing tasks to avoid duplicates
- Real-time autocomplete with dropdown selection

### Description Expansion
- Click the AI button next to the description field to automatically expand brief descriptions
- Get detailed, actionable descriptions from simple task titles
- Context-aware expansion that maintains your writing style

### Task Breakdown
- Break complex tasks into manageable subtasks automatically
- AI analyzes your task title and description to create step-by-step action items
- Helps with project planning and task organization

## Setup

### 1. Install dependencies
```bash
pip install fastapi uvicorn jinja2 python-multipart sqlalchemy openai python-dotenv
```

### 2. Configure AI (Optional)
To enable AI features, you'll need an OpenAI API key:

1. Copy the environment template:
```bash
copy .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

3. Get your API key from: https://platform.openai.com/api-keys

**Note**: AI features are optional. The application works fully without an API key, but AI assistance will be disabled.

### 3. Run the application

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
├── app.py                           # FastAPI application with AI endpoints
├── database.py                      # SQLite database client
├── models.py                        # Pydantic models
├── ai_service.py                    # AI service integration (NEW)
├── primo.db                         # SQLite database (auto-created)
├── .env.example                     # Environment template
├── templates/                       # Jinja2 templates
│   ├── base.html                    # Base template
│   ├── login.html                   # Login page
│   ├── register.html                # Registration page
│   ├── dashboard.html               # Main dashboard with AI features
│   ├── reports.html                 # Analytics dashboard
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

### Core Endpoints
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

### AI Endpoints (New)
- `GET /ai/suggestions` - Get AI task name suggestions
- `POST /ai/expand-description` - Expand task description with AI
- `POST /ai/breakdown-task` - Break down complex tasks into subtasks
- `GET /ai/status` - Check AI service availability

## Usage

1. **Register**: Create a new account at `/register`
2. **Login**: Sign in at `/login`
3. **Add Tasks**: Use the form on the dashboard to create new tasks
   - **AI Suggestions**: Start typing a task title to see AI-powered suggestions
   - **Description Expansion**: Click the AI button to expand descriptions automatically
   - **Task Breakdown**: Use the "Break down into subtasks" button for complex tasks
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
- **Frontend**: HTML, Tailwind CSS, HTMX, JavaScript
- **Templates**: Jinja2
- **AI Integration**: OpenAI GPT models
- **Environment**: python-dotenv for configuration

## Security Features

- Password hashing using PBKDF2 with SHA-256
- Session-based authentication
- CSRF protection
- SQL injection prevention with parameterized queries
- Secure API key management through environment variables

## AI Configuration

The AI features use OpenAI's API and support the following configuration options:

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)
- `OPENAI_MODEL`: The model to use (default: gpt-3.5-turbo)

**Cost Considerations**: AI features use OpenAI's API which has usage-based pricing. The application is designed to be efficient with API calls, but monitor your usage if cost is a concern.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
