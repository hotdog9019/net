from fastapi import FastAPI
from app.routers import tasks, users, admin

app = FastAPI(title="Task Management API")

# Include routers
app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
