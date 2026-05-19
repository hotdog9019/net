from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.schemas import Task, TaskCreate, TaskStatusUpdate, User
from app.storage import tasks_db, get_next_task_id
from app.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=201, response_model=Task)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
) -> Task:
    """Create a new task for the current user."""
    task_id = get_next_task_id()
    new_task = Task(
        id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        owner_id=current_user.id,
    )
    tasks_db[task_id] = new_task.model_dump()
    return new_task


@router.get("", response_model=list[Task])
async def get_tasks(
    status: Optional[str] = Query(None),
    min_priority: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    """Get all tasks for the current user with optional filtering."""
    tasks = [
        Task(**task_data)
        for task_data in tasks_db.values()
        if task_data["owner_id"] == current_user.id
    ]
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    if min_priority is not None:
        tasks = [t for t in tasks if t.priority >= min_priority]
    
    return tasks


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
) -> Task:
    """Get a single task by ID."""
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Task(**task_data)


@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
) -> Task:
    """Update the status of a task."""
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data["status"] = update.status
    return Task(**task_data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a task."""
    task_data = tasks_db.get(task_id)
    if not task_data or task_data["owner_id"] != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
