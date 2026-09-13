from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.knowledge_governance.service import (
    KnowledgeGovernanceService,
)


router = APIRouter(
    prefix="/knowledge-governance",
    tags=["Knowledge Governance"],
)


class VersionCreate(BaseModel):
    workspace_id: int
    resource_type: str
    resource_id: int
    content: str
    changed_by: int | None = None
    change_reason: str | None = None


def serialize_version(version):
    return {
        "id": version.id,
        "workspace_id": version.workspace_id,
        "resource_type": version.resource_type,
        "resource_id": version.resource_id,
        "version_number": version.version_number,
        "content": version.content,
        "changed_by": version.changed_by,
        "change_reason": version.change_reason,
        "created_at": version.created_at,
    }


@router.post("/versions")
def create_version(
    request: VersionCreate,
    db: Session = Depends(get_db),
):
    version = KnowledgeGovernanceService.create_version(
        db=db,
        workspace_id=request.workspace_id,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        content=request.content,
        changed_by=request.changed_by,
        change_reason=request.change_reason,
    )

    return serialize_version(version)


@router.get(
    "/versions/{workspace_id}/{resource_type}/{resource_id}"
)
def get_version_history(
    workspace_id: int,
    resource_type: str,
    resource_id: int,
    db: Session = Depends(get_db),
):
    versions = KnowledgeGovernanceService.get_version_history(
        db=db,
        workspace_id=workspace_id,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    return [
        serialize_version(version)
        for version in versions
    ]


@router.get(
    "/versions/{workspace_id}/{resource_type}/{resource_id}/{version_number}"
)
def get_version(
    workspace_id: int,
    resource_type: str,
    resource_id: int,
    version_number: int,
    db: Session = Depends(get_db),
):
    version = KnowledgeGovernanceService.get_version(
        db=db,
        workspace_id=workspace_id,
        resource_type=resource_type,
        resource_id=resource_id,
        version_number=version_number,
    )

    if not version:
        raise HTTPException(
            status_code=404,
            detail="Knowledge version not found",
        )

    return serialize_version(version)
