from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.services.auth.permissions import require_roles
from app.services.audit.service import create_audit_log


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


ALLOWED_ROLES = {
    "owner",
    "admin",
    "member",
}


class UpdateRoleRequest(BaseModel):
    role: str


@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    current_user: User = Depends(
        require_roles(
            "owner",
            "admin",
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Change the role of a user in the current workspace.

    Rules:
    - Owners can manage users in their workspace.
    - Owners can assign the owner role.
    - Admins cannot assign the owner role.
    - Admins cannot modify an owner.
    - Users cannot change their own role.
    """

    # --------------------------------------------------
    # 1. Validate requested role
    # --------------------------------------------------

    if request.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid role. Allowed roles: "
                "owner, admin, member."
            ),
        )

    # --------------------------------------------------
    # 2. Validate workspace
    # --------------------------------------------------

    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    # --------------------------------------------------
    # 3. Prevent self-role modification
    # --------------------------------------------------

    if user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot change your own role.",
        )

    # --------------------------------------------------
    # 4. Find target user
    # --------------------------------------------------

    target_user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.workspace_id == current_user.workspace_id,
        )
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="User not found in your workspace.",
        )

    # --------------------------------------------------
    # 5. Admin cannot create another owner
    # --------------------------------------------------

    if (
        request.role == "owner"
        and current_user.role != "owner"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only an owner can assign the owner role.",
        )

    # --------------------------------------------------
    # 6. Admin cannot modify an existing owner
    # --------------------------------------------------

    if (
        target_user.role == "owner"
        and current_user.role != "owner"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only an owner can modify an owner.",
        )

    # --------------------------------------------------
    # 7. Store old role
    # --------------------------------------------------

    old_role = target_user.role

    # --------------------------------------------------
    # 8. Update role
    # --------------------------------------------------

    target_user.role = request.role

    # --------------------------------------------------
    # 9. Create audit log
    # --------------------------------------------------

    create_audit_log(
        db,
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        action="USER_ROLE_CHANGED",
        resource_type="user",
        resource_id=target_user.id,
        details={
            "target_user_id": target_user.id,
            "old_role": old_role,
            "new_role": request.role,
        },
    )

    # --------------------------------------------------
    # 10. Commit
    # --------------------------------------------------

    db.commit()
    db.refresh(target_user)

    # --------------------------------------------------
    # 11. Return
    # --------------------------------------------------

    return {
        "message": "User role updated successfully",
        "user": {
            "id": target_user.id,
            "email": target_user.email,
            "name": target_user.name,
            "role": target_user.role,
            "workspace_id": target_user.workspace_id,
        },
    }
