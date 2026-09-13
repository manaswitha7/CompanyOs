from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "system",
        workspace_id: int | None = None,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            workspace_id=workspace_id,
            notification_type=notification_type,
            title=title,
            message=message,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def list_notifications(
        db: Session,
        user_id: int,
        workspace_id: int | None = None,
    ) -> list[Notification]:

        query = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id
            )
        )

        if workspace_id is not None:
            query = query.filter(
                Notification.workspace_id == workspace_id
            )

        return (
            query
            .order_by(
                Notification.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:

        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            return None

        notification.is_read = True

        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: int,
        user_id: int,
    ) -> bool:

        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            return False

        db.delete(notification)
        db.commit()

        return True
