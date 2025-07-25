from app import app
import uvicorn

def main():
    print("Starting Primo Task Manager...")
    print("🚀 Server will be available at: http://localhost:8000")
    print("📋 Features:")
    print("  - User registration and login with SQLite")
    print("  - Personal task management")
    print("  - Mobile-friendly interface with Tailwind CSS")  
    print("  - Real-time updates with HTMX")
    print("💾 Using SQLite database for data storage")
    print("\n" + "="*50)
    
    # Start the FastAPI server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
