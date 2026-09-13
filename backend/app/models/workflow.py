from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Workflow(Base):
    """
    Defines an automation workflow in Company OS.

    A workflow follows:

        Trigger -> Conditions -> Actions

    Example:

        Trigger:
            document.created

        Condition:
            department == "HR"

        Action:
            create_task
    """

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    workspace_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Example:
    #
    # {
    #     "event": "document.created"
    # }
    #
    trigger: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Example:
    #
    # {
    #     "operator": "AND",
    #     "rules": [
    #         {
    #             "field": "department",
    #             "operator": "equals",
    #             "value": "HR"
    #         }
    #     ]
    # }
    conditions: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Example:
    #
    # [
    #     {
    #         "type": "create_task",
    #         "config": {
    #             "title": "Review document"
    #         }
    #     },
    #     {
    #         "type": "send_notification",
    #         "config": {
    #             "message": "New HR document uploaded"
    #         }
    #     }
    # ]
    actions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
