from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.services.permissions.roles import Permission, Role
from app.services.permissions.service import has_permission


# ============================================================
# DOCUMENT ACCESS
# ============================================================


def is_document_owner(
    db: Session,
    user_id: int,
    document_id: int,
) -> bool:
    """
    Check whether the given user owns the document.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
        )
        .first()
    )

    if not document:
        return False

    return document.owner_id == user_id


def has_document_permission(
    db: Session,
    user_id: int,
    document_id: int,
    permission: str = "read",
) -> bool:
    """
    Check whether a specific user has an explicit
    permission on a specific document.
    """

    document_permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission == permission,
        )
        .first()
    )

    return document_permission is not None


def can_read_document(
    db: Session,
    user_id: int,
    role: str | Role,
    document_id: int,
) -> bool:
    """
    Determine whether a user can read a document.

    Access is granted when:

    1. The user's role allows document reading AND
    2. The user owns the document OR
       has an explicit document permission.

    This also preserves workspace-level isolation
    through the document queries performed by callers.
    """

    if not has_permission(
        role,
        Permission.DOCUMENTS_READ,
    ):
        return False

    if is_document_owner(
        db=db,
        user_id=user_id,
        document_id=document_id,
    ):
        return True

    return has_document_permission(
        db=db,
        user_id=user_id,
        document_id=document_id,
        permission="read",
    )


def can_update_document(
    db: Session,
    user_id: int,
    role: str | Role,
    document_id: int,
) -> bool:
    """
    Determine whether a user can update a document.

    Owners require the role-level update permission.
    Explicit document permissions can grant update access.
    """

    if not has_permission(
        role,
        Permission.DOCUMENTS_UPDATE,
    ):
        return False

    if is_document_owner(
        db=db,
        user_id=user_id,
        document_id=document_id,
    ):
        return True

    return has_document_permission(
        db=db,
        user_id=user_id,
        document_id=document_id,
        permission="update",
    )


def can_delete_document(
    db: Session,
    user_id: int,
    role: str | Role,
    document_id: int,
) -> bool:
    """
    Determine whether a user can delete a document.

    The user must have the global delete permission
    and either own the document or have explicit delete access.
    """

    if not has_permission(
        role,
        Permission.DOCUMENTS_DELETE,
    ):
        return False

    if is_document_owner(
        db=db,
        user_id=user_id,
        document_id=document_id,
    ):
        return True

    return has_document_permission(
        db=db,
        user_id=user_id,
        document_id=document_id,
        permission="delete",
    )


# ============================================================
# ACCESSIBLE DOCUMENTS
# ============================================================


def get_accessible_document_ids(
    db: Session,
    user_id: int,
    role: str | Role,
    workspace_id: int,
) -> list[int]:
    """
    Return document IDs that the user is allowed to read.

    Documents are restricted to the user's workspace.

    Access is granted when the user:

    - owns the document
    - OR has an explicit read permission
    """

    if not has_permission(
        role,
        Permission.DOCUMENTS_READ,
    ):
        return []

    owned_document_ids = (
        db.query(Document.id)
        .filter(
            Document.workspace_id == workspace_id,
            Document.owner_id == user_id,
        )
        .all()
    )

    permitted_document_ids = (
        db.query(Document.id)
        .join(
            DocumentPermission,
            DocumentPermission.document_id
            == Document.id,
        )
        .filter(
            Document.workspace_id == workspace_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission == "read",
        )
        .all()
    )

    document_ids = {
        document_id
        for (document_id,) in owned_document_ids
    }

    document_ids.update(
        document_id
        for (document_id,) in permitted_document_ids
    )

    return list(document_ids)
