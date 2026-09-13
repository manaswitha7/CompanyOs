from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Connector(Base):
    """
    Represents an external data-source connection.

    A connector belongs to a workspace and provides a
    standardized way of synchronizing external systems
    into Company OS.
    """

    __tablename__ = "connectors"

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

    connector_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="inactive",
        server_default="inactive",
        index=True,
    )

    # Public/non-secret connector configuration.
    config: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Do not put raw passwords/tokens here.
    # This field is reserved for an encrypted secret reference.
    credential_ref: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_sync_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    last_sync_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
