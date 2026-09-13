from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/team-views",
    tags=["Team Views"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class TeamViewCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    team_id: int
    config: dict[str, Any] = Field(default_factory=dict)


class TeamViewUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None
    config: dict[str, Any] | None = None


# ============================================================
# LIST TEAM VIEWS
# ============================================================


@router.get("")
def list_team_views():
    """
    Return all team views.

    Database-backed implementation will be connected
    in the next step.
    """

    return {
        "team_views": []
    }


# ============================================================
# GET TEAM VIEW
# ============================================================


@router.get("/{view_id}")
def get_team_view(view_id: int):
    """
    Return a single team view.
    """

    raise HTTPException(
        status_code=404,
        detail=f"Team view not found: {view_id}",
    )


# ============================================================
# CREATE TEAM VIEW
# ============================================================


@router.post("")
def create_team_view(
    request: TeamViewCreate,
):
    """
    Create a team view.
    """

    return {
        "message": "Team view creation endpoint ready",
        "team_view": request.model_dump(),
    }


# ============================================================
# UPDATE TEAM VIEW
# ============================================================


@router.patch("/{view_id}")
def update_team_view(
    view_id: int,
    request: TeamViewUpdate,
):
    """
    Update a team view.
    """

    return {
        "message": "Team view update endpoint ready",
        "view_id": view_id,
        "updates": request.model_dump(
            exclude_unset=True
        ),
    }


# ============================================================
# DELETE TEAM VIEW
# ============================================================


@router.delete("/{view_id}")
def delete_team_view(view_id: int):
    """
    Delete a team view.
    """

    return {
        "message": "Team view deletion endpoint ready",
        "view_id": view_id,
    }
