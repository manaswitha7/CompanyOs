from enum import Enum


class Role(str, Enum):
    """
    Roles supported by Company OS.

    Role hierarchy:

        OWNER
          ↓
        ADMIN
          ↓
        MANAGER
          ↓
        MEMBER
          ↓
        VIEWER
    """

    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class Permission(str, Enum):

    # ========================================================
    # Documents
    # ========================================================

    DOCUMENTS_READ = "documents.read"
    DOCUMENTS_CREATE = "documents.create"
    DOCUMENTS_UPDATE = "documents.update"
    DOCUMENTS_DELETE = "documents.delete"

    # ========================================================
    # Workspace
    # ========================================================

    WORKSPACE_READ = "workspace.read"
    WORKSPACE_MANAGE = "workspace.manage"

    # ========================================================
    # Users
    # ========================================================

    USERS_READ = "users.read"
    USERS_MANAGE = "users.manage"

    # ========================================================
    # Chat / RAG
    # ========================================================

    CHAT_USE = "chat.use"

    # ========================================================
    # Tasks
    # ========================================================

    TASKS_READ = "tasks.read"
    TASKS_CREATE = "tasks.create"
    TASKS_UPDATE = "tasks.update"
    TASKS_DELETE = "tasks.delete"

    # ========================================================
    # Evaluation
    # ========================================================

    EVALUATION_READ = "evaluation.read"
    EVALUATION_RUN = "evaluation.run"

    # ========================================================
    # System
    # ========================================================

    SYSTEM_VIEW = "system.view"
    SYSTEM_MANAGE = "system.manage"

    # ========================================================
    # Audit
    # ========================================================

    AUDIT_READ = "audit.read"


# ============================================================
# ROLE → PERMISSION MAPPING
# ============================================================

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {

    # --------------------------------------------------------
    # VIEWER
    # --------------------------------------------------------

    Role.VIEWER: {
        Permission.DOCUMENTS_READ,

        Permission.WORKSPACE_READ,

        Permission.CHAT_USE,

        Permission.TASKS_READ,
    },

    # --------------------------------------------------------
    # MEMBER
    # --------------------------------------------------------

    Role.MEMBER: {
        # Documents
        Permission.DOCUMENTS_READ,
        Permission.DOCUMENTS_CREATE,
        Permission.DOCUMENTS_UPDATE,

        # Workspace
        Permission.WORKSPACE_READ,

        # Chat
        Permission.CHAT_USE,

        # Tasks
        Permission.TASKS_READ,
        Permission.TASKS_CREATE,
        Permission.TASKS_UPDATE,
    },

    # --------------------------------------------------------
    # MANAGER
    # --------------------------------------------------------

    Role.MANAGER: {
        # Documents
        Permission.DOCUMENTS_READ,
        Permission.DOCUMENTS_CREATE,
        Permission.DOCUMENTS_UPDATE,
        Permission.DOCUMENTS_DELETE,

        # Workspace
        Permission.WORKSPACE_READ,

        # Users
        Permission.USERS_READ,

        # Chat
        Permission.CHAT_USE,

        # Tasks
        Permission.TASKS_READ,
        Permission.TASKS_CREATE,
        Permission.TASKS_UPDATE,
        Permission.TASKS_DELETE,

        # Evaluation
        Permission.EVALUATION_READ,
        Permission.EVALUATION_RUN,

        # System
        Permission.SYSTEM_VIEW,
    },

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    Role.ADMIN: {
        # Documents
        Permission.DOCUMENTS_READ,
        Permission.DOCUMENTS_CREATE,
        Permission.DOCUMENTS_UPDATE,
        Permission.DOCUMENTS_DELETE,

        # Workspace
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_MANAGE,

        # Users
        Permission.USERS_READ,
        Permission.USERS_MANAGE,

        # Chat
        Permission.CHAT_USE,

        # Tasks
        Permission.TASKS_READ,
        Permission.TASKS_CREATE,
        Permission.TASKS_UPDATE,
        Permission.TASKS_DELETE,

        # Evaluation
        Permission.EVALUATION_READ,
        Permission.EVALUATION_RUN,

        # System
        Permission.SYSTEM_VIEW,
        Permission.SYSTEM_MANAGE,

        # Audit
        Permission.AUDIT_READ,
    },

    # --------------------------------------------------------
    # OWNER
    # --------------------------------------------------------

    Role.OWNER: {
        # Documents
        Permission.DOCUMENTS_READ,
        Permission.DOCUMENTS_CREATE,
        Permission.DOCUMENTS_UPDATE,
        Permission.DOCUMENTS_DELETE,

        # Workspace
        Permission.WORKSPACE_READ,
        Permission.WORKSPACE_MANAGE,

        # Users
        Permission.USERS_READ,
        Permission.USERS_MANAGE,

        # Chat
        Permission.CHAT_USE,

        # Tasks
        Permission.TASKS_READ,
        Permission.TASKS_CREATE,
        Permission.TASKS_UPDATE,
        Permission.TASKS_DELETE,

        # Evaluation
        Permission.EVALUATION_READ,
        Permission.EVALUATION_RUN,

        # System
        Permission.SYSTEM_VIEW,
        Permission.SYSTEM_MANAGE,

        # Audit
        Permission.AUDIT_READ,
    },
}


