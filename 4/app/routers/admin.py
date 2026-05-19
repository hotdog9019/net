from fastapi import APIRouter, Depends, HTTPException
from app.schemas import StatsResponse, User
from app.storage import tasks_db
from app.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(require_admin),
) -> StatsResponse:
    """Get statistics about all tasks (admin only)."""
    total_tasks = len(tasks_db)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    
    for task_data in tasks_db.values():
        status = task_data.get("status", "todo")
        if status in by_status:
            by_status[status] += 1
    
    return StatsResponse(total_tasks=total_tasks, by_status=by_status)


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task_admin(
    task_id: int,
    current_user: User = Depends(require_admin),
) -> None:
    """Delete any task (admin only)."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks_db[task_id]
