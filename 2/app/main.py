import os
from fastapi import FastAPI, HTTPException, Header, Query
from typing import Optional
from app.schemas import Task, TaskCreate, TaskStatusUpdate, HealthResponse
from app.storage import tasks_db, get_next_task_id, reset_storage

app = FastAPI()

# Get environment
APP_ENV = os.getenv("APP_ENV", "local")


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", env=APP_ENV)


@app.post("/tasks", status_code=201, response_model=Task)
def create_task(
    task: TaskCreate,
    x_user_id: str = Header(...),
) -> Task:
    """Create a new task for the current user."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    
    task_id = get_next_task_id()
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        owner_id=user_id,
    )
    tasks_db[task_id] = new_task.model_dump()
    return new_task


@app.get("/tasks", response_model=list[Task])
def get_tasks(
    status: Optional[str] = Query(None),
    min_priority: Optional[int] = Query(None),
    x_user_id: str = Header(...),
) -> list[Task]:
    """Get all tasks for the current user with optional filtering."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    
    tasks = [
        Task(**task_data)
        for task_data in tasks_db.values()
        if task_data["owner_id"] == user_id
    ]
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    if min_priority is not None:
        tasks = [t for t in tasks if t.priority >= min_priority]
    
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    x_user_id: str = Header(...),
) -> Task:
    """Get a single task by ID."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Task(**task_data)


@app.patch("/tasks/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    x_user_id: str = Header(...),
) -> Task:
    """Update the status of a task."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data["status"] = update.status
    return Task(**task_data)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    x_user_id: str = Header(...),
) -> None:
    """Delete a task."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-User-Id must be an integer")
    
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
