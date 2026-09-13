from sqlalchemy.orm import Session

from app.models.document_permission import DocumentPermission


READ_PERMISSION = "read"
WRITE_PERMISSION = "write"
DELETE_PERMISSION = "delete"


def grant_document_permission(
    db: Session,
    document_id: int,
    user_id: int,
    permission: str = READ_PERMISSION,
) -> DocumentPermission:
    """
    Grant a user permission on a document.

    If the permission already exists, update it.
    """

    existing = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
        )
        .first()
    )

    if existing:
        existing.permission = permission
        db.flush()
        return existing

    document_permission = DocumentPermission(
        document_id=document_id,
        user_id=user_id,
        permission=permission,
    )

    db.add(document_permission)
    db.flush()

    return document_permission


def revoke_document_permission(
    db: Session,
    document_id: int,
    user_id: int,
) -> bool:
    """
    Remove a user's permission from a document.
    """

    existing = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
        )
        .first()
    )

    if not existing:
        return False

    db.delete(existing)
    db.flush()

    return True


def user_can_read_document(
    db: Session,
    document_id: int,
    user_id: int,
) -> bool:
    """
    Check whether a user has explicit read permission.
    """

    permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission == READ_PERMISSION,
        )
        .first()
    )

    return permission is not None
