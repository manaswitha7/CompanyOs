from app.services.permissions.roles import (
    Permission,
    Role,
    ROLE_PERMISSIONS,
)


def normalize_role(role: str | Role) -> Role:
    """
    Convert a database/user role into the Role enum.
    """

    if isinstance(role, Role):
        return role

    try:
        return Role(role.lower())
    except (ValueError, AttributeError):
        raise ValueError(
            f"Unknown role: {role}"
        )


def has_permission(
    role: str | Role,
    permission: str | Permission,
) -> bool:
    """
    Check whether a role has a specific permission.
    """

    normalized_role = normalize_role(role)

    if isinstance(permission, Permission):
        normalized_permission = permission
    else:
        try:
            normalized_permission = Permission(permission)
        except ValueError:
            return False

    permissions = ROLE_PERMISSIONS.get(
        normalized_role,
        set(),
    )

    return normalized_permission in permissions


def get_permissions(
    role: str | Role,
) -> set[Permission]:
    """
    Return all permissions available to a role.
    """

    normalized_role = normalize_role(role)

    return ROLE_PERMISSIONS.get(
        normalized_role,
        set(),
    )


def require_permission(
    role: str | Role,
    permission: str | Permission,
) -> None:
    """
    Raise PermissionError if the role does not
    have the requested permission.
    """

    if not has_permission(role, permission):
        raise PermissionError(
            f"Role '{role}' does not have permission "
            f"'{permission}'."
        )
