from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task, TaskResponse
from .services import (
    create_task as create_task_service,
    get_task as get_task_service,
    get_tasks as get_tasks_service,
    update_task as update_task_service,
    delete_task as delete_task_service,
)

router = APIRouter()


# Get all tasks
@router.get("/tasks", response_model=list[TaskResponse])
def read_tasks(db: Session = Depends(get_db)):
    return get_tasks_service(db)


# Get a single task by ID
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = get_task_service(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


# Create a new task
@router.post("/tasks", response_model=TaskResponse)
def create_task(task: Task, db: Session = Depends(get_db)):
    return create_task_service(db, task)


# Update an existing task
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: Task,
    db: Session = Depends(get_db),
):
    # Validate that the URL ID matches the request body ID
    if task.id != task_id:
        raise HTTPException(
            status_code=400,
            detail="Task ID in URL must match task ID in request body",
        )

    updated_task = update_task_service(db, task_id, task)

    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return updated_task


# Delete an existing task
@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_task_service(db, task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {"message": "Task deleted successfully"}