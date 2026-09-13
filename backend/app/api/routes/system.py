from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.models.user import User
from app.models.workspace import Workspace

from app.services.queue.redis_queue import (
    check_redis_connection,
)

from app.services.storage.minio import (
    create_bucket_if_not_exists,
)

from app.models.user import User

from app.services.permissions.dependencies import (
    require_permission,
)
from app.services.permissions.roles import Permission

router = APIRouter(
    prefix="/system",
    tags=["System"],
)


# ============================================================
# BASIC SYSTEM HEALTH
# ============================================================

@router.get("/health")
def system_health(
    current_user: User = Depends(
        require_permission(
            Permission.SYSTEM_VIEW
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return health information for the main
    Company OS backend dependencies.
    """

    database_status = "healthy"

    try:
        db.execute(
            text("SELECT 1")
        )
    except Exception:
        database_status = "unhealthy"

    # Redis
    try:
        redis_status = (
            "healthy"
            if check_redis_connection()
            else "unhealthy"
        )
    except Exception:
        redis_status = "unhealthy"

    # MinIO
    minio_status = "healthy"

    try:
        create_bucket_if_not_exists()
    except Exception:
        minio_status = "unhealthy"

    overall_status = (
        "healthy"
        if (
            database_status == "healthy"
            and redis_status == "healthy"
            and minio_status == "healthy"
        )
        else "degraded"
    )

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow(),
        "services": {
            "database": database_status,
            "redis": redis_status,
            "minio": minio_status,
        },
    }


# ============================================================
# PLATFORM STATISTICS
# ============================================================

@router.get("/stats")
def system_stats(
    current_user: User = Depends(
        require_permission(
            Permission.SYSTEM_VIEW
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return high-level Company OS statistics.

    Intended for admin monitoring.
    """

    total_users = (
        db.query(func.count(User.id))
        .scalar()
        or 0
    )

    total_workspaces = (
        db.query(func.count(Workspace.id))
        .scalar()
        or 0
    )

    total_documents = (
        db.query(func.count(Document.id))
        .scalar()
        or 0
    )

    completed_documents = (
        db.query(func.count(Document.id))
        .filter(
            Document.status == "completed"
        )
        .scalar()
        or 0
    )

    processing_documents = (
        db.query(func.count(Document.id))
        .filter(
            Document.status == "processing"
        )
        .scalar()
        or 0
    )

    queued_documents = (
        db.query(func.count(Document.id))
        .filter(
            Document.status == "queued"
        )
        .scalar()
        or 0
    )

    failed_documents = (
        db.query(func.count(Document.id))
        .filter(
            Document.status == "failed"
        )
        .scalar()
        or 0
    )

    total_audit_events = (
        db.query(func.count(AuditLog.id))
        .scalar()
        or 0
    )

    return {
        "users": total_users,
        "workspaces": total_workspaces,
        "documents": {
            "total": total_documents,
            "queued": queued_documents,
            "processing": processing_documents,
            "completed": completed_documents,
            "failed": failed_documents,
        },
        "audit_events": total_audit_events,
    }


# ============================================================
# INGESTION MONITORING
# ============================================================

@router.get("/ingestion")
def ingestion_monitor(
    current_user: User = Depends(
        require_permission(
            Permission.SYSTEM_VIEW
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return document ingestion health and failures.
    """

    status_counts = (
        db.query(
            Document.status,
            func.count(Document.id),
        )
        .group_by(Document.status)
        .all()
    )

    status_summary = {
        status: count
        for status, count in status_counts
    }

    failed_documents = (
        db.query(Document)
        .filter(
            Document.status == "failed"
        )
        .order_by(
            Document.created_at.desc()
        )
        .limit(20)
        .all()
    )

    return {
        "status_counts": status_summary,
        "failed_documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "workspace_id": document.workspace_id,
                "created_at": document.created_at,
            }
            for document in failed_documents
        ],
    }


# ============================================================
# AUDIT MONITORING
# ============================================================

@router.get("/audit")
def audit_monitor(
    limit: int = 50,
    current_user: User = Depends(
        require_permission(
            Permission.AUDIT_READ
        )
    ),
    db: Session = Depends(get_db),
):
    """
    Return recent audit events for administration.
    """

    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 200",
        )

    logs = (
        db.query(AuditLog)
        .order_by(
            AuditLog.created_at.desc()
        )
        .limit(limit)
        .all()
    )

    return {
        "count": len(logs),
        "events": [
            {
                "id": log.id,
                "workspace_id": log.workspace_id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "created_at": log.created_at,
            }
            for log in logs
        ],
    }
