from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.database.database import SessionLocal
from app.models.workflow import Workflow


router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class WorkflowCreate(BaseModel):
    workspace_id: int

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    trigger: dict[str, Any]

    conditions: dict[str, Any] | None = None

    actions: list[dict[str, Any]]

    enabled: bool = True


class WorkflowUpdate(BaseModel):
    name: str | None = None

    description: str | None = None

    trigger: dict[str, Any] | None = None

    conditions: dict[str, Any] | None = None

    actions: list[dict[str, Any]] | None = None

    enabled: bool | None = None


# ============================================================
# CREATE
# ============================================================


@router.post("")
def create_workflow(
    request: WorkflowCreate,
):
    db = SessionLocal()

    try:
        workflow = Workflow(
            workspace_id=request.workspace_id,
            name=request.name,
            description=request.description,
            trigger=request.trigger,
            conditions=request.conditions,
            actions=request.actions,
            enabled=request.enabled,
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        return workflow

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        db.close()


# ============================================================
# LIST
# ============================================================


@router.get("")
def list_workflows(
    workspace_id: int | None = None,
):
    db = SessionLocal()

    try:
        query = select(Workflow)

        if workspace_id is not None:
            query = query.where(
                Workflow.workspace_id == workspace_id
            )

        query = query.order_by(
            Workflow.created_at.desc()
        )

        workflows = db.scalars(query).all()

        return {
            "count": len(workflows),
            "workflows": workflows,
        }

    finally:
        db.close()


# ============================================================
# GET
# ============================================================


@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: int,
):
    db = SessionLocal()

    try:
        workflow = db.get(
            Workflow,
            workflow_id,
        )

        if workflow is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found",
            )

        return workflow

    finally:
        db.close()


# ============================================================
# PROCESS EVENT
# ============================================================


@router.post("/events")
def process_workflow_event(
    request: WorkflowEvent,
):
    """
    Send an event into the workflow engine.

    Example:

    {
        "event_name": "deal.created",
        "workspace_id": 1,
        "event_data": {
            "deal_id": 123,
            "amount": 50000,
            "status": "new"
        }
    }
    """

    from app.services.workflow.service import (
        workflow_service,
    )

    try:

        results = workflow_service.process_event(
            event_name=request.event_name,
            event_data=request.event_data,
            workspace_id=request.workspace_id,
        )

        return {
            "event": request.event_name,
            "matched_workflows": len(results),
            "results": results,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# UPDATE
# ============================================================


@router.put("/{workflow_id}")
def update_workflow(
    workflow_id: int,
    request: WorkflowUpdate,
):
    db = SessionLocal()

    try:
        workflow = db.get(
            Workflow,
            workflow_id,
        )

        if workflow is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found",
            )

        updates = request.model_dump(
            exclude_unset=True
        )

        for field, value in updates.items():
            setattr(
                workflow,
                field,
                value,
            )

        db.commit()
        db.refresh(workflow)

        return workflow

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        db.close()


# ============================================================
# ENABLE / DISABLE
# ============================================================


@router.patch("/{workflow_id}/enabled")
def set_workflow_enabled(
    workflow_id: int,
    enabled: bool,
):
    db = SessionLocal()

    try:
        workflow = db.get(
            Workflow,
            workflow_id,
        )

        if workflow is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found",
            )

        workflow.enabled = enabled

        db.commit()
        db.refresh(workflow)

        return {
            "workflow_id": workflow.id,
            "enabled": workflow.enabled,
        }

    finally:
        db.close()


# ============================================================
# DELETE
# ============================================================


@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
):
    db = SessionLocal()

    try:
        workflow = db.get(
            Workflow,
            workflow_id,
        )

        if workflow is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow not found",
            )

        db.delete(workflow)
        db.commit()

        return {
            "message": "Workflow deleted",
            "workflow_id": workflow_id,
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        db.close()


class WorkflowEvent(BaseModel):
    event_name: str = Field(
        min_length=1,
        max_length=255,
    )

    event_data: dict[str, Any] = Field(
        default_factory=dict
    )

    workspace_id: int | None = None
