from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.context.cross_team import (
    get_cross_team_context,
)


router = APIRouter(
    prefix="/context",
    tags=["Cross-Team Context"],
)


@router.get("/cross-team")
def cross_team_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return organizational and business context
    available within the user's workspace.
    """

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    return get_cross_team_context(
        db=db,
        user_id=current_user.id,
        workspace_id=current_user.workspace_id,
    )
