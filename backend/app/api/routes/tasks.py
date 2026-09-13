from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task import Task
from app.models.user import User
from app.services.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ============================================================
# SCHEMAS
# ============================================================


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    status: str = "todo"


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


# ============================================================
# SERIALIZER
# ============================================================


def serialize_task(task: Task) -> dict:
    return {
        "id": task.id,
        "workspace_id": task.workspace_id,
        "created_by": task.created_by,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


# ============================================================
# LIST TASKS
# ============================================================


@router.get("")
def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    tasks = (
        db.query(Task)
        .filter(
            Task.workspace_id == current_user.workspace_id
        )
        .order_by(Task.updated_at.desc())
        .all()
    )

    return {
        "tasks": [
            serialize_task(task)
            for task in tasks
        ]
    }


# ============================================================
# GET TASK
# ============================================================


@router.get("/{task_id}")
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.workspace_id == current_user.workspace_id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return serialize_task(task)


# ============================================================
# CREATE TASK
# ============================================================


@router.post("")
def create_task(
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Task title is required.",
        )

    task = Task(
        workspace_id=current_user.workspace_id,
        created_by=current_user.id,
        title=title,
        description=request.description,
        status=request.status,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return serialize_task(task)


# ============================================================
# UPDATE TASK
# ============================================================


@router.put("/{task_id}")
def update_task(
    task_id: int,
    request: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.workspace_id == current_user.workspace_id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    if request.title is not None:
        title = request.title.strip()

        if not title:
            raise HTTPException(
                status_code=400,
                detail="Task title cannot be empty.",
            )

        task.title = title

    if request.description is not None:
        task.description = request.description

    if request.status is not None:
        task.status = request.status

    db.commit()
    db.refresh(task)

    return serialize_task(task)


# ============================================================
# DELETE TASK
# ============================================================


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    task = (
        db.query(Task)
        .filter(
            Task.id == task_id,
            Task.workspace_id == current_user.workspace_id,
        )
        .first()
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully.",
        "task_id": task_id,
    }
