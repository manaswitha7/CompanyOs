from app.services.permissions.roles import (
    Permission,
    Role,
)
from app.services.permissions.service import (
    has_permission,
)


def test_owner_can_delete_documents():

    assert has_permission(
        Role.OWNER,
        Permission.DOCUMENTS_DELETE,
    )


def test_admin_can_delete_documents():

    assert has_permission(
        Role.ADMIN,
        Permission.DOCUMENTS_DELETE,
    )


def test_member_cannot_delete_documents():

    assert not has_permission(
        Role.MEMBER,
        Permission.DOCUMENTS_DELETE,
    )


def test_viewer_can_read_documents():

    assert has_permission(
        Role.VIEWER,
        Permission.DOCUMENTS_READ,
    )


def test_viewer_cannot_upload_documents():

    assert not has_permission(
        Role.VIEWER,
        Permission.DOCUMENTS_CREATE,
    )
