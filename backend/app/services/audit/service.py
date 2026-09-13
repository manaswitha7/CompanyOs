import json
from enum import Enum
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


# ============================================================
# AUDIT ACTIONS
# ============================================================


class AuditAction(str, Enum):
    """
    Standard audit events supported by Company OS.
    """

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"

    # --------------------------------------------------------
    # Documents
    # --------------------------------------------------------

    DOCUMENT_VIEWED = "DOCUMENT_VIEWED"
    DOCUMENT_CREATED = "DOCUMENT_CREATED"
    DOCUMENT_UPDATED = "DOCUMENT_UPDATED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"

    # --------------------------------------------------------
    # Document permissions
    # --------------------------------------------------------

    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"

    # --------------------------------------------------------
    # Workspace
    # --------------------------------------------------------

    WORKSPACE_CREATED = "WORKSPACE_CREATED"
    WORKSPACE_UPDATED = "WORKSPACE_UPDATED"

    # --------------------------------------------------------
    # Users
    # --------------------------------------------------------

    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"

    # --------------------------------------------------------
    # Chat / RAG
    # --------------------------------------------------------

    CHAT_REQUESTED = "CHAT_REQUESTED"

    # --------------------------------------------------------
    # AI / Tools
    # --------------------------------------------------------

    AI_ACTION_EXECUTED = "AI_ACTION_EXECUTED"

    # --------------------------------------------------------
    # System
    # --------------------------------------------------------

    SYSTEM_CONFIGURATION_CHANGED = (
        "SYSTEM_CONFIGURATION_CHANGED"
    )


# ============================================================
# ACTION NORMALIZATION
# ============================================================


def normalize_action(
    action: str | AuditAction,
) -> str:
    """
    Convert an audit action into a canonical string.

    AuditAction values are always preferred, but strings
    remain supported so existing API callers do not break.
    """

    if isinstance(action, AuditAction):
        return action.value

    normalized = str(action).strip().upper()

    if not normalized:
        raise ValueError(
            "Audit action cannot be empty."
        )

    return normalized


# ============================================================
# DETAILS SANITIZATION
# ============================================================


def sanitize_audit_details(
    details: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Prepare audit metadata before storing it.

    Audit logs should contain operational metadata,
    not secrets or authentication credentials.
    """

    if details is None:
        return None

    if not isinstance(details, dict):
        raise ValueError(
            "Audit details must be a dictionary."
        )

    sanitized: dict[str, Any] = {}

    sensitive_keys = {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
        "secret",
        "api_key",
        "apikey",
        "secret_key",
    }

    for key, value in details.items():

        normalized_key = str(key).strip().lower()

        if normalized_key in sensitive_keys:

            sanitized[key] = "[REDACTED]"

            continue

        sanitized[key] = value

    return sanitized


# ============================================================
# CREATE AUDIT LOG
# ============================================================


def create_audit_log(
    db: Session,
    *,
    workspace_id: int,
    user_id: int,
    action: str | AuditAction,
    resource_type: str | None = None,
    resource_id: int | str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """
    Create an audit log entry.

    Records:

        who
        where
        what
        which resource
        additional metadata

    The record is flushed immediately so callers can use
    the generated audit ID before the surrounding transaction
    is committed.
    """

    # --------------------------------------------------------
    # Validate required identifiers
    # --------------------------------------------------------

    if workspace_id is None:
        raise ValueError(
            "workspace_id is required for audit logging."
        )

    if user_id is None:
        raise ValueError(
            "user_id is required for audit logging."
        )

    # --------------------------------------------------------
    # Normalize action
    # --------------------------------------------------------

    normalized_action = normalize_action(action)

    # --------------------------------------------------------
    # Normalize resource information
    # --------------------------------------------------------

    normalized_resource_type = None

    if resource_type is not None:

        normalized_resource_type = (
            str(resource_type)
            .strip()
            .lower()
        )

        if not normalized_resource_type:
            normalized_resource_type = None

    normalized_resource_id = None

    if resource_id is not None:

        normalized_resource_id = str(
            resource_id
        )

    # --------------------------------------------------------
    # Sanitize details
    # --------------------------------------------------------

    sanitized_details = (
        sanitize_audit_details(details)
    )

    serialized_details = None

    if sanitized_details is not None:

        try:

            serialized_details = json.dumps(
                sanitized_details,
                default=str,
            )

        except (TypeError, ValueError) as exc:

            raise ValueError(
                "Audit details could not be serialized."
            ) from exc

    # --------------------------------------------------------
    # Create model
    # --------------------------------------------------------

    audit_log = AuditLog(
        workspace_id=workspace_id,
        user_id=user_id,
        action=normalized_action,
        resource_type=normalized_resource_type,
        resource_id=normalized_resource_id,
        details=serialized_details,
    )

    # --------------------------------------------------------
    # Add + flush
    # --------------------------------------------------------

    db.add(audit_log)
    db.flush()

    return audit_log
