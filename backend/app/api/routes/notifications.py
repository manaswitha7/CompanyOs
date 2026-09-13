from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.services.notifications.service import NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


class NotificationCreate(BaseModel):
    user_id: int
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    message: str
    notification_type: str = "system"
    workspace_id: int | None = None


def serialize_notification(
    notification,
):
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "workspace_id": notification.workspace_id,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
    }


@router.post("")
def create_notification(
    request: NotificationCreate,
):
    db = SessionLocal()

    try:
        notification = (
            NotificationService.create_notification(
                db=db,
                user_id=request.user_id,
                title=request.title,
                message=request.message,
                notification_type=request.notification_type,
                workspace_id=request.workspace_id,
            )
        )

        return serialize_notification(
            notification
        )

    finally:
        db.close()


@router.get("/{user_id}")
def list_notifications(
    user_id: int,
    workspace_id: int | None = None,
):
    db = SessionLocal()

    try:
        notifications = (
            NotificationService.list_notifications(
                db=db,
                user_id=user_id,
                workspace_id=workspace_id,
            )
        )

        return [
            serialize_notification(item)
            for item in notifications
        ]

    finally:
        db.close()


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    user_id: int,
):
    db = SessionLocal()

    try:
        notification = (
            NotificationService.mark_as_read(
                db=db,
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return serialize_notification(
            notification
        )

    finally:
        db.close()


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    user_id: int,
):
    db = SessionLocal()

    try:
        deleted = (
            NotificationService.delete_notification(
                db=db,
                notification_id=notification_id,
                user_id=user_id,
            )
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Notification not found",
            )

        return {
            "message": "Notification deleted successfully",
            "notification_id": notification_id,
        }

    finally:
        db.close()