# ============================================================
# ROLE HIERARCHY
# ============================================================

ROLE_LEVEL: dict[Role, int] = {
    Role.VIEWER: 10,
    Role.MEMBER: 20,
    Role.MANAGER: 30,
    Role.ADMIN: 40,
    Role.OWNER: 50,
}


# ============================================================
# ROLE NORMALIZATION
# ============================================================

def normalize_role(role: str | Role) -> Role:
    """
    Convert a string/database role into the Role enum.
    """

    if isinstance(role, Role):
        return role

    try:
        return Role(str(role).strip().lower())
    except ValueError:
        raise ValueError(
            f"Unknown role: {role}"
        )


# ============================================================
# ROLE COMPARISON
# ============================================================

def role_level(role: str | Role) -> int:
    """
    Return the numeric hierarchy level of a role.
    """

    normalized_role = normalize_role(role)

    return ROLE_LEVEL[normalized_role]


def has_higher_or_equal_role(
    role: str | Role,
    required_role: str | Role,
) -> bool:
    """
    Check whether a role is equal to or higher than
    another role in the Company OS hierarchy.
    """

    return (
        role_level(role)
        >= role_level(required_role)
    )


# ============================================================
# PERMISSION LOOKUP
# ============================================================

def get_role_permissions(
    role: str | Role,
) -> set[Permission]:
    """
    Return all permissions assigned to a role.
    """

    normalized_role = normalize_role(role)

    return ROLE_PERMISSIONS.get(
        normalized_role,
        set(),
    ).copy()


# ============================================================
# PERMISSION CHECK
# ============================================================

def role_has_permission(
    role: str | Role,
    permission: str | Permission,
) -> bool:
    """
    Check whether a role has a specific permission.
    """

    normalized_role = normalize_role(role)

    if not isinstance(permission, Permission):
        try:
            permission = Permission(permission)
        except ValueError:
            return False

    return permission in ROLE_PERMISSIONS.get(
        normalized_role,
        set(),
    )


# ============================================================
# RBAC VALIDATION
# ============================================================

def validate_role_configuration() -> None:
    """
    Validate the RBAC configuration.

    This catches accidental mistakes such as:

    - missing roles
    - invalid permissions
    - broken hierarchy
    - higher roles missing permissions from lower roles
    """

    # Every role must have a hierarchy level.
    for role in Role:

        if role not in ROLE_LEVEL:
            raise RuntimeError(
                f"Role '{role.value}' has no hierarchy level."
            )

        if role not in ROLE_PERMISSIONS:
            raise RuntimeError(
                f"Role '{role.value}' has no permission mapping."
            )

    # Every configured permission must be valid.
    for role, permissions in ROLE_PERMISSIONS.items():

        for permission in permissions:

            if not isinstance(
                permission,
                Permission,
            ):
                raise RuntimeError(
                    f"Invalid permission '{permission}' "
                    f"configured for role '{role.value}'."
                )

    # Higher roles must inherit lower-role permissions.
    ordered_roles = sorted(
        Role,
        key=lambda role: ROLE_LEVEL[role],
    )

    for index, role in enumerate(ordered_roles):

        current_permissions = ROLE_PERMISSIONS[role]

        inherited_permissions = set()

        for lower_role in ordered_roles[:index]:
            inherited_permissions.update(
                ROLE_PERMISSIONS[lower_role]
            )

        missing_permissions = (
            inherited_permissions
            - current_permissions
        )

        if missing_permissions:

            missing = ", ".join(
                permission.value
                for permission in sorted(
                    missing_permissions,
                    key=lambda permission: permission.value,
                )
            )

            raise RuntimeError(
                f"Role '{role.value}' is missing inherited "
                f"permissions: {missing}"
            )


# Validate configuration when the module loads.
validate_role_configuration()
