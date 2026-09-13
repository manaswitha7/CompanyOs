from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.models.crm_relationship import CRMRelationship


router = APIRouter(
    prefix="/crm",
    tags=["CRM"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class RelationshipCreate(BaseModel):
    workspace_id: int

    source_type: str
    source_id: int

    target_type: str
    target_id: int

    relationship_type: str

    description: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


# ============================================================
# RELATIONSHIP SERIALIZER
# ============================================================


def relationship_to_dict(
    relationship: CRMRelationship,
) -> dict:

    return {
        "id": relationship.id,
        "workspace_id": relationship.workspace_id,
        "source": {
            "type": relationship.source_type,
            "id": relationship.source_id,
        },
        "target": {
            "type": relationship.target_type,
            "id": relationship.target_id,
        },
        "relationship_type": (
            relationship.relationship_type
        ),
        "description": relationship.description,
        "metadata": relationship.metadata_json,
        "created_at": (
            relationship.created_at.isoformat()
        ),
        "updated_at": (
            relationship.updated_at.isoformat()
        ),
    }


# ============================================================
# CREATE RELATIONSHIP
# ============================================================


@router.post("/relationships")
def create_relationship(
    request: RelationshipCreate,
):

    db = SessionLocal()

    try:
        relationship = CRMRelationship(
            workspace_id=request.workspace_id,
            source_type=request.source_type.lower(),
            source_id=request.source_id,
            target_type=request.target_type.lower(),
            target_id=request.target_id,
            relationship_type=(
                request.relationship_type.lower()
            ),
            description=request.description,
            metadata_json=request.metadata,
        )

        db.add(relationship)
        db.commit()
        db.refresh(relationship)

        return relationship_to_dict(
            relationship
        )

    finally:
        db.close()


# ============================================================
# GET RELATIONSHIPS OF AN OBJECT
# ============================================================


@router.get("/relationships")
def get_relationships(
    workspace_id: int,
    object_type: str,
    object_id: int,
):

    db = SessionLocal()

    try:

        object_type = object_type.lower()

        relationships = (
            db.query(CRMRelationship)
            .filter(
                CRMRelationship.workspace_id
                == workspace_id
            )
            .filter(
                (
                    (
                        CRMRelationship.source_type
                        == object_type
                    )
                    & (
                        CRMRelationship.source_id
                        == object_id
                    )
                )
                |
                (
                    (
                        CRMRelationship.target_type
                        == object_type
                    )
                    & (
                        CRMRelationship.target_id
                        == object_id
                    )
                )
            )
            .all()
        )

        return {
            "object": {
                "type": object_type,
                "id": object_id,
            },
            "count": len(relationships),
            "relationships": [
                relationship_to_dict(item)
                for item in relationships
            ],
        }

    finally:
        db.close()


# ============================================================
# DELETE RELATIONSHIP
# ============================================================


@router.delete("/relationships/{relationship_id}")
def delete_relationship(
    relationship_id: int,
):

    db = SessionLocal()

    try:

        relationship = (
            db.query(CRMRelationship)
            .filter(
                CRMRelationship.id
                == relationship_id
            )
            .first()
        )

        if not relationship:
            raise HTTPException(
                status_code=404,
                detail="Relationship not found",
            )

        db.delete(relationship)
        db.commit()

        return {
            "success": True,
            "relationship_id": relationship_id,
        }

    finally:
        db.close()


# ============================================================
# CRM OBJECT TYPES
# ============================================================


@router.get("/object-types")
def crm_object_types():

    return {
        "object_types": [
            "company",
            "person",
            "project",
            "deal",
            "ticket",
        ]
    }
