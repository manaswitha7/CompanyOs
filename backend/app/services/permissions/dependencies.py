from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.services.auth.dependencies import get_current_user
from app.services.permissions.roles import Permission
from app.services.permissions.service import has_permission


def require_permission(
    permission: Permission,
):
    """
    FastAPI dependency that checks whether the
    authenticated user's role has the requested permission.
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if not has_permission(
            current_user.role,
            permission,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role}' does not have "
                    f"permission '{permission.value}'."
                ),
            )

        return current_user

    return checker
