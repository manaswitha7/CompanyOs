from unittest.mock import MagicMock

from app.services.permissions.document_access import (
    can_read_document,
    can_update_document,
    can_delete_document,
)


def make_db():
    return MagicMock()


def setup_document_query(db, owner_id):
    document = MagicMock()
    document.owner_id = owner_id

    (
        db.query.return_value
        .filter.return_value
        .first.return_value
    ) = document

    return document


def setup_no_explicit_permission(db):
    """
    Make the explicit document-permission lookup
    return None.

    The first query is used by is_document_owner().
    The second query is used by has_document_permission().
    """

    owner_query = MagicMock()
    permission_query = MagicMock()

    db.query.side_effect = [
        owner_query,
        permission_query,
    ]

    return owner_query, permission_query


# ============================================================
# READ
# ============================================================


def test_owner_can_read_document():
    db = make_db()

    setup_document_query(
        db=db,
        owner_id=1,
    )

    result = can_read_document(
        db=db,
        user_id=1,
        role="member",
        document_id=10,
    )

    assert result is True


def test_non_owner_without_permission_cannot_read():
    db = make_db()

    owner_query = MagicMock()
    permission_query = MagicMock()

    document = MagicMock()
    document.owner_id = 2

    owner_query.filter.return_value.first.return_value = document

    # No explicit permission exists.
    permission_query.filter.return_value.first.return_value = None

    db.query.side_effect = [
        owner_query,
        permission_query,
    ]

    result = can_read_document(
        db=db,
        user_id=1,
        role="member",
        document_id=10,
    )

    assert result is False


# ============================================================
# DELETE
# ============================================================


def test_member_cannot_delete_document():
    db = make_db()

    setup_document_query(
        db=db,
        owner_id=1,
    )

    result = can_delete_document(
        db=db,
        user_id=1,
        role="member",
        document_id=10,
    )

    assert result is False


# ============================================================
# UPDATE
# ============================================================


def test_viewer_cannot_update_document():
    db = make_db()

    setup_document_query(
        db=db,
        owner_id=1,
    )

    result = can_update_document(
        db=db,
        user_id=1,
        role="viewer",
        document_id=10,
    )

    assert result is False
